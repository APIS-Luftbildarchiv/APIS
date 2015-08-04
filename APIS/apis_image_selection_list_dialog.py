# -*- coding: utf-8 -*

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

from qgis.core import *

from apis_db_manager import *

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
        self.setupUi(self)

        #self.uiDisplayFlightPathBtn.clicked.connect(lambda: parent.openViewFlightPathDialog(self.getFilmList(), self))

        self.uiExportFootprintsBtn.clicked.connect(self.exportFootprints)
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

        #query = QSqlQuery(self.dbm.db)
        qryStr = "select cp.BILD, cp.FILM, cp.MASS, f.weise, f.art_ausarbeitung from '{0}' AS cp, film AS f WHERE cp.FILM = '{1}' AND f.filmnummer = '{1}'".format(fromTable, filmid)
        #query.exec_(qryStr)

        self.model = QSqlQueryModel()
        self.model.setQuery(qryStr)
        self.uiImageCountLbl.setText("{0}".format(self.model.rowCount()))

        #query.first()
        #res = query.value(0)
        self.setupTable()
        self.setupFilter()
        self.applyFilter()

    def loadImageListBySpatialQuery(self, geometry):
        pass

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
            filmKinds.append(self.model.record(row).value("art_ausarbeitung"))

        for filmKind in set(filmKinds):
            self.uiFilterFilmKindCombo.addItem(filmKind)
        self.uiFilterFilmKindCombo.setCurrentIndex(0)


    def getImageList(self, getAll=False):
        imageList = []
        if self.uiImageListTableV.selectionModel().hasSelection() and not getAll:
            rows = self.uiImageListTableV.selectionModel().selectedRows()
            for row in rows:
                #get imagenummer
                if not self.uiImageListTableV.isRowHidden(row.row()):
                    imageList.append(self.model.record(row.row()).value("BILD"))#(self.model.createIndex(row.row(), self.model.fieldIndex("filmnummer"))))
        else:
            for row in range(self.model.rowCount()):
                if not self.uiImageListTableV.isRowHidden(row):
                    imageList.append(self.model.record(row).value("BILD"))#(self.model.createIndex(row, self.model.fieldIndex("filmnummer"))))

        return imageList

    def viewImage(self):
        rec = self.model.record(self.uiImageListTableV.currentIndex().row())
        s = QSettings()
        imageDir = s.value("APIS/image_dir")
        fileName = imageDir + "\\{0}\\{1}.jpg".format(rec.value("FILM"), rec.value("BILD").replace('.','_'))
        if os.path.isfile(fileName):
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

        #for image in imageList:
            #QMessageBox.warning(None, "BildNumber", "{0}".format(image))

        query = QSqlQuery(self.dbm.db)
        qryStr = "select FILM, BILD, WEISE, AsWKT(geom) as mp, Area(geom) as area from luftbild_senk_fp where BILD in ('01910704.010','01910704.011','01910704.012','01670401.110','01670401.111','01670401.112') union all select FILM, BILD, WEISE, AsWKT(geom) as mp, Area(geom) as area from luftbild_schraeg_fp where BILD in ('01910704.010','01910704.011','01910704.012','01670401.110','01670401.111','01670401.112') order by bild"
        query.exec_(qryStr)

        layer = "C:\\apis\\export_footprints.shp"
        check = QFile(layer)
        if check.exists():
            if not QgsVectorFileWriter.deleteShapeFile(layer):
                msg = 'Unable to delete existing shapefile "{}"'
                raise Exception

        #fields
        fields = QgsFields()
        fields.append(QgsField("bild", QVariant.String))
        fields.append(QgsField("film", QVariant.String))
        fields.append(QgsField("weise", QVariant.String))
        fields.append(QgsField("area", QVariant.Double))

        writer = QgsVectorFileWriter(layer, "UTF-8", fields, QGis.WKBMultiPolygon, QgsCoordinateReferenceSystem(4312, QgsCoordinateReferenceSystem.EpsgCrsId))

        for feature in self.iter_features(query):
            writer.addFeature(feature)
        del writer

        self.iface.addVectorLayer(layer, "export footprints", 'ogr')

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
            attributes = [rec.value(rec.indexOf("BILD")), rec.value(rec.indexOf("FILM")), unicode(rec.value(rec.indexOf("WEISE"))), rec.value(rec.indexOf("area"))]
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromWkt(rec.value(rec.indexOf("mp"))))
            feature.setAttributes(attributes)
            yield feature

    def onSelectionChanged(self, current, previous):
        if self.uiImageListTableV.selectionModel().hasSelection() and len(self.uiImageListTableV.selectionModel().selectedRows()) == 1:
            self.uiImageDetailsBtn.setEnabled(True)
        else:
            self.uiImageDetailsBtn.setEnabled(False)
        #QMessageBox.warning(None, "FilmNumber", "selection Changed")

    def applyFilter(self):
        if self.uiFilterGrp.isChecked():
            count = 0
            for row in range(self.model.rowCount()):
                show = True
                #Weise
                if (self.uiFilterVerticalChk.checkState() == Qt.Unchecked and self.model.record(row).value("weise") == u'senk.') or (self.uiFilterObliqueChk.checkState() == Qt.Unchecked and self.model.record(row).value("weise") == u'schräg'):
                    show = False
                #Scale
                if self.uiFilterScaleEdit.text().strip() != '':
                    imageScaleNumber = int(self.model.record(row).value("MASS"))
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
            if count == 0:
                self.uiImageDetailsBtn.setEnabled(False)
                self.uiImageThumbsBtn.setEnabled(False)
                self.uiExportFootprintsBtn.setEnabled(False)
                self.uiCopyImagesBtn.setEnabled(False)
                self.uiExportListAsPdfBtn.setEnabled(False)
            else:
                if self.uiImageListTableV.selectionModel().hasSelection() and len(self.uiImageListTableV.selectionModel().selectedRows()) == 1:
                    self.uiImageDetailsBtn.setEnabled(True)
                self.uiImageThumbsBtn.setEnabled(True)
                self.uiExportFootprintsBtn.setEnabled(True)
                self.uiCopyImagesBtn.setEnabled(True)
                self.uiExportListAsPdfBtn.setEnabled(True)
        else:
            # show all rows
            for row in range(self.model.rowCount()):
                self.uiImageListTableV.showRow(row)
            self.uiImageFilterCountLbl.setText('-')


    def onAccepted(self):
        self.accept()