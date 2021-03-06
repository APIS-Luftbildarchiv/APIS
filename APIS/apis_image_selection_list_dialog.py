# -*- coding: utf-8 -*

import os, glob

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from PyQt4.QtXml import *

from qgis.core import *

from apis_db_manager import *
from apis_thumb_viewer import *
from apis_image_registry import *
from apis_image2exif import *
from apis_printer import *

from functools import partial

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

# --------------------------------------------------------
# Film - Eingabe, Pflege
# --------------------------------------------------------
from apis_image_selection_list_form import *
from functools import partial
import subprocess

class ApisImageSelectionListDialog(QDialog, Ui_apisImageSelectionListDialog):

    def __init__(self, iface, dbm, imageRegistry):
        QDialog.__init__(self)
        self.iface = iface
        self.dbm = dbm
        self.imageRegistry = imageRegistry
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)
        self.setupUi(self)

        #self.uiDisplayFlightPathBtn.clicked.connect(lambda: parent.openViewFlightPathDialog(self.getFilmList(), self))

        self.uiExportFootprintsBtn.clicked.connect(self.exportFootprints)
        self.uiImageThumbsBtn.clicked.connect(self.viewAsThumbs)
        self.uiLoadOrthoBtn.clicked.connect(self.loadOrthos)
        self.uiCopyImagesBtn.clicked.connect(self.copyImages)
        self.uiImage2ExifBtn.clicked.connect(self.image2Exif)
        self.uiExportListAsPdfBtn.clicked.connect(self.DEVexportListAsPdf)
        self.uiExportLabelsAsPdfBtn.clicked.connect(self.exportLabelsAsPdf)
        self.accepted.connect(self.onAccepted)

        self.uiImageListTableV.doubleClicked.connect(self.viewImage)


        self.uiFilterGrp.toggled.connect(self.applyFilter)
        self.uiFilterVerticalChk.stateChanged.connect(self.applyFilter)
        self.uiFilterObliqueChk.stateChanged.connect(self.applyFilter)
        self.uiFilterScanChk.stateChanged.connect(self.applyFilter)
        self.uiFilterHiResChk.stateChanged.connect(self.applyFilter)
        self.uiFilterOrthoChk.stateChanged.connect(self.applyFilter)
        self.uiFilterScaleEdit.setValidator(QDoubleValidator())
        self.uiFilterScaleEdit.textEdited.connect(self.applyFilter)
        self.uiFilterScaleOperatorCombo.currentIndexChanged.connect(self.applyFilter)
        self.uiFilterFilmKindChk.stateChanged.connect(self.applyFilter)
        self.uiFilterFilmKindCombo.currentIndexChanged.connect(self.applyFilter)
        self.uiFilterScanCombo.currentIndexChanged.connect(self.applyFilter)
        self.uiFilterHiResCombo.currentIndexChanged.connect(self.applyFilter)
        self.uiFilterOrthoCombo.currentIndexChanged.connect(self.applyFilter)
        #self.setupTable()

    def loadImageListByFilm(self, filmid, mode):
        #QMessageBox.warning(None, "FilmNumber", "{0} - {1}".format(filmid, mode))
        if mode == u"senk.":
            fromTable = 'luftbild_senk_cp'
            spatialIndicator = 'massstab'
        elif mode == u"schräg":
            fromTable = 'luftbild_schraeg_cp'
            spatialIndicator = 'radius'
        else:
            #FIXME Introduce Error System
            sys.exit()

        query = QSqlQuery(self.dbm.db)
        qryStr = "select count(*) from {0} WHERE filmnummer = '{1}'".format(fromTable, filmid)
        query.exec_(qryStr)
        query.first()
        rows = query.value(0)
        if rows < 1:
            QMessageBox.warning(None, "Bild Auswahl", u"Für den Film mit der Nummer {0} wurden noch keine Bilder kartiert!".format(filmid))
            return False

        query.clear()
        qryStr = "select cp.bildnummer, cp.filmnummer, cp.{2}, f.weise, f.art_ausarbeitung as art from {0} AS cp, film AS f WHERE cp.filmnummer = '{1}' AND f.filmnummer = '{1}'".format(fromTable, filmid, spatialIndicator)
        query.exec_(qryStr)

        rec = query.record()
        #QMessageBox.warning(None, "Bild", u"{0}, {1}".format(rows,rec.count()))
        self.model = QStandardItemModel()
        #set Header


        #iterate over query result
        # TODO: Introduce Image Registry
        imageDir = self.settings.value("APIS/image_dir")
        orthoDir = self.settings.value("APIS/ortho_image_dir")

        while query.next():
            newRow = []
            rec = query.record()
            for col in range(rec.count()):
                newCol = QStandardItem(unicode(rec.value(col)))
                newRow.append(newCol)

            #scan
            #TODO RM fileName = imageDir + "\\{0}\\{1}.jpg".format(IdToIdLegacy(rec.value("filmnummer")), IdToIdLegacy(rec.value("bildnummer")).replace('.','_'))
            fileName = imageDir + "\\{0}\\{1}.jpg".format(rec.value("filmnummer"), rec.value("bildnummer").replace('.','_'))
            #if os.path.isfile(os.path.normpath(fileName)):
            #    newRow.append(QStandardItem("ja"))
            #else:
            #    newRow.append(QStandardItem("nein"))
            #TODO RM imageNumber = IdToIdLegacy(rec.value("bildnummer"))
            imageNumber = rec.value("bildnummer")
            if self.imageRegistry.hasImage(imageNumber):
                newRow.append(QStandardItem("ja"))
            else:
                newRow.append(QStandardItem("nein"))

            #ortho
            #TODO RM #fileNames = glob.glob(orthoDir + "\\{0}\\{1}_op*.*".format(IdToIdLegacy(rec.value("filmnummer")), IdToIdLegacy(rec.value("bildnummer")).replace('.','_')))
            #fileNames = glob.glob(orthoDir + "\\{0}\\{1}_op*.*".format(rec.value("filmnummer"), rec.value("bildnummer").replace('.','_')))
            #if fileNames:
            if self.imageRegistry.hasOrtho(imageNumber):
                newRow.append(QStandardItem("ja"))
            else:
                newRow.append(QStandardItem("nein"))

            #hires
            if self.imageRegistry.hasHiRes(imageNumber):
                newRow.append(QStandardItem("ja"))
            else:
                newRow.append(QStandardItem("nein"))
            #TODO RM # filmDirName = imageDir + "\\{0}".format(IdToIdLegacy(rec.value("filmnummer")))
            # filmDirName = imageDir + "\\{0}".format(rec.value("filmnummer"))
            # filmDir = QDir(filmDirName)
            # hiResDirs = filmDir.entryList(["highres*", "mrsid", "raw"], QDir.Dirs)
            # if len(hiResDirs) > 0:
            #     hasHiRes = "nein"
            #     for hiResDirName in hiResDirs:
            #         hiResDir = QDir(filmDirName + "\\" + hiResDirName)
            #TODO RM          hiResFiles = hiResDir.entryList([IdToIdLegacy(rec.value("bildnummer")).replace('.','_')+"*"], QDir.Files)
            #         hiResFiles = hiResDir.entryList([rec.value("bildnummer").replace('.','_')+"*"], QDir.Files)
            #         if len(hiResFiles) > 0:
            #             #QMessageBox.warning(None, "Bild", u"{0}".format(', '.join(hiResFiles)))
            #             #newRow.append(QStandardItem("ja"))
            #             hasHiRes = "ja"
            #
            #     newRow.append(QStandardItem(hasHiRes))
            # else:
            #     newRow.append(QStandardItem("nein"))

            self.model.appendRow(newRow)

        for col in range(rec.count()):
            self.model.setHeaderData(col, Qt.Horizontal, rec.fieldName(col))

        self.model.setHeaderData(self.model.columnCount()-3, Qt.Horizontal, "scan")
        self.model.setHeaderData(self.model.columnCount()-2, Qt.Horizontal, "ortho")
        self.model.setHeaderData(self.model.columnCount()-1, Qt.Horizontal, "hires")

        #self.model = QSqlQueryModel()
        #self.model.setQuery(qryStr)
        #self.model.insertColumn(self.model.columnCount())
        #self.model.setHeaderData(self.model.columnCount()-1, Qt.Horizontal, "scan")
        #self.model.insertColumn(self.model.columnCount())
        #self.model.setHeaderData(self.model.columnCount()-1, Qt.Horizontal, "ortho")
        #self.model.data(self.model.creat)
        #rec = self.model.record(1)
        #field = rec.field("scan")
        #field.setReadOnly(False)
        #field.setValue("True")


        self.uiImageCountLbl.setText("{0}".format(self.model.rowCount()))
        self.uiScanCountLbl.setText("{0}".format(self.conditionalRowCount(5,"ja")))
        self.uiOrthoCountLbl.setText("{0}".format(self.conditionalRowCount(6,"ja")))
        self.uiHiResCountLbl.setText("{0}".format(self.conditionalRowCount(7,"ja")))

        #query.first()
        #res = query.value(0)
        self.setupTable()
        self.setupFilter()
        self.applyFilter()

        return True

    def loadImageListBySpatialQuery(self, query=None):
        #epsg = 4312
        #qryStr = "select  cp.bildnummer as bildnummer, cp.filmnummer as filmnummer, cp.radius as mst_radius, f.weise as weise, f.art_ausarbeitung as art from film as f, luftbild_schraeg_cp as cp where cp.bildnummer in (select fp.bildnummer from luftbild_schraeg_fp as fp where not IsEmpty(fp.geom) and intersects(GeomFromText('{0}',{1}),fp.geom)) and f.filmnummer = cp.filmnummer UNION ALL select  cp_s.bildnummer as bildnummer, cp_S.filmnummer as filmnummer, cp_s.massstab, f_s.weise, f_s.art_ausarbeitung from film as f_s, luftbild_senk_cp as cp_s where cp_s.bildnummer in (select fp_s.bildnummer from luftbild_senk_fp as fp_s where not IsEmpty(fp_s.geom) and intersects(GeomFromText('{0}',{1}),fp_s.geom)) and f_s.filmnummer = cp_s.filmnummer ORDER BY filmnummer, bildnummer".format(geometry, epsg)
        #t = QTime()
        #t.start()
        #query = QSqlQuery(qryStr, self.dbm.db)
        #qryStr = "select  cp.bildnummer as bildnummer, cp.filmnummer as filmnummer, cp.radius as mst_radius, f.weise as weise, f.art_ausarbeitung as art from film as f, luftbild_schraeg_cp as cp where cp.bildnummer in (select fp.bildnummer from luftbild_schraeg_fp as fp where not IsEmpty(fp.geom) and intersects(GeomFromText('{0}',{1}),fp.geom)) and f.filmnummer = cp.filmnummer UNION ALL select  cp_s.bildnummer as bildnummer, cp_S.filmnummer as filmnummer, cp_s.massstab, f_s.weise, f_s.art_ausarbeitung from film as f_s, luftbild_senk_cp as cp_s where cp_s.bildnummer in (select fp_s.bildnummer from luftbild_senk_fp as fp_s where not IsEmpty(fp_s.geom) and intersects(GeomFromText('{0}',{1}),fp_s.geom)) and f_s.filmnummer = cp_s.filmnummer ORDER BY filmnummer, bildnummer".format(geometry, epsg)

        #query.exec_(qryStr)
        #e = t.elapsed()

        #QMessageBox.warning(None, "Time", u"{0}".format(e))

        rec = query.record()

        #QMessageBox.warning(None, "Bild", u"{0}, {1}".format(rows,rec.count()))
        self.model = QStandardItemModel()
        #set Header

        #iterate over query result
        imageDir = self.settings.value("APIS/image_dir")
        orthoDir = self.settings.value("APIS/ortho_image_dir")
        while query.next():
            newRow = []
            rec = query.record()
            for col in range(rec.count()):
                newCol = QStandardItem(unicode(rec.value(col)))
                newRow.append(newCol)

            #scan
            #TODO RM imageNumber = IdToIdLegacy(rec.value("bildnummer"))
            imageNumber = rec.value("bildnummer")
            if self.imageRegistry.hasImage(imageNumber):
                newRow.append(QStandardItem("ja"))
            else:
                newRow.append(QStandardItem("nein"))

            #ortho
            if self.imageRegistry.hasOrtho(imageNumber):
                newRow.append(QStandardItem("ja"))
            else:
                newRow.append(QStandardItem("nein"))

            #hires
            if self.imageRegistry.hasHiRes(imageNumber):
                newRow.append(QStandardItem("ja"))
            else:
                newRow.append(QStandardItem("nein"))
            #scan
            #TODO RM # fileName = imageDir + "\\{0}\\{1}.jpg".format(IdToIdLegacy(rec.value("filmnummer")), IdToIdLegacy(rec.value("bildnummer")).replace('.','_'))
            # fileName = imageDir + "\\{0}\\{1}.jpg".format(rec.value("filmnummer"), rec.value("bildnummer").replace('.','_'))
            # if os.path.isfile(os.path.normpath(fileName)):
            #     newRow.append(QStandardItem("ja"))
            # else:
            #     newRow.append(QStandardItem("nein"))
            #
            # #ortho
            #TODO RM   # fileNames = glob.glob(orthoDir + "\\{0}\\{1}_op*.*".format(IdToIdLegacy(rec.value("filmnummer")), IdToIdLegacy(rec.value("bildnummer")).replace('.','_')))
            # fileNames = glob.glob(orthoDir + "\\{0}\\{1}_op*.*".format(rec.value("filmnummer"), rec.value("bildnummer").replace('.','_')))
            # if fileNames:
            #     newRow.append(QStandardItem("ja"))
            # else:
            #     newRow.append(QStandardItem("nein"))
            #
            # #hires
            #TODO RM # filmDirName = imageDir + "\\{0}".format(IdToIdLegacy(rec.value("filmnummer")))
            # filmDirName = imageDir + "\\{0}".format(rec.value("filmnummer"))
            # filmDir = QDir(filmDirName)
            # hiResDirs = filmDir.entryList(["highres*", "mrsid", "raw"], QDir.Dirs)
            # if len(hiResDirs) > 0:
            #     hasHiRes = "nein"
            #     for hiResDirName in hiResDirs:
            #         hiResDir = QDir(filmDirName + "\\" + hiResDirName)
            #TODO RM          hiResFiles = hiResDir.entryList([IdToIdLegacy(rec.value("bildnummer")).replace('.','_')+"*"], QDir.Files)
            #         hiResFiles = hiResDir.entryList([rec.value("bildnummer").replace('.','_')+"*"], QDir.Files)
            #         if len(hiResFiles) > 0:
            #             #QMessageBox.warning(None, "Bild", u"{0}".format(', '.join(hiResFiles)))
            #             #newRow.append(QStandardItem("ja"))
            #             hasHiRes = "ja"
            #         #else:
            #             #newRow.append(QStandardItem("nein"))
            #     newRow.append(QStandardItem(hasHiRes))
            # else:
            #     newRow.append(QStandardItem("nein"))

            self.model.appendRow(newRow)

        if self.model.rowCount() < 1:
            QMessageBox.warning(None, "Bild Auswahl", u"Es wurden keine kartierten Bilder gefunden!")
            return False

        for col in range(rec.count()):
            self.model.setHeaderData(col, Qt.Horizontal, rec.fieldName(col))

        self.model.setHeaderData(self.model.columnCount()-3, Qt.Horizontal, "scan")
        self.model.setHeaderData(self.model.columnCount()-2, Qt.Horizontal, "ortho")
        self.model.setHeaderData(self.model.columnCount()-1, Qt.Horizontal, "hires")

        #self.model = QSqlQueryModel()
        #self.model.setQuery(qryStr)
        #self.model.insertColumn(self.model.columnCount())
        #self.model.setHeaderData(self.model.columnCount()-1, Qt.Horizontal, "scan")
        #self.model.insertColumn(self.model.columnCount())
        #self.model.setHeaderData(self.model.columnCount()-1, Qt.Horizontal, "ortho")
        #self.model.data(self.model.creat)
        #rec = self.model.record(1)
        #field = rec.field("scan")
        #field.setReadOnly(False)
        #field.setValue("True")


        self.uiImageCountLbl.setText("{0}".format(self.model.rowCount()))
        self.uiScanCountLbl.setText("{0}".format(self.conditionalRowCount(5,"ja")))
        self.uiOrthoCountLbl.setText("{0}".format(self.conditionalRowCount(6,"ja")))
        self.uiHiResCountLbl.setText("{0}".format(self.conditionalRowCount(7,"ja")))

        #query.first()
        #res = query.value(0)
        self.setupTable()
        self.setupFilter()
        self.applyFilter()

        return True

    def conditionalRowCount(self, section, value):
        count = 0
        for row in range(self.model.rowCount()):
           if self.model.item(row, section).text() == value:
               count += 1
        return count

    def setupTable(self):
        self.uiImageListTableV.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.uiImageListTableV.setModel(self.model)
        self.uiImageListTableV.setEditTriggers(QAbstractItemView.NoEditTriggers)

        #hide and sort Columns
        #visibleColumns = ['filmnummer', 'flugdatum', 'anzahl_bilder', 'weise', 'art_ausarbeitung', 'militaernummer', 'militaernummer_alt']
        #vCIdx = []
        #for vC in visibleColumns:
            #vCIdx.append(self.model.fieldIndex(vC))

        #for c in range(self.model.columnCount()):
            #if c not in vCIdx:
                #self.uiImageListTableV.hideColumn(c)

        #hH = self.uiImageListTableV.horizontalHeader()
        #for i in range(len(vCIdx)):
           #hH.moveSection(hH.visualIndex(vCIdx[i]), i)

        self.uiImageListTableV.resizeColumnsToContents()
        self.uiImageListTableV.resizeRowsToContents()
        self.uiImageListTableV.horizontalHeader().setResizeMode(QHeaderView.Stretch)
       # self.uiImageListTableV.show()

        self.uiImageListTableV.selectionModel().selectionChanged.connect(self.onSelectionChanged)


        # signals

        #
    def setupFilter(self):
        self.uiFilterGrp.setChecked(False)
        self.uiFilterFilmKindChk.setCheckState(Qt.Unchecked)
        self.uiFilterVerticalChk.setCheckState(Qt.Checked)
        self.uiFilterObliqueChk.setCheckState(Qt.Checked)
        self.uiFilterScaleEdit.clear()
        self.uiFilterScaleOperatorCombo.setCurrentIndex(0)
        self.uiFilterFilmKindCombo.clear()

        self.uiFilterScanChk.setCheckState(Qt.Unchecked)
        self.uiFilterHiResChk.setCheckState(Qt.Unchecked)
        self.uiFilterOrthoChk.setCheckState(Qt.Unchecked)
        self.uiFilterScanCombo.setCurrentIndex(0)
        self.uiFilterHiResCombo.setCurrentIndex(0)
        self.uiFilterOrthoCombo.setCurrentIndex(0)
        #
        filmKinds = []
        for row in range(self.model.rowCount()):
            filmKinds.append(self.model.item(row, 4).text())

        for filmKind in set(filmKinds):
            self.uiFilterFilmKindCombo.addItem(filmKind)
        self.uiFilterFilmKindCombo.setCurrentIndex(0)


    def getImageList(self, getAll=False, filterSection=None, filterValue=None):
        imageList = []
        if self.uiImageListTableV.selectionModel().hasSelection() and not getAll:
            rows = self.uiImageListTableV.selectionModel().selectedRows()
            for row in rows:
                #get imagenummer
                if not self.uiImageListTableV.isRowHidden(row.row()):
                    if filterSection and filterValue:
                        if self.model.item(row.row(), filterSection).text() == filterValue:
                            imageList.append(self.model.item(row.row(), 0).text())
                    else:
                        imageList.append(self.model.item(row.row(), 0).text())
                    #imageList.append(self.model.record(row.row()).value("bildnummer"))#(self.model.createIndex(row.row(), self.model.fieldIndex("filmnummer"))))
        else:
            for row in range(self.model.rowCount()):
                if not self.uiImageListTableV.isRowHidden(row):
                    if filterSection and filterValue:
                        if self.model.item(row, filterSection).text() == filterValue:
                            imageList.append(self.model.item(row, 0).text())
                    else:
                        imageList.append(self.model.item(row, 0).text())
                   #imageList.append(self.model.record(row).value("bildnummer"))#(self.model.createIndex(row, self.model.fieldIndex("filmnummer"))))

        return imageList

    def getImageListWithRows(self, getAll=False, filterSection=None, filterValue=None):
        imageList = []
        if self.uiImageListTableV.selectionModel().hasSelection() and not getAll:
            rows = self.uiImageListTableV.selectionModel().selectedRows()
            for row in rows:
                #get imagenummer
                if not self.uiImageListTableV.isRowHidden(row.row()):
                    rowContent = []
                    if filterSection and filterValue:
                        if self.model.item(row.row(), filterSection).text() == filterValue:
                            for col in range(self.model.columnCount()):
                                rowContent.append(self.model.item(row.row(), col).text())
                            imageList.append(rowContent)
                    else:
                        for col in range(self.model.columnCount()):
                            rowContent.append(self.model.item(row.row(), col).text())
                        imageList.append(rowContent)
        else:
            for row in range(self.model.rowCount()):
                if not self.uiImageListTableV.isRowHidden(row):
                    rowContent = []
                    if filterSection and filterValue:
                        if self.model.item(row, filterSection).text() == filterValue:
                            for col in range(self.model.columnCount()):
                                rowContent.append(self.model.item(row, col).text())
                            imageList.append(rowContent)
                    else:
                        for col in range(self.model.columnCount()):
                            rowContent.append(self.model.item(row, col).text())
                        imageList.append(rowContent)
        return imageList

    def viewImage(self):
        r = self.uiImageListTableV.currentIndex().row()
        imageDir = self.settings.value("APIS/image_dir")
        #TODO RM fileName = imageDir + "\\{0}\\{1}.jpg".format(IdToIdLegacy(self.model.item(r, 1).text()), IdToIdLegacy(self.model.item(r, 0).text()).replace('.','_'))
        fileName = imageDir + "\\{0}\\{1}.jpg".format(self.model.item(r, 1).text(), self.model.item(r, 0).text().replace('.','_'))
        if os.path.isfile(os.path.normpath(fileName)):
            OpenFileOrFolder(fileName)
        else:
            QMessageBox.warning(None, "Bild", u"Bild unter {0} nicht vorhanden".format(fileName))
        #get Path to Image
        #open with standard

        # QMessageBox.warning(None, "FilmNumber", "Double")
        #filmIdx = self.model.createIndex(self.uiFilmListTableV.currentIndex().row(), self.model.fieldIndex("filmnummer"))
        #self.filmNumberToLoad = self.model.data(filmIdx)
        #self.accept()
        #QMessageBox.warning(None, "FilmNumber", unicode(self.model.data(filmIdx)))

    def viewAsThumbs(self):
        if self.uiImageListTableV.selectionModel().hasSelection():
            #Abfrage Footprints der selektierten Bilder Exportieren oder alle
            msgBox = QMessageBox()
            msgBox.setWindowTitle(u'Vorschau der Bilder')
            msgBox.setText(u'Wollen Sie die Vorschau der ausgewählten Bilder oder der gesamten Liste öffnen?')
            msgBox.addButton(QPushButton(u'Auswahl'), QMessageBox.YesRole)
            msgBox.addButton(QPushButton(u'Gesamte Liste'), QMessageBox.NoRole)
            msgBox.addButton(QPushButton(u'Abbrechen'), QMessageBox.RejectRole)
            ret = msgBox.exec_()

            if ret == 0:
                imageList = self.getImageList(False, 5, "ja")
            elif ret == 1:
                imageList = self.getImageList(True, 5, "ja")
            else:
                return
        else:
            imageList = self.getImageList(True, 5, "ja")

        if len(imageList) == 0:
            QMessageBox.warning(None, "Bildvorschau", u"Es sind keine Bilder vorhanden!")
            return

        #imageString = ""
        #for image in imageList:
        #    imageString += "'" + image + "',"
        # use: imageString[:-1]
        #QMessageBox.warning(None, "BildNumber", "{0}".format(imageString))

        imagePathList = []
        imageList.sort()
        imageDir = self.settings.value("APIS/image_dir")

        for image in imageList:
            #TODO RM imagePathList.append(os.path.normpath(imageDir + "\\{0}\\{1}.jpg".format(IdToIdLegacy(image.split('.')[0]), IdToIdLegacy(image).replace('.','_'))))
            imagePathList.append(os.path.normpath(imageDir + "\\{0}\\{1}.jpg".format(image.split('.')[0], image.replace('.','_'))))

        #QMessageBox.warning(None, "BildNumber", "{0}".format(', '.join(imagePathList)))
        #app = QtGui.QApplication([])
        widget = QdContactSheet()
        widget.load(imagePathList)
        widget.setWindowTitle("Apis Thumb Viewer")
        widget.setModal(True)
        widget.resize(1000, 600)
        widget.show()
        if widget.exec_():
            pass
        #app.exec_()

    def loadOrthos(self):
        orthoList = self.getImageList(False, 6, "ja")

        orthoPathList = []
        orthoList.sort()
        orthoDir = self.settings.value("APIS/ortho_image_dir")

        for ortho in orthoList:
            #TODO RM rthoFileNames = glob.glob(os.path.normpath(orthoDir + "\\{0}\\{1}_op*.*".format(IdToIdLegacy(ortho.split('.')[0]), IdToIdLegacy(ortho).replace('.','_'))))
            orthoFileNames = glob.glob(os.path.normpath(orthoDir + "\\{0}\\{1}_op*.*".format(ortho.split('.')[0], ortho.replace('.','_'))))
            for orthoFile in orthoFileNames:
                if os.path.splitext(orthoFile)[1] in ['.sid', '.tif', '.tiff', '.jpg']:
                    fileInfo = QFileInfo(orthoFile)
                    baseName = fileInfo.baseName()
                    rlayer = QgsRasterLayer(orthoFile, baseName)
                    if not rlayer.isValid():
                        QMessageBox.warning(None, "Ortho", "{0}".format(os.path.splitext(orthoFile)[1]))
                    else:
                        QgsMapLayerRegistry.instance().addMapLayer(rlayer)
                    #QMessageBox.warning(None, "Ortho", "{0}".format(os.path.splitext(orthoFile)[1]))
                #if os.path.basename(orthoFile)
                #orthoPathList.append()


    def exportFootprints(self):
        if self.uiImageListTableV.selectionModel().hasSelection():
            #Abfrage Footprints der selektierten Bilder Exportieren oder alle
            msgBox = QMessageBox()
            msgBox.setWindowTitle(u'Footprints Exportieren')
            msgBox.setText(u'Wollen Sie die Footprints der ausgewählten Bilder oder der gesamten Liste exportieren?')
            msgBox.addButton(QPushButton(u'Auswahl'), QMessageBox.YesRole)
            msgBox.addButton(QPushButton(u'Gesamte Liste'), QMessageBox.NoRole)
            msgBox.addButton(QPushButton(u'Abbrechen'), QMessageBox.RejectRole)
            ret = msgBox.exec_()

            if ret == 0:
                imageList = self.getImageList(False)
            elif ret == 1:
                imageList = self.getImageList(True)
            else:
                return
        else:
            imageList = self.getImageList(True)

        imageString = ""
        for image in imageList:
            imageString += "'" + image + "',"
        # use: imageString[:-1]
        #QMessageBox.warning(None, "BildNumber", "{0}".format(imageString))

        query = QSqlQuery(self.dbm.db)
        qryStr = "select filmnummer, bildnummer, AsWKT(geometry) as fpGeom, Area(geometry) as area from luftbild_senk_fp where bildnummer in ({0}) union all select filmnummer, bildnummer, AsWKT(geometry) as fpGeom, Area(geometry) as area from luftbild_schraeg_fp where bildnummer in ({0}) order by bildnummer".format(imageString[:-1])
        query.exec_(qryStr)


        # Save Dialog
        now = QDateTime.currentDateTime()
        saveDir = self.settings.value("APIS/working_dir", QDir.home().dirName())
        layer = QFileDialog.getSaveFileName(self, 'Footprint Export Speichern', saveDir + "\\" + 'Footprints_{0}'.format(now.toString("yyyyMMdd_hhmmss")), '*.shp')
        if layer:
            #layer = "C:\\apis\\export_footprints.shp"
            check = QFile(layer)
            if check.exists():
                if not QgsVectorFileWriter.deleteShapeFile(layer):
                    QMessageBox.warning(None, "Footprint Export", u"Es ist nicht möglich die SHP Datei {0} zu überschreiben!".format(layer))
                    return
                    #raise Exception

            #fields
            fields = QgsFields()
            fields.append(QgsField("bildnummer", QVariant.String))
            fields.append(QgsField("filmnummer", QVariant.String))
            fields.append(QgsField("area", QVariant.Double))

            writer = QgsVectorFileWriter(layer, "UTF-8", fields, QGis.WKBPolygon, QgsCoordinateReferenceSystem(4312, QgsCoordinateReferenceSystem.EpsgCrsId))

            for feature in self.iter_features(query):
                writer.addFeature(feature)
            del writer

            #load to canvas
            self.iface.addVectorLayer(layer, "", 'ogr')

            #open folder in file browser
            OpenFileOrFolder(os.path.split(layer)[0])

            #vlayer = QgsVectorLayer("multipolygon?crs=EPSG:4326", "export_footprints", "memory")
            # vlayer.setCrs(self.pointLayer.crs())
            #provider = vlayer.dataProvider()
            #vlayer use crs of pointLayer

            #fields = QgsFields()
            #fields.append(QgsField("area", QVariant.Double))
            #vlayer.addAttribute(QgsField("area", QVariant.Double))


            #vlayer.updateFields()

            #for feature in self.iter_features():
                #provider.addFeatures([feature])

            #while query.next():
                #rec = query.record()
                #feature = QgsFeature()
                #feature.setFields(fields)
                #feature.setGeometry(QgsGeometry.fromWkt(rec.value(rec.indexOf("mp"))))
                #feature.setAttribute("area",rec.value(rec.indexOf("area")))
               # vlayer.addFeature(feature)
                #geom.fromPolygon()
                #QMessageBox.warning(None, "BildNumber", "{0}".format(geom.exportToWkt()))

            #vlayer.updateExtents()
            #QgsMapLayerRegistry.instance().addMapLayer(vlayer)

    def iter_features(self, query):
        """Iterate over the features of the input layer.

        Yields pairs of the form (QgsPoint, attributeMap).
        Each time a vertice is read hook is called.

        """

        while query.next():
            rec = query.record()
            attributes = [rec.value(rec.indexOf("bildnummer")), rec.value(rec.indexOf("filmnummer")), unicode(rec.value(rec.indexOf("weise"))), rec.value(rec.indexOf("area"))]
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromWkt(rec.value(rec.indexOf("fpGeom"))))
            feature.setAttributes(attributes)
            yield feature

    def copyImages(self):
        if self.uiImageListTableV.selectionModel().hasSelection():
            #Abfrage Footprints der selektierten Bilder Exportieren oder alle
            msgBox = QMessageBox()
            msgBox.setWindowTitle(u'Bilder Kopieren')
            msgBox.setText(u'Wollen Sie die ausgewählten Bilder oder die gesamte Liste kopieren?')
            msgBox.addButton(QPushButton(u'Auswahl'), QMessageBox.YesRole)
            msgBox.addButton(QPushButton(u'Gesamte Liste'), QMessageBox.NoRole)
            msgBox.addButton(QPushButton(u'Abbrechen'), QMessageBox.RejectRole)
            ret = msgBox.exec_()

            if ret == 0:
                imageList = self.getImageList(False, 5, "ja")
                hiResImageList = self.getImageList(False, 7, "ja")
            elif ret == 1:
                imageList = self.getImageList(True, 5, "ja")
                hiResImageList = self.getImageList(True, 7, "ja")
            else:
                return
        else:
            imageList = self.getImageList(True, 5, "ja")
            hiResImageList = self.getImageList(True, 7, "ja")

        if len(imageList) == 0:
            QMessageBox.warning(None, "Bilder kopieren", u"Es sind keine Bilder vorhanden!")
            return

        selectedDirName = QFileDialog.getExistingDirectory(
             None,
             u"Ziel Ordner auswählen",
             self.settings.value("APIS/working_dir", QDir.home().dirName())
        )


        if selectedDirName:
            loRes = True
            hiRes = False
            if len(hiResImageList) > 0:
                #ask if normal, hires, oder beides?
                msgBox = QMessageBox()
                msgBox.setWindowTitle(u'Bilder Kopieren')
                msgBox.setText(u'Neben Bildern mit normaler Auflösung stehen Bilder mit hoher Auflösung zur Verfügung. Welche wollen Sie kopieren?')
                msgBox.addButton(QPushButton(u'Normale Auflösung'), QMessageBox.ActionRole)
                msgBox.addButton(QPushButton(u'Hohe Auflösung'), QMessageBox.ActionRole)
                msgBox.addButton(QPushButton(u'Alle Auflösungen'), QMessageBox.ActionRole)
                msgBox.addButton(QPushButton(u'Abbrechen'), QMessageBox.RejectRole)
                ret = msgBox.exec_()

                if ret == 0:
                    loRes = True
                    hiRes = False
                elif ret == 1:
                    loRes = False
                    hiRes = True
                elif ret == 2:
                    loRes = True
                    hiRes = True
                else:
                    return

            destinationDir = QDir(selectedDirName)
            now = QDateTime.currentDateTime()
            newDirName = "apis_bild_export_{0}".format(now.toString("yyyyMMdd_hhmmss"))
            if destinationDir.mkdir(newDirName):
                destinationDirName = selectedDirName + '\\' + newDirName
                destinationDir = QDir(destinationDirName)
                #QMessageBox.warning(None, "Bilder kopieren", u"ZielVZ: {0}".format(destinationDirName))
                imageDir = self.settings.value("APIS/image_dir")
                for image in imageList:
                    if loRes or hiRes:
                        filmDirName = image.split('.')[0]
                        if not destinationDir.exists(filmDirName):
                            destinationDir.mkdir(filmDirName)

                        if loRes:
                            #TODO RM sourceFileName = os.path.normpath(imageDir + "\\{0}\\{1}.jpg".format(IdToIdLegacy(filmDirName), IdToIdLegacy(image).replace('.','_')))
                            sourceFileName = os.path.normpath(imageDir + "\\{0}\\{1}.jpg".format(filmDirName, image.replace('.','_')))
                            destinationFileName = os.path.normpath(destinationDirName + "\\{0}\\{1}.jpg".format(filmDirName, image.replace('.','_')))
                            #MessageBox.warning(None, "Bilder kopieren", u"SourceVZ: {0}, DestVZ: {1}".format(sourceFileName, destinationFileName))
                            sourceFile = QFile(sourceFileName)
                            sourceFile.copy(destinationFileName)

                        #HiRes Kopieren
                        #QMessageBox.warning(None, "Bilder kopieren", u"{0}, {1}".format(hiRes, ', '.join(hiResImageList)))
                        if hiRes and image in hiResImageList:
                            #copy hi res image files
                            #TODO RM filmDirPathName = imageDir + "\\" + IdToIdLegacy(filmDirName)
                            filmDirPathName = imageDir + "\\" + filmDirName
                            filmDir = QDir(filmDirPathName)
                            hiResDirs = filmDir.entryList(["highres*", "mrsid", "raw"], QDir.Dirs)
                            if len(hiResDirs) > 0:
                                for hiResDirName in hiResDirs:
                                    filmDestDirName = destinationDirName + "\\" + filmDirName
                                    filmDestDir = QDir(filmDestDirName)
                                    if not filmDestDir.exists(hiResDirName):
                                        filmDestDir.mkdir(hiResDirName)
                                    hiResDir = QDir(filmDirPathName + "\\" + hiResDirName)
                                    #TODO RM hiResFiles = hiResDir.entryList([IdToIdLegacy(image).replace('.','_')+"*"], QDir.Files)
                                    hiResFiles = hiResDir.entryList([image.replace('.','_')+"*"], QDir.Files)
                                    if len(hiResFiles) > 0:
                                        for hiResFile in hiResFiles:
                                            sourceHiResFileName = os.path.normpath("{0}\\{1}\\{2}".format(filmDirPathName, hiResDirName, hiResFile))
                                            destinationHiResFileName = os.path.normpath(destinationDirName + "\\{0}\\{1}\\{2}".format(filmDirName, hiResDirName, hiResFile))
                                            #QMessageBox.warning(None, "Bilder kopieren", u"SourceVZ: {0}, DestVZ: {1}".format(sourceHiResFileName, destinationHiResFileName))
                                            sourceHiResFile = QFile(sourceHiResFileName)
                                            sourceHiResFile.copy(destinationHiResFileName)
                                        #QMessageBox.warning(None, "Bild", u"{0}".format(', '.join(hiResFiles)))

                OpenFileOrFolder(destinationDirName)

            else:
                QMessageBox.warning(None, "Bilder kopieren", u"Das Ziel Verzeichnis {0} konnte in {1} nicht erstellt werden".format(newDirName, selectedDirName))

    def image2Exif(self):

        if self.uiImageListTableV.selectionModel().hasSelection():
            #Abfrage Footprints der selektierten Bilder Exportieren oder alle
            msgBox = QMessageBox()
            msgBox.setWindowTitle(u'Schreibe EXIF/IPTC')
            msgBox.setText(u'Wollen Sie die Metadaten der ausgewählten Bilder oder der gesamten Liste exportieren?')
            msgBox.addButton(QPushButton(u'Auswahl'), QMessageBox.YesRole)
            msgBox.addButton(QPushButton(u'Gesamte Liste'), QMessageBox.NoRole)
            msgBox.addButton(QPushButton(u'Abbrechen'), QMessageBox.RejectRole)
            ret = msgBox.exec_()

            if ret == 0:
                imageList = self.getImageList(False)
            elif ret == 1:
                imageList = self.getImageList(True)
            else:
                return
        else:
            imageList = self.getImageList(True)

        imageString = "'" + "','".join(imageList) + "'"

        query = QSqlQuery(self.dbm.db)
        qryStr = u"SELECT * FROM (SELECT bildnummer, hoehe, longitude, latitude,  (SELECT group_concat(fundortnummer, ';' ) FROM fundort, luftbild_senk_fp WHERE luftbild_senk_fp.bildnummer = lb.bildnummer AND Intersects(fundort.geometry, luftbild_senk_fp.geometry) AND fundort.rowid IN (SELECT rowid FROM spatialindex WHERE f_table_name='fundort' AND search_frame=luftbild_senk_fp.geometry) ORDER BY fundortnummer_nn) AS fundorte, NULL AS keyword, NULL AS description, lb.projekt, lb.copyright, land, militaernummer, militaernummer_alt, archiv, kamera, kalibrierungsnummer, kammerkonstante, fokus, fotograf, flugdatum, flugzeug FROM luftbild_senk_cp AS lb, film AS f WHERE lb.filmnummer = f.filmnummer AND lb.bildnummer IN ({0}) UNION ALL SELECT bildnummer, hoehe, longitude, latitude, (SELECT group_concat(fundortnummer, ';' ) FROM fundort, luftbild_schraeg_fp WHERE luftbild_schraeg_fp.bildnummer = lb.bildnummer AND Intersects(fundort.geometry, luftbild_schraeg_fp.geometry) AND fundort.rowid IN (SELECT rowid FROM spatialindex WHERE f_table_name='fundort' AND search_frame=luftbild_schraeg_fp.geometry) ORDER BY fundortnummer_nn) as fundorte, keyword, description, lb.projekt, lb.copyright, land, militaernummer, militaernummer_alt, archiv, kamera, kalibrierungsnummer, kammerkonstante, fokus, fotograf, flugdatum, flugzeug FROM luftbild_schraeg_cp AS lb, film AS f WHERE lb.filmnummer = f.filmnummer AND lb.bildnummer IN ({0})) ORDER BY bildnummer".format(imageString)
        query.prepare(qryStr)
        query.exec_()

        imageDir = self.settings.value("APIS/image_dir")

        query.seek(-1)
        count = 0
        while query.next():
            count += 1

        progressDlg = QProgressDialog("XMP Metadaten werden geschrieben...", "Abbrechen", 0, count, self)
        progressDlg.setWindowModality(Qt.WindowModal)
        progressDlg.show()
        query.seek(-1)
        i = 0
        while query.next():
            progressDlg.setValue(i)
            if progressDlg.wasCanceled():
                break

            rec = query.record()
            metadataDict = {}
            for i in range(rec.count()):
                val = u"{0}".format(rec.value(i))
                if val.replace(" ", "") == '' or val == 'NULL':
                    val = u"---"
                metadataDict["APIS_" + rec.fieldName(i)] = val

            #TODO RM if self.imageRegistry.hasImage(IdToIdLegacy(metadataDict["APIS_bildnummer"])):
            if self.imageRegistry.hasImage(metadataDict["APIS_bildnummer"]):
                #TODO RM imagePath = imageDir + "\\" + IdToIdLegacy(metadataDict["APIS_bildnummer"][:10]) + "\\" + IdToIdLegacy(metadataDict["APIS_bildnummer"]).replace('.','_') + ".jpg"
                imagePath = imageDir + "\\" + metadataDict["APIS_bildnummer"][:10] + "\\" + metadataDict["APIS_bildnummer"].replace('.','_') + ".jpg"
                if os.path.isfile(imagePath):
                    pass
                    # QMessageBox.information(None, "Image", u"{0}".format(imagePath))
                    Image2Exif(metadataDict, imagePath)
                else:
                    QMessageBox.information(None, "Image", u"Die Bilddatei für {0} wurde nicht gefunden (FileSystem: {1}).".format(metadataDict["APIS_bildnummer"], imagePath))
            else:
                QMessageBox.information(None, "Image", u"Die Bilddatei für {0} wurde nicht gefunden (ImageRegistry).".format(metadataDict["APIS_bildnummer"]))
            #imagePath = self.settings.value("APIS/image_dir") + "\\02140301\\02140301_003.jpg"
        progressDlg.setValue(count)

    def DEVexportListAsPdf(self):
        if self.uiImageListTableV.selectionModel().hasSelection():
            #Abfrage Footprints der selektierten Bilder Exportieren oder alle
            msgBox = QMessageBox()
            msgBox.setWindowTitle(u'Bildliste als PDF speichern')
            msgBox.setText(u'Wollen Sie die ausgewählten Bilder oder die gesamte Liste als PDF speichern?')
            msgBox.addButton(QPushButton(u'Auswahl'), QMessageBox.YesRole)
            msgBox.addButton(QPushButton(u'Gesamte Liste'), QMessageBox.NoRole)
            msgBox.addButton(QPushButton(u'Abbrechen'), QMessageBox.RejectRole)
            ret = msgBox.exec_()

            if ret == 0:
                imageList = self.getImageList(False)
                scanCount = len(self.getImageList(False,5,"ja"))
                hiResCount = len(self.getImageList(False,7,"ja"))
                orthoCount = len(self.getImageList(False,6,"ja"))
            elif ret == 1:
                imageList = self.getImageList(True)
                scanCount = len(self.getImageList(True,5,"ja"))
                hiResCount = len(self.getImageList(True,7,"ja"))
                orthoCount = len(self.getImageList(True,6,"ja"))
            else:
                return
        else:
            imageList = self.getImageList(True)
            scanCount = len(self.getImageList(True,5,"ja"))
            hiResCount = len(self.getImageList(True,7,"ja"))
            orthoCount = len(self.getImageList(True,6,"ja"))

        #qryStr = u"SELECT filmnummer AS Filmnummer, strftime('%d.%m.%Y', flugdatum) AS Flugdatum, anzahl_bilder AS Bildanzahl, weise AS Weise, art_ausarbeitung AS Art, militaernummer AS Militärnummer, militaernummer_alt AS 'Militärnummer Alt', CASE WHEN weise = 'senk.' THEN (SELECT count(*) from luftbild_senk_cp WHERE film.filmnummer = luftbild_senk_cp.filmnummer) ELSE (SELECT count(*) from luftbild_schraeg_cp WHERE film.filmnummer = luftbild_schraeg_cp.filmnummer) END AS Kartiert, 0 AS Gescannt FROM film WHERE filmnummer IN ({0}) ORDER BY filmnummer".format(u",".join(u"'{0}'".format(image) for image in imageList))
        qryStr = u"SELECT bildnummer AS Bildnummer, weise AS Weise, radius AS 'Radius/Maßstab', art_ausarbeitung AS Art, 'nein' AS Gescannt, 'nein' AS Ortho, 'nein' AS HiRes FROM luftbild_schraeg_cp oI, film f WHERE oI.filmnummer = f.filmnummer AND bildnummer IN ({0}) UNION ALL SELECT bildnummer AS Bildnummer, weise AS Weise, CAST(massstab AS INT) AS 'Radius/Maßstab', art_ausarbeitung AS Art, 'nein' AS Gescannt, 'nein' AS Ortho, 'nein' AS HiRes FROM luftbild_senk_cp vI, film f WHERE vI.filmnummer = f.filmnummer AND bildnummer IN ({0}) ORDER BY bildnummer".format(u",".join(u"'{0}'".format(image) for image in imageList))
        printer = ApisListPrinter(self, self.dbm, self.imageRegistry, True, False, None, 0)
        printer.setupInfo(u"Bildliste", u"Bildliste speichern", u"Bildliste", 14)
        printer.setQuery(qryStr)
        printer.printList(u"Gescannt", u"Ortho", u"HiRes")

    def exportListAsPdf(self):

        if self.uiImageListTableV.selectionModel().hasSelection():
            #Abfrage Footprints der selektierten Bilder Exportieren oder alle
            msgBox = QMessageBox()
            msgBox.setWindowTitle(u'Bildliste als PDF speichern')
            msgBox.setText(u'Wollen Sie die ausgewählten Bilder oder die gesamte Liste als PDF speichern?')
            msgBox.addButton(QPushButton(u'Auswahl'), QMessageBox.YesRole)
            msgBox.addButton(QPushButton(u'Gesamte Liste'), QMessageBox.NoRole)
            msgBox.addButton(QPushButton(u'Abbrechen'), QMessageBox.RejectRole)
            ret = msgBox.exec_()

            if ret == 0:
                imageList = self.getImageListWithRows(False)
                scanCount = len(self.getImageList(False,5,"ja"))
                hiResCount = len(self.getImageList(False,7,"ja"))
                orthoCount = len(self.getImageList(False,6,"ja"))
            elif ret == 1:
                imageList = self.getImageListWithRows(True)
                scanCount = len(self.getImageList(True,5,"ja"))
                hiResCount = len(self.getImageList(True,7,"ja"))
                orthoCount = len(self.getImageList(True,6,"ja"))
            else:
                return
        else:
            imageList = self.getImageListWithRows(True)
            scanCount = len(self.getImageList(True,5,"ja"))
            hiResCount = len(self.getImageList(True,7,"ja"))
            orthoCount = len(self.getImageList(True,6,"ja"))


        #fileName = 'C:\\apis\\temp\\BildListe.pdf'
        saveDir = self.settings.value("APIS/working_dir", QDir.home().dirName())
        fileName = QFileDialog.getSaveFileName(self, 'Bildliste Speichern', saveDir + "\\" + 'Bildliste_{0}'.format(QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")), '*.pdf')



        if fileName:

            ms = QgsMapSettings()
            comp = QgsComposition(ms)
            comp.setPlotStyle(QgsComposition.Print)
            comp.setPrintResolution(300)
            comp.setPaperSize(210.0, 297.0)

            #header
            hHight = 15
            fHight = 15
            margin = 15
            mTab = 5
            hWidth = comp.paperWidth()/2-margin
            fWidth = (comp.paperWidth()-(2*margin))/3

            page = 1
            prevPage = 0
            imageCount = 0
            imageCountTotal = 0
            pageBreak = 40
            for imageRow in imageList:
                imageCountTotal += 1
                imageCount += 1
                if imageCount > pageBreak:
                    imageCount = 1
                    page += 1
                if page > prevPage:
                    prevPage = page
                    #Header Left - Title
                    hLeft = QgsComposerLabel(comp)
                    hLeft.setItemPosition(margin, margin, hWidth , hHight, QgsComposerItem.UpperLeft, False, page)
                    hLeft.setBackgroundEnabled(True)
                    hLeft.setBackgroundColor(QColor("#CCCCCC"))
                    hLeft.setText(u"Bildliste")
                    hLeft.setVAlign(Qt.AlignVCenter)
                    hLeft.setMarginX(5)
                    hLeft.setFont(QFont("Arial", 16, 100))
                    comp.addItem(hLeft)
                    #Header Right - Stats
                    hRight = QgsComposerLabel(comp)
                    hRight.setItemPosition(comp.paperWidth()/2, margin, hWidth , hHight, QgsComposerItem.UpperLeft, False, page)
                    hRight.setBackgroundEnabled(True)
                    hRight.setBackgroundColor(QColor("#CCCCCC"))
                    hRight.setText(u"Anzahl:\t{0}\nScan:\t\t\t{1}\nHiRes:\t\t\t{2}\nOrtho:\t{3}".format(len(imageList), scanCount, hiResCount, orthoCount))
                    hRight.setVAlign(Qt.AlignVCenter)
                    hRight.setHAlign(Qt.AlignRight)
                    hRight.setMarginX(5)
                    hRight.setFont(QFont("Arial", 8))
                    comp.addItem(hRight)
                    #Footer Left - Institute
                    fLeft = QgsComposerLabel(comp)
                    fLeft.setItemPosition(margin, comp.paperHeight()-margin, fWidth, fHight, QgsComposerItem.LowerLeft, False, page)
                    fLeft.setBackgroundEnabled(True)
                    fLeft.setBackgroundColor(QColor("#CCCCCC"))
                    #FIXME get From Settings!
                    fLeft.setText(u"Luftbildarchiv,\nInstitut für Urgeschichte und Historische Archäologie,\nUniversität Wien")
                    fLeft.setVAlign(Qt.AlignVCenter)
                    fLeft.setMarginX(5)
                    fLeft.setFont(QFont("Arial", 8))
                    comp.addItem(fLeft)
                    #Footer Center - Date
                    fCenter = QgsComposerLabel(comp)
                    fCenter.setItemPosition(margin+fWidth, comp.paperHeight()-margin, fWidth, fHight, QgsComposerItem.LowerLeft, False, page)
                    fCenter.setBackgroundEnabled(True)
                    fCenter.setBackgroundColor(QColor("#CCCCCC"))
                    fCenter.setText(u"{0}".format(QDateTime.currentDateTime().toString("dd.MM.yyyy")))
                    fCenter.setVAlign(Qt.AlignVCenter)
                    fCenter.setHAlign(Qt.AlignHCenter)
                    fCenter.setMarginX(5)
                    fCenter.setFont(QFont("Arial", 8))
                    comp.addItem(fCenter)
                    #Footer Right - PageNumber
                    fRight = QgsComposerLabel(comp)
                    fRight.setItemPosition(margin+(2*fWidth), comp.paperHeight()-margin, fWidth, fHight, QgsComposerItem.LowerLeft, False, page)
                    fRight.setBackgroundEnabled(True)
                    fRight.setBackgroundColor(QColor("#CCCCCC"))
                    fRight.setText(u"Seite {0}".format(page))
                    fRight.setVAlign(Qt.AlignVCenter)
                    fRight.setHAlign(Qt.AlignRight)
                    fRight.setMarginX(5)
                    fRight.setFont(QFont("Arial", 8))
                    comp.addItem(fRight)

                    imageTab = QgsComposerTextTable(comp)
                    imageTab.setShowGrid(True)
                    imageTab.setGridStrokeWidth(0.2)
                    imageTab.setLineTextDistance(1.2)
                    imageTab.setHeaderFont(QFont("Arial",9,100))
                    #imageTab.setHeaderHAlignment(QgsComposerTable.HeaderCenter)
                    hLabels = [u"#", "Bildnummer", "Filmnummer", u"Mst./\nRad.", "Weise", "Art", "Scan", "Ortho", "HiRes"]
                    hLabelsAdjust = []
                    for l in hLabels:
                        hLabelsAdjust.append(l.ljust(12))
                    # colProps = QgsComposerTableColumn()
                    # props = QDomElement()
                    # props.setAttribute("hAlignment", 4)
                    # props.setAttribute("vAlignment", 128)
                    # props.setAttribute("heading", "Nummer")
                    # props.setAttribute("attribute", "" )
                    # props.setAttribute("sortByRank", 0 )
                    # props.setAttribute("sortOrder", 0 )
                    # props.setAttribute("width", "100.0" )
                    # colProps.readXML(props)
                    # imageTab.setColumns([colProps])

                    imageTab.setHeaderLabels(hLabelsAdjust)
                    imageTab.setItemPosition(margin+mTab,margin+hHight+mTab, QgsComposerItem.UpperLeft, page)
                    comp.addItem(imageTab)

                #imageTab.addRow([str(imageCountTotal).zfill(len(str(len(imageList))))])
                imageTab.addRow([str(imageCountTotal).zfill(len(str(len(imageList))))] + imageRow)

                # if imageCount == pageBreak or imageCount == len(imageList):
                #     w = imageTab.rect().width()
                #     QMessageBox.warning(None, "Bild", u"{0}".format(w))
                #     hLabels = [u"ABC", "Bildnummer", "Filmnummer", u"Maßstab", "Weise", "Art","Scan","HiRes","Ortho"]
                #     imageTab.setHeaderLabels(hLabels)

            comp.setNumPages(page)

            #header.setItemPosition(0,0,comp.paperWidth(), 20, QgsComposerItem.UpperLeft, False, 1)

            #footer
            # footer = QgsComposerItemGroup(comp)
            # left = QgsComposerLabel(comp)
            # left.setText(u"Luftbildarchiv - Institut für Urgeschichte und Historische Archäologie, Universität Wien")
            # footer.addItem(left)
            # footer.setBackgroundEnabled(True)
            # footer.setBackgroundColor(QColor('#ab23c9'))
            # footer.setItemPosition(0,comp.paperHeight(), comp.paperWidth(), 100, QgsComposerItem.LowerLeft,  False, 1)


            #comp.moveItemToTop(header)
            #comp.addItem(footer)
            #comp.moveItemToBottom(footer)

            comp.exportAsPDF(fileName)

            try:
                OpenFileOrFolder(fileName)
            except Exception, e:
                pass


    def exportLabelsAsPdf(self):

        if self.uiImageListTableV.selectionModel().hasSelection():
            #Abfrage Footprints der selektierten Bilder Exportieren oder alle
            msgBox = QMessageBox()
            msgBox.setWindowTitle(u'Etiketten als PDF speichern')
            msgBox.setText(u'Wollen Sie für die ausgewählten Bilder oder für die gesamte Liste Etiketten als PDF speichern?')
            msgBox.addButton(QPushButton(u'Auswahl'), QMessageBox.YesRole)
            msgBox.addButton(QPushButton(u'Gesamte Liste'), QMessageBox.NoRole)
            msgBox.addButton(QPushButton(u'Abbrechen'), QMessageBox.RejectRole)
            ret = msgBox.exec_()

            if ret == 0:
                imageListOblique = self.getImageList(False, 3, u"schräg")
                imageListVertical = self.getImageList(False, 3, u"senk.")
            elif ret == 1:
                imageListOblique = self.getImageList(True, 3, u"schräg")
                imageListVertical = self.getImageList(True, 3, u"senk.")
            else:
                return
        else:
            imageListOblique = self.getImageList(True, 3, u"schräg")
            imageListVertical = self.getImageList(True, 3, u"senk.")

        query = QSqlQuery(self.dbm.db)

        if len(imageListOblique) > 0:
            title = u"Uni Wien - IUHA - Luftbildarchiv"
            qryStrOblique = u"SELECT luftbild_schraeg_fp.bildnummer AS bildnummer, '[' || fundortnummer || '][' || katastralgemeindenummer  || ' ' || katastralgemeinde || ']' AS fundort_kg FROM fundort, luftbild_schraeg_fp WHERE luftbild_schraeg_fp.bildnummer IN ({0}) AND Intersects(fundort.geometry, luftbild_schraeg_fp.geometry)AND fundort.rowid IN (SELECT rowid FROM spatialindex WHERE f_table_name='fundort' AND search_frame=luftbild_schraeg_fp.geometry) ORDER BY luftbild_schraeg_fp.bildnummer, katastralgemeindenummer, fundortnummer_nn".format(u",".join(u"'{0}'".format(image) for image in imageListOblique))
            query.prepare(qryStrOblique)
            query.exec_()
            labelsData = []

            for imageNumber in imageListOblique:
                labelData = {
                    'title': [title],
                    'bildnummer': [imageNumber],
                    'fundort_kg': []
                }
                query.seek(-1)
                while query.next():
                    rec = query.record()
                    if rec.value("bildnummer") == imageNumber:
                        labelData['fundort_kg'].append(rec.value("fundort_kg"))

                labelsData.append(labelData)

            pageSettings = {}
            labelSettings = {'width': 42.0, 'height': 10.0}
            labelItemOrder = ['title', 'bildnummer', 'fundort_kg']
            labelLayout = {
                'title': {'width': 1.0, 'height': 1.0/3.0, 'font': QFont("Arial", 5), 'halign': Qt.AlignCenter, 'valign': Qt.AlignVCenter},
                'bildnummer': {'width': 1.0, 'height': 1.0/3.0, 'font': QFont("Arial", 6, QFont.Bold), 'halign': Qt.AlignCenter, 'valign': Qt.AlignVCenter},
                'fundort_kg': {'width': 1.0, 'height': 1.0/3.0, 'font': QFont("Arial", 5), 'halign': Qt.AlignCenter, 'valign': Qt.AlignVCenter},
            }


            labelPrinterOblique = ApisLabelPrinter(self, u"Schräg", pageSettings, labelSettings, labelLayout, labelItemOrder, labelsData)

        if len(imageListVertical) > 0:
            title = u"Uni Wien - IUHA - Luftbildarchiv"
            qryStrOblique = u"SELECT luftbild_senk_fp.bildnummer AS bildnummer, film.kamera, luftbild_senk_cp.fokus, luftbild_senk_cp.hoehe, luftbild_senk_cp.massstab, film.militaernummer AS mil_num, film.flugdatum, '[' || fundortnummer || '][' || katastralgemeindenummer  || ' ' || katastralgemeinde || ']' AS fundort_kg FROM film, fundort, luftbild_senk_cp, luftbild_senk_fp WHERE luftbild_senk_fp.filmnummer = film.filmnummer AND luftbild_senk_cp.bildnummer = luftbild_senk_fp.bildnummer AND luftbild_senk_fp.bildnummer IN ({0}) AND Intersects(fundort.geometry, luftbild_senk_fp.geometry)AND fundort.rowid IN (SELECT rowid FROM spatialindex WHERE f_table_name='fundort' AND search_frame=luftbild_senk_fp.geometry) ORDER BY luftbild_senk_fp.bildnummer, katastralgemeindenummer, fundortnummer_nn".format(u",".join(u"'{0}'".format(image) for image in imageListVertical))
            query.prepare(qryStrOblique)
            query.exec_()
            labelsData = []
            query.seek(-1)
            count = 0
            while query.next():
                count += 1

            #Keine FOs
            if count == 0:
                qryStrOblique = u"SELECT luftbild_senk_cp.bildnummer AS bildnummer, film.kamera, luftbild_senk_cp.fokus, luftbild_senk_cp.hoehe, luftbild_senk_cp.massstab, film.militaernummer AS mil_num, film.flugdatum FROM film, luftbild_senk_cp WHERE luftbild_senk_cp.filmnummer = film.filmnummer AND luftbild_senk_cp.bildnummer IN ({0}) ORDER BY luftbild_senk_cp.bildnummer".format(u",".join(u"'{0}'".format(image) for image in imageListVertical))
                query.prepare(qryStrOblique)
                query.exec_()

            for imageNumber in imageListVertical:
                labelData = {
                    'title': [title],
                    'bildnummer': [imageNumber],
                    'mil_nummer': [],
                    'flugdatum': [],
                    'kamera': [],
                    'fokus': [],
                    'massstab': [],
                    'hoehe': [],
                    'fundort_kg': []
                }

                query.seek(-1)
                while query.next():
                    rec = query.record()
                    if rec.value("bildnummer") == imageNumber:
                        if len(labelData['mil_nummer']) < 1:
                            if rec.isNull("mil_nummer"):
                                labelData['mil_nummer'].append(u"Mil#: -")
                            else:
                                labelData['mil_nummer'].append(u"Mil#: {0}".format(rec.value("mil_num")))

                        if len(labelData['flugdatum']) < 1:
                            if rec.isNull("flugdatum"):
                                labelData['flugdatum'].append(u"kein Flugdatum")
                            else:
                                labelData['flugdatum'].append(u"Flug vom {0}".format(datetime.datetime.strptime(rec.value("flugdatum"), '%Y-%m-%d').strftime('%d.%m.%Y')))

                        if len(labelData['kamera']) < 1:
                            if rec.isNull("kamera"):
                                labelData['kamera'].append(u"Kamera: -")
                            else:
                                labelData['kamera'].append(u"Kamera: {0}".format(rec.value("kamera")))

                        if len(labelData['fokus']) < 1:
                            if rec.isNull("fokus"):
                                labelData['fokus'].append(u"Fokus: -")
                            else:
                                labelData['fokus'].append(u"Fokus: {0:.2f}".format(float(rec.value("fokus"))))

                        if len(labelData['massstab']) < 1:
                            if rec.isNull("massstab"):
                                labelData['massstab'].append(u"Mst. -")
                            else:
                                labelData['massstab'].append(u"Mst. 1:{0}".format(int(rec.value("massstab"))))

                        if len(labelData['hoehe']) < 1:
                            if rec.isNull("hoehe"):
                                labelData['hoehe'].append(u"Höhe: -")
                            else:
                                labelData['hoehe'].append(u"Höhe: {0}m".format(rec.value("hoehe")))

                        if count > 0:
                            if rec.isNull("fundort_kg"):
                                labelData['fundort_kg'].append(u"---")
                            else:
                                labelData['fundort_kg'].append(rec.value("fundort_kg"))

                labelsData.append(labelData)

            pageSettings = {}
            labelSettings = {'width': 70.0, 'height': 35.0}
            labelItemOrder = ['title', 'bildnummer', 'mil_nummer', 'flugdatum', 'kamera','fokus', 'massstab', 'hoehe', 'fundort_kg']
            labelLayout = {
                'title': {'width': 1.0, 'height': 1.0 / 6.0, 'font': QFont("Arial", 5), 'halign': Qt.AlignCenter, 'valign': Qt.AlignVCenter},
                'bildnummer': {'width': 1.0, 'height': 1.0 / 6.0, 'font': QFont("Arial", 6, QFont.Bold), 'halign': Qt.AlignCenter, 'valign': Qt.AlignVCenter},
                'mil_nummer': {'width': 1.0 / 2.0, 'height': 1.0 / 6.0, 'font': QFont("Arial", 5), 'halign': Qt.AlignCenter, 'valign': Qt.AlignVCenter},
                'flugdatum': {'width': 1.0 / 2.0, 'height': 1.0 / 6.0, 'font': QFont("Arial", 5), 'halign': Qt.AlignCenter, 'valign': Qt.AlignVCenter},
                'kamera': {'width': 1.0 / 2.0, 'height': 1.0 / 6.0, 'font': QFont("Arial", 5), 'halign': Qt.AlignCenter, 'valign': Qt.AlignVCenter},
                'fokus': {'width': 1.0 / 2.0, 'height': 1.0 / 6.0, 'font': QFont("Arial", 5), 'halign': Qt.AlignCenter, 'valign': Qt.AlignVCenter},
                'massstab': {'width': 1.0 / 2.0, 'height': 1.0 / 6.0, 'font': QFont("Arial", 5), 'halign': Qt.AlignCenter, 'valign': Qt.AlignVCenter},
                'hoehe': {'width': 1.0 / 2.0, 'height': 1.0 / 6.0, 'font': QFont("Arial", 5), 'halign': Qt.AlignCenter, 'valign': Qt.AlignVCenter},
                'fundort_kg': {'width': 1.0, 'height': 1.0 / 6.0, 'font': QFont("Arial", 5), 'halign': Qt.AlignCenter, 'valign': Qt.AlignVCenter},
            }

            labelPrinterVertical = ApisLabelPrinter(self, u"Senkrecht", pageSettings, labelSettings, labelLayout, labelItemOrder, labelsData)


    def onSelectionChanged(self, current, previous):
        # Filter ortho = ja
        if self.uiImageListTableV.selectionModel().hasSelection() and len(self.getImageList(False, 6, "ja")) > 0:
            self.uiLoadOrthoBtn.setEnabled(True)
        else:
            self.uiLoadOrthoBtn.setEnabled(False)
        #if self.uiImageListTableV.selectionModel().hasSelection() and len(self.uiImageListTableV.selectionModel().selectedRows()) == 1:
        #    self.uiLoadOrthoBtn.setEnabled(True)
        #else:
        #    self.uiLoadOrthoBtn.setEnabled(False)
        #QMessageBox.warning(None, "FilmNumber", "selection Changed")

    def applyFilter(self):
        self.uiImageListTableV.selectionModel().clear()
        if self.uiFilterGrp.isChecked():
            count = 0
            for row in range(self.model.rowCount()):
                show = True
                #Weise
                if (self.uiFilterVerticalChk.checkState() == Qt.Unchecked and self.model.item(row, 3).text() == u'senk.') or (self.uiFilterObliqueChk.checkState() == Qt.Unchecked and self.model.item(row, 3).text() == u'schräg'):
                    show = False
                #Images
                if show and ((self.uiFilterScanChk.checkState() == Qt.Checked and self.model.item(row,5).text() != self.uiFilterScanCombo.currentText()) or (self.uiFilterOrthoChk.checkState() == Qt.Checked and self.model.item(row,6).text() != self.uiFilterOrthoCombo.currentText()) or (self.uiFilterHiResChk.checkState() == Qt.Checked and self.model.item(row,7).text() != self.uiFilterHiResCombo.currentText())):
                    show = False
                #Scale
                if show and self.uiFilterScaleEdit.text().strip() != '':
                    imageScaleNumber = float(self.model.item(row, 2).text())
                    scaleNumber = float(self.uiFilterScaleEdit.text().replace(',', '.'))
                    operator = self.uiFilterScaleOperatorCombo.currentText()
                    if operator == '=':
                        if imageScaleNumber != scaleNumber:
                            show = False
                    elif operator == '>=':
                        if imageScaleNumber < scaleNumber:
                            show = False
                    elif operator == '<=':
                        if imageScaleNumber > scaleNumber:
                            show = False
                #filmart
                if show and self.uiFilterFilmKindChk.checkState() == Qt.Checked and self.uiFilterFilmKindCombo.currentText() != self.model.item(row,4).text():
                    show = False

                if show:
                    self.uiImageListTableV.showRow(row)
                    count += 1
                else:
                    self.uiImageListTableV.hideRow(row)

            self.uiImageFilterCountLbl.setText('({0})'.format(count))
            self.uiScanFilterCountLbl.setText('({0})'.format(len(self.getImageList(True,5,"ja"))))
            self.uiHiResFilterCountLbl.setText('({0})'.format(len(self.getImageList(True,7,"ja"))))
            self.uiOrthoFilterCountLbl.setText('({0})'.format(len(self.getImageList(True,6,"ja"))))

            self.onSelectionChanged(None, None)
            if count == 0:
                #self.uiLoadOrthoBtn.setEnabled(False)
                self.uiImageThumbsBtn.setEnabled(False)
                self.uiExportFootprintsBtn.setEnabled(False)
                self.uiCopyImagesBtn.setEnabled(False)
                self.uiExportListAsPdfBtn.setEnabled(False)
            else:
                #if self.uiImageListTableV.selectionModel().hasSelection() and len(self.uiImageListTableV.selectionModel().selectedRows()) == 1:
                #    self.uiLoadOrthoBtn.setEnabled(True)
                self.uiImageThumbsBtn.setEnabled(True)
                self.uiExportFootprintsBtn.setEnabled(True)
                self.uiCopyImagesBtn.setEnabled(True)
                self.uiExportListAsPdfBtn.setEnabled(True)
        else:
            # show all rows
            for row in range(self.model.rowCount()):
                self.uiImageListTableV.showRow(row)
            self.uiImageFilterCountLbl.setText('(-)')
            self.uiScanFilterCountLbl.setText('(-)')
            self.uiHiResFilterCountLbl.setText('(-)')
            self.uiOrthoFilterCountLbl.setText('(-)')

            self.uiImageThumbsBtn.setEnabled(True)
            self.uiExportFootprintsBtn.setEnabled(True)
            self.uiCopyImagesBtn.setEnabled(True)
            self.uiExportListAsPdfBtn.setEnabled(True)

            self.uiFilterScanChk.setChecked(False)
            self.uiFilterHiResChk.setChecked(False)
            self.uiFilterOrthoChk.setChecked(False)



    def onAccepted(self):
        self.accept()