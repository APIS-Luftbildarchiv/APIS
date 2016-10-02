# -*- coding: utf-8 -*

import os, glob

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from PyQt4.QtXml import *

from qgis.core import *

from apis_db_manager import *
from apis_findspot_dialog import *
from functools import partial

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

# --------------------------------------------------------
# Film - Eingabe, Pflege
# --------------------------------------------------------
from apis_findspot_selection_list_form import *
from functools import partial
import subprocess

class ApisFindSpotSelectionListDialog(QDialog, Ui_apisFindSpotSelectionListDialog):
    def __init__(self, iface, dbm, imageRegistry, apisLayer):
        QDialog.__init__(self)
        self.iface = iface
        self.dbm = dbm
        self.imageRegistry = imageRegistry
        self.apisLayer = apisLayer
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)
        self.setupUi(self)

        self.query = None

        self.uiFindSpotListTableV.doubleClicked.connect(self.openFindSpotDialog)

        self.uiViewFindSpotsBtn.clicked.connect(self.loadFindSpotInQgis)
        self.uiExportFindSpotsAsShpBtn.clicked.connect(self.exportFindSpotAsShp)
        self.uiExportFindSpotAsPdfBtn.clicked.connect(self.exportFindSpotAsPdf)
        self.uiExportListAsPdfBtn.clicked.connect(self.exportListAsPdf)

        self.findSpotDlg = None

    def hideEvent(self,event):
        self.query = None

    def loadFindSpotListBySpatialQuery(self, query=None, info=None, update=False):
        if self.query == None:
            self.query = query
        self.model = QStandardItemModel()
        self.query.seek(-1)
        while self.query.next():
            newRow = []
            rec = self.query.record()
            for col in range(rec.count()):
                if rec.value(col) == None:
                    value = ''
                else:
                    value = rec.value(col)
                newCol = QStandardItem(unicode(value))
                newRow.append(newCol)

            self.model.appendRow(newRow)

        if self.model.rowCount() < 1:
            if not update:
                QMessageBox.warning(None, "Fundstellen Auswahl", u"Es wurden keine Fundstellen gefunden!")
            self.query = None
            self.done(1)
            return False

        for col in range(rec.count()):
            self.model.setHeaderData(col, Qt.Horizontal, rec.fieldName(col))

        self.setupTable()

        self.uiFindSpotCountLbl.setText(unicode(self.model.rowCount()))
        if info != None:
            self.uiInfoLbl.setText(info)

        return True

    def setupTable(self):
        self.uiFindSpotListTableV.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.uiFindSpotListTableV.setModel(self.model)
        self.uiFindSpotListTableV.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.uiFindSpotListTableV.resizeColumnsToContents()
        self.uiFindSpotListTableV.resizeRowsToContents()
        self.uiFindSpotListTableV.horizontalHeader().setResizeMode(QHeaderView.Stretch)


    def openFindSpotDialog(self, idx):
        findSpotNumber = self.model.item(idx.row(), 1).text()
        siteNumber = self.model.item(idx.row(), 0).text()
        if self.findSpotDlg == None:
            self.findSpotDlg = ApisFindSpotDialog(self.iface, self.dbm, self.imageRegistry, self.apisLayer, self)
            self.findSpotDlg.findSpotEditsSaved.connect(self.reloadTable)
            self.findSpotDlg.findSpotDeleted.connect(self.reloadTable)
        self.findSpotDlg.openInViewMode(siteNumber, findSpotNumber)
        self.findSpotDlg.show()
        # Run the dialog event loop

        if self.findSpotDlg.exec_():
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
        self.findSpotDlg.uiDatingTimeCombo.currentIndexChanged.disconnect(self.findSpotDlg.loadPeriodContent)
        self.findSpotDlg.uiDatingPeriodCombo.currentIndexChanged.disconnect(self.findSpotDlg.loadPeriodDetailsContent)
        #QMessageBox.warning(None, self.tr(u"Load Site"), self.tr(u"For Site: {0}".format(siteNumber)))

    def reloadTable(self, editsSaved):
        self.query.exec_()
        self.loadFindSpotListBySpatialQuery(self.query, None, True)
        #QMessageBox.warning(None, self.tr(u"Load Site"), self.tr(u"Reload Table Now"))


    def loadFindSpotInQgis(self):
        findSpotList = self.askForFindSpotList()
        if findSpotList:
            # QMessageBox.warning(None, self.tr(u"SiteList"), u"{0}".format(u", ".join(siteList)))
            polygon, point = self.askForGeometryType()
            if polygon or point:
                # QMessageBox.warning(None, self.tr(u"SiteList"), u"{0}, {1}".format(polygon, point))

                # get PolygonLayer
                subsetString = u'"fundortnummer"  || \'.\' || "fundstellenummer" IN ('
                for findSpotNumber in findSpotList:
                    subsetString += u'\'{0}\','.format(findSpotNumber)
                subsetString = subsetString[:-1]
                subsetString += u')'
                findSpotLayer = self.getSpatialiteLayer('fundstelle', subsetString)

                if polygon:
                    # load PolygonLayer
                    self.loadLayer(findSpotLayer)

                if point:
                    # generate PointLayer
                    centerPointLayer = self.generateCenterPointLayer(findSpotLayer)
                    # load PointLayer
                    self.loadLayer(centerPointLayer)

                self.close()


    def exportFindSpotAsShp(self):
        findSpotList = self.askForFindSpotList()
        if findSpotList:
            # QMessageBox.warning(None, self.tr(u"SiteList"), u"{0}".format(u", ".join(siteList)))
            polygon, point = self.askForGeometryType()
            if polygon or point:
                # QMessageBox.warning(None, self.tr(u"SiteList"), u"{0}, {1}".format(polygon, point))

                # get PolygonLayer
                subsetString = u'"fundortnummer"  || \'.\' || "fundstellenummer" IN ('
                for findSpotNumber in findSpotList:
                    subsetString += u'\'{0}\','.format(findSpotNumber)
                subsetString = subsetString[:-1]
                subsetString += u')'
                findSpotLayer = self.getSpatialiteLayer('fundstelle', subsetString)

                now = QDateTime.currentDateTime()
                time = now.toString("yyyyMMdd_hhmmss")
                if polygon:
                    # save PolygonLayer
                    self.exportLayer(findSpotLayer, time)

                if point:
                    # generate PointLayer
                    centerPointLayer = self.generateCenterPointLayer(findSpotLayer)
                    # save PointLayer
                    self.exportLayer(centerPointLayer, time)


    def exportFindSpotAsPdf(self):
        findSpotList = self.askForFindSpotList()
        if findSpotList:
            saveDir = self.settings.value("APIS/working_dir", QDir.home().dirName())
            timeStamp = QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")

            if len(findSpotList) == 1:
                saveDialogTitle = u"Fundstelle"
                targetFileNameTemplate = u"Fundstelle_{0}_{1}".format(findSpotList[0], timeStamp)
            else:
                saveDialogTitle = u"Fundstellen Sammlung"
                targetFileNameTemplate = u"Fundstellen_Sammlung_{0}".format(timeStamp)

            targetFileName = QFileDialog.getSaveFileName(self, saveDialogTitle, os.path.join(saveDir, targetFileNameTemplate), "*.pdf")

            if targetFileName:
                fsDetailsPrinter = ApisFindSpotPrinter(self, self.dbm, self.imageRegistry)

                if len(findSpotList) == 1:

                    # print file
                    pdfFiles = fsDetailsPrinter.exportDetailsPdf(findSpotList, targetFileName, timeStamp)

                    # open file, open location?
                    for key in pdfFiles:
                        for pdfFile in pdfFiles[key]:
                            OpenFileOrFolder(pdfFile)

                else:
                    targetDirName = os.path.join(os.path.dirname(os.path.abspath(targetFileName)), u"temp_apis_print")
                    try:
                        os.makedirs(targetDirName)
                    except OSError:
                        if not os.path.isdir(targetDirName):
                            raise

                    # print files (temp)
                    pdfFiles = fsDetailsPrinter.exportDetailsPdf(findSpotList, targetDirName, timeStamp)

                    # merge to collection
                    pdfFilesList = []
                    for key in pdfFiles:
                        for pdfFile in pdfFiles[key]:
                            pdfFilesList.append(pdfFile)

                    MergePdfFiles(targetFileName, pdfFilesList)

                    # open file, open location?
                    OpenFileOrFolder(targetFileName)


    def exportListAsPdf(self):
        findSpotList = self.askForFindSpotList()
        if findSpotList:
            qryStr = u"SELECT fs.fundortnummer || '.' || fs.fundstellenummer AS Fundstellenummer, fo.katastralgemeindenummer AS 'KG Nummer', fo.katastralgemeinde AS 'KG Name', datierung_zeit || ',' || datierung_periode || ',' || datierung_periode_detail || ',' || phase_von || '-' || phase_bis AS Datierung, fundart AS Fundart FROM fundstelle fs, fundort fo WHERE fs.fundortnummer = fo.fundortnummer AND fs.fundortnummer || '.' || fs.fundstellenummer IN ({0}) ORDER BY fo.land, fo.katastralgemeindenummer, fo.fundortnummer_nn, fs.fundstellenummer".format(u",".join(u"'{0}'".format(findSpot) for findSpot in findSpotList))
            printer = ApisListPrinter(self, self.dbm, self.imageRegistry, True, False, None, 1)
            printer.setupInfo(u"Fundstellenliste", u"Fundstellenliste speichern", u"Fundstellenliste", 22)
            printer.setQuery(qryStr)
            printer.printList()


    def askForFindSpotList(self):
        if self.uiFindSpotListTableV.selectionModel().hasSelection():
            # Abfrage ob Fundorte der selektierten Bilder Exportieren oder alle
            msgBox = QMessageBox()
            msgBox.setWindowTitle(u'Fundstellen')
            msgBox.setText(u'Wollen Sie die ausgewählten Funstellen oder die gesamte Liste verwenden?')
            msgBox.addButton(QPushButton(u'Auswahl'), QMessageBox.YesRole)
            msgBox.addButton(QPushButton(u'Gesamte Liste'), QMessageBox.NoRole)
            msgBox.addButton(QPushButton(u'Abbrechen'), QMessageBox.RejectRole)
            ret = msgBox.exec_()

            if ret == 0:
                findSpotList = self.getFindSpotList(False)
            elif ret == 1:
                findSpotList = self.getFindSpotList(True)
            else:
                return None
        else:
            findSpotList = self.getFindSpotList(True)

        return findSpotList


    def getFindSpotList(self, getAll):
        findSpotList = []
        if self.uiFindSpotListTableV.selectionModel().hasSelection() and not getAll:
            rows = self.uiFindSpotListTableV.selectionModel().selectedRows()
            for row in rows:
                if not self.uiFindSpotListTableV.isRowHidden(row.row()):
                    findSpotList.append(u"{0}.{1}".format(self.model.item(row.row(), 0).text(), self.model.item(row.row(), 1).text()))
        else:
            for row in range(self.model.rowCount()):
                if not self.uiFindSpotListTableV.isRowHidden(row):
                    findSpotList.append(u"{0}.{1}".format(self.model.item(row, 0).text(), self.model.item(row, 1).text()))

        return findSpotList


    def askForGeometryType(self):
        # Abfrage ob Fundstellen der selektierten Bilder Exportieren oder alle
        msgBox = QMessageBox()
        msgBox.setWindowTitle(u'Fundstellen')
        msgBox.setText(u'Wollen Sie für die Fundstellen Polygone, Punkte oder beide Layer verwenden?')
        msgBox.addButton(QPushButton(u'Polygone'), QMessageBox.ActionRole)
        msgBox.addButton(QPushButton(u'Punkte'), QMessageBox.ActionRole)
        msgBox.addButton(QPushButton(u'Polygone und Punkte'), QMessageBox.ActionRole)
        msgBox.addButton(QPushButton(u'Abbrechen'), QMessageBox.RejectRole)
        ret = msgBox.exec_()

        if ret == 0:
            polygon = True
            point = False
        elif ret == 1:
            polygon = False
            point = True
        elif ret == 2:
            polygon = True
            point = True
        else:
            return None, None

        return polygon, point


    def getSpatialiteLayer(self, layerName, subsetString=None, displayName=None):
        if not displayName:
            displayName = layerName
        uri = QgsDataSourceURI()
        uri.setDatabase(self.dbm.db.databaseName())
        uri.setDataSource('', layerName, 'geometry')
        layer = QgsVectorLayer(uri.uri(), displayName, 'spatialite')
        if subsetString:
            layer.setSubsetString(subsetString)

        return layer

        # symbol_layer = QgsSimpleLineSymbolLayerV2()
        # symbol_layer.setWidth(0.6)
        # symbol_layer.setColor(QColor(100, 50, 140, 255))
        # self.siteLayer.rendererV2().symbols()[0].changeSymbolLayer(0, symbol_layer)


    def loadLayer(self, layer):
        QgsMapLayerRegistry.instance().addMapLayer(layer)


    def exportLayer(self, layer, time):
        geomType = "Punkt" if layer.geometryType() == 0 else "Polygon"
        saveDir = self.settings.value("APIS/working_dir", QDir.home().dirName())
        layerName = QFileDialog.getSaveFileName(self, u'Fundstellen {0} Export Speichern'.format(geomType), saveDir + "\\" + 'Fundstellen_{0}_{1}'.format(geomType, time), '*.shp')
        if layerName:
            check = QFile(layerName)
            if check.exists():
                if not QgsVectorFileWriter.deleteShapeFile(layerName):
                    QMessageBox.warning(None, "Fundstelle Export",
                                        u"Es ist nicht möglich die SHP Datei {0} zu überschreiben!".format(layerName))
                    return

            error = QgsVectorFileWriter.writeAsVectorFormat(layer, layerName, "UTF-8", layer.crs(), "ESRI Shapefile")

            if error == QgsVectorFileWriter.NoError:
                # QMessageBox.information(None, "Fundorte Export", u"Die ausgewählten Fundorte wurden in eine SHP Datei exportiert.")
                msgBox = QMessageBox()
                msgBox.setWindowTitle(u'Fundtelle Export')
                msgBox.setText(u"Die ausgewählten Fundstellen wurden in eine SHP Datei exportiert.")
                msgBox.addButton(QPushButton(u'SHP Datei laden'), QMessageBox.ActionRole)
                msgBox.addButton(QPushButton(u'Ordner öffnen'), QMessageBox.ActionRole)
                msgBox.addButton(QPushButton(u'SHP Datei laden und Ordner öffnen'), QMessageBox.ActionRole)
                msgBox.addButton(QPushButton(u'OK'), QMessageBox.AcceptRole)
                ret = msgBox.exec_()

                if ret == 0 or ret == 2:
                    # Load Shp File in QGIS
                    self.iface.addVectorLayer(layerName, "", 'ogr')

                if ret == 1 or ret == 2:
                    # Open Folder
                    OpenFileOrFolder(os.path.split(layerName)[0])

            else:
                QMessageBox.warning(None, "Fundstelle Export", u"Beim erstellen der SHP Datei ist ein Fehler aufgetreten.")


    def generateCenterPointLayer(self, polygonLayer, displayName=None):
        if not displayName:
            displayName = polygonLayer.name()
        epsg = polygonLayer.crs().authid()
        # QMessageBox.warning(None, "EPSG", u"{0}".format(epsg))
        layer = QgsVectorLayer("Point?crs={0}".format(epsg), displayName, "memory")
        layer.setCrs(polygonLayer.crs())
        provider = layer.dataProvider()
        provider.addAttributes(polygonLayer.dataProvider().fields())

        layer.updateFields()

        pointFeatures = []
        for polygonFeature in polygonLayer.getFeatures():
            polygonGeom = polygonFeature.geometry()
            pointGeom = polygonGeom.centroid()
            # if center point is not on polygon get the nearest Point
            if not polygonGeom.contains(pointGeom):
                pointGeom = polygonGeom.pointOnSurface()

            pointFeature = QgsFeature()
            pointFeature.setGeometry(pointGeom)
            pointFeature.setAttributes(polygonFeature.attributes())
            pointFeatures.append(pointFeature)

        provider.addFeatures(pointFeatures)

        layer.updateExtents()

        return layer