# -*- coding: utf-8 -*

import os, glob

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

from qgis.core import *

from apis_db_manager import *
from apis_thumb_viewer import *

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

    def __init__(self, iface, dbm):
        QDialog.__init__(self)
        self.iface = iface
        self.dbm = dbm
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)
        self.setupUi(self)

        #self.uiDisplayFlightPathBtn.clicked.connect(lambda: parent.openViewFlightPathDialog(self.getFilmList(), self))

        self.uiExportFootprintsBtn.clicked.connect(self.exportFootprints)
        self.uiImageThumbsBtn.clicked.connect(self.viewAsThumbs)
        self.uiLoadOrthoBtn.clicked.connect(self.loadOrthos)
        self.uiCopyImagesBtn.clicked.connect(self.copyImages)
        self.accepted.connect(self.onAccepted)

        self.uiImageListTableV.doubleClicked.connect(self.viewImage)


        self.uiFilterGrp.toggled.connect(self.applyFilter)
        self.uiFilterVerticalChk.stateChanged.connect(self.applyFilter)
        self.uiFilterObliqueChk.stateChanged.connect(self.applyFilter)
        self.uiFilterScaleEdit.setValidator(QIntValidator())
        self.uiFilterScaleEdit.textEdited.connect(self.applyFilter)
        self.uiFilterScaleOperatorCombo.currentIndexChanged.connect(self.applyFilter)
        #self.setupTable()

    def loadImageListByFilm(self, filmid, mode):
        #QMessageBox.warning(None, "FilmNumber", "{0} - {1}".format(filmid, mode))
        if mode == u"senk.":
            fromTable = 'luftbild_senk_cp'
        elif mode == u"schräg":
            fromTable = 'luftbild_schraeg_cp'
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
        qryStr = "select cp.bildnummer, cp.filmnummer, cp.massstab, f.weise, f.art_ausarbeitung as art from {0} AS cp, film AS f WHERE cp.filmnummer = '{1}' AND f.filmnummer = '{1}'".format(fromTable, filmid)
        query.exec_(qryStr)

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
            fileName = imageDir + "\\{0}\\{1}.jpg".format(rec.value("filmnummer"), rec.value("bildnummer").replace('.','_'))
            if os.path.isfile(os.path.normpath(fileName)):
                newRow.append(QStandardItem("ja"))
            else:
                newRow.append(QStandardItem("nein"))

            #ortho
            fileNames = glob.glob(orthoDir + "\\{0}\\{1}_op*.*".format(rec.value("filmnummer"), rec.value("bildnummer").replace('.','_')))
            if fileNames:
                newRow.append(QStandardItem("ja"))
            else:
                newRow.append(QStandardItem("nein"))

            #hires
            filmDirName = imageDir + "\\{0}".format(rec.value("filmnummer"))
            filmDir = QDir(filmDirName)
            hiResDirs = filmDir.entryList(["highres*", "mrsid", "raw"], QDir.Dirs)
            if len(hiResDirs) > 0:
                for hiResDirName in hiResDirs:
                    hiResDir = QDir(filmDirName + "\\" + hiResDirName)
                    hiResFiles = hiResDir.entryList([rec.value("bildnummer").replace('.','_')+"*"], QDir.Files)
                    if len(hiResFiles) > 0:
                        #QMessageBox.warning(None, "Bild", u"{0}".format(', '.join(hiResFiles)))
                        newRow.append(QStandardItem("ja"))
                    else:
                        newRow.append(QStandardItem("nein"))
            else:
                newRow.append(QStandardItem("nein"))

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

    def loadImageListBySpatialQuery(self, geometry):
        pass

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
        self.uiFilterVerticalChk.setCheckState(Qt.Checked)
        self.uiFilterObliqueChk.setCheckState(Qt.Checked)
        self.uiFilterScaleEdit.clear()
        self.uiFilterScaleOperatorCombo.setCurrentIndex(0)
        self.uiFilterFilmKindCombo.clear()
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

    def viewImage(self):
        r = self.uiImageListTableV.currentIndex().row()
        imageDir = self.settings.value("APIS/image_dir")
        fileName = imageDir + "\\{0}\\{1}.jpg".format(self.model.item(r, 1).text(), self.model.item(r, 0).text().replace('.','_'))
        if os.path.isfile(os.path.normpath(fileName)):
            if sys.platform == 'linux2':
                subprocess.call(["xdg-open", fileName])
            else:
                os.startfile(fileName)
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
        qryStr = "select filmnummer, bildnummer, weise, AsWKT(geom) as fpGeom, Area(geom) as area from luftbild_senk_fp where bildnummer in ({0}) union all select filmnummer, bildnummer, weise, AsWKT(geom) as fpGeom, Area(geom) as area from luftbild_schraeg_fp where bildnummer in ({0}) order by bildnummer".format(imageString[:-1])
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
            fields.append(QgsField("weise", QVariant.String))
            fields.append(QgsField("area", QVariant.Double))

            writer = QgsVectorFileWriter(layer, "UTF-8", fields, QGis.WKBMultiPolygon, QgsCoordinateReferenceSystem(4312, QgsCoordinateReferenceSystem.EpsgCrsId))

            for feature in self.iter_features(query):
                writer.addFeature(feature)
            del writer

            #load to canvas
            self.iface.addVectorLayer(layer, "", 'ogr')

            #open folder in file browser
            if sys.platform == 'linux2':
                subprocess.call(["xdg-open", os.path.split(layer)[0]])
            else:
                os.startfile(os.path.split(layer)[0])

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
                msgBox.setText(u'Neben Bilder mit normaler Auflösung stehen Bilder mit hoher Auflösung zur Verfügung. Welche wollen Sie kopieren?')
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
                            sourceFileName = os.path.normpath(imageDir + "\\{0}\\{1}.jpg".format(filmDirName, image.replace('.','_')))
                            destinationFileName = os.path.normpath(destinationDirName + "\\{0}\\{1}.jpg".format(filmDirName, image.replace('.','_')))
                            #MessageBox.warning(None, "Bilder kopieren", u"SourceVZ: {0}, DestVZ: {1}".format(sourceFileName, destinationFileName))
                            sourceFile = QFile(sourceFileName)
                            sourceFile.copy(destinationFileName)

                        #TODO HiRes Kopieren
                        #QMessageBox.warning(None, "Bilder kopieren", u"{0}, {1}".format(hiRes, ', '.join(hiResImageList)))
                        if hiRes and image in hiResImageList:
                            #copy hi res image files
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
                                    hiResFiles = hiResDir.entryList([image.replace('.','_')+"*"], QDir.Files)
                                    if len(hiResFiles) > 0:
                                        for hiResFile in hiResFiles:
                                            sourceHiResFileName = os.path.normpath("{0}\\{1}\\{2}".format(filmDirPathName, hiResDirName, hiResFile))
                                            destinationHiResFileName = os.path.normpath(destinationDirName + "\\{0}\\{1}\\{2}".format(filmDirName, hiResDirName, hiResFile))
                                            #QMessageBox.warning(None, "Bilder kopieren", u"SourceVZ: {0}, DestVZ: {1}".format(sourceHiResFileName, destinationHiResFileName))
                                            sourceHiResFile = QFile(sourceHiResFileName)
                                            sourceHiResFile.copy(destinationHiResFileName)
                                        #QMessageBox.warning(None, "Bild", u"{0}".format(', '.join(hiResFiles)))


                if sys.platform == 'linux2':
                    subprocess.call(["xdg-open", destinationDirName])
                else:
                    os.startfile(destinationDirName)

            else:
                QMessageBox.warning(None, "Bilder kopieren", u"Das Ziel Verzeichnis {0} konnte in {1} nicht erstellt werden".format(newDirName, selectedDirName))


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
        if self.uiFilterGrp.isChecked():
            count = 0
            for row in range(self.model.rowCount()):
                show = True
                #Weise
                if (self.uiFilterVerticalChk.checkState() == Qt.Unchecked and self.model.item(row, 3).text() == u'senk.') or (self.uiFilterObliqueChk.checkState() == Qt.Unchecked and self.model.item(row, 3).text() == u'schräg'):
                    show = False
                #Scale
                if self.uiFilterScaleEdit.text().strip() != '':
                    imageScaleNumber = float(self.model.item(row, 2).text())
                    scaleNumber = int(self.uiFilterScaleEdit.text())
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

                if show:
                    self.uiImageListTableV.showRow(row)
                    count += 1
                else:
                    self.uiImageListTableV.hideRow(row)

            self.uiImageFilterCountLbl.setText('{0}'.format(count))
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
            self.uiImageFilterCountLbl.setText('-')

            self.uiImageThumbsBtn.setEnabled(True)
            self.uiExportFootprintsBtn.setEnabled(True)
            self.uiCopyImagesBtn.setEnabled(True)
            self.uiExportListAsPdfBtn.setEnabled(True)


    def onAccepted(self):
        self.accept()