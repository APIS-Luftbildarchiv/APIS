# -*- coding: utf-8 -*

import os, glob

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from PyQt4.QtXml import *

from qgis.core import *

from apis_db_manager import *
from apis_site_dialog import *
from functools import partial
from apis_utils import OpenFileOrFolder
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

# --------------------------------------------------------
# Film - Eingabe, Pflege
# --------------------------------------------------------
from apis_site_selection_list_form import *
from functools import partial
import subprocess

class ApisSiteSelectionListDialog(QDialog, Ui_apisSiteSelectionListDialog):
    def __init__(self, iface, dbm, imageRegistry, apisLayer):
        QDialog.__init__(self)
        self.iface = iface
        self.dbm = dbm
        self.imageRegistry = imageRegistry
        self.apisLayer = apisLayer
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)
        self.setupUi(self)

        self.query = None

        self.uiSiteListTableV.doubleClicked.connect(self.openSiteDialog)

        self.uiViewSitesBtn.clicked.connect(self.loadSiteInQgis)
        self.uiViewInterpretationBtn.clicked.connect(self.loadSiteInterpretationInQgis)
        self.uiExportSitesAsShpBtn.clicked.connect(self.exportSiteAsShp)
        self.uiExportSiteAsPdfBtn.clicked.connect(self.exportSiteAsPdf)
        self.uiExportListAsPdfBtn.clicked.connect(self.exportListAsPdf)

        self.siteDlg = None

    def hideEvent(self,event):
        self.query = None

    def loadSiteListBySpatialQuery(self, query=None, info=None, update=False):
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
                newCol = QStandardItem(value)
                newRow.append(newCol)

            self.model.appendRow(newRow)

        if self.model.rowCount() < 1:
            if not update:
                QMessageBox.warning(None, "Fundort Auswahl", u"Es wurden keine Fundorte gefunden!")
            self.query = None
            self.done(1)
            return False

        for col in range(rec.count()):
            self.model.setHeaderData(col, Qt.Horizontal, rec.fieldName(col))

        self.setupTable()

        self.uiImageCountLbl.setText(unicode(self.model.rowCount()))
        if info != None:
            self.uiInfoLbl.setText(info)

        return True

    def setupTable(self):
        self.uiSiteListTableV.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.uiSiteListTableV.setModel(self.model)
        self.uiSiteListTableV.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.uiSiteListTableV.resizeColumnsToContents()
        self.uiSiteListTableV.resizeRowsToContents()
        self.uiSiteListTableV.horizontalHeader().setResizeMode(QHeaderView.Stretch)


    def openSiteDialog(self, idx):
        siteNumber = self.model.item(idx.row(), 0).text()
        if self.siteDlg == None:
            self.siteDlg = ApisSiteDialog(self.iface, self.dbm, self.imageRegistry, self.apisLayer)
            self.siteDlg.siteEditsSaved.connect(self.reloadTable)
            self.siteDlg.siteDeleted.connect(self.reloadTable)
        self.siteDlg.openInViewMode(siteNumber)
        self.siteDlg.show()
        # Run the dialog event loop

        if self.siteDlg.exec_():
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
        self.siteDlg.removeSitesFromSiteMapCanvas()
        #QMessageBox.warning(None, self.tr(u"Load Site"), self.tr(u"For Site: {0}".format(siteNumber)))

    def reloadTable(self, editsSaved):
        self.query.exec_()
        #QMessageBox.information(None, "SqlQuery", self.query.executedQuery())
        self.loadSiteListBySpatialQuery(self.query, None, True)
        #QMessageBox.warning(None, self.tr(u"Load Site"), self.tr(u"Reload Table Now"))

    def loadSiteInQgis(self):
        siteList = self.askForSiteList()
        if siteList:
            #QMessageBox.warning(None, self.tr(u"SiteList"), u"{0}".format(u", ".join(siteList)))
            polygon, point = self.askForGeometryType()
            if polygon or point:
                #QMessageBox.warning(None, self.tr(u"SiteList"), u"{0}, {1}".format(polygon, point))

                # get PolygonLayer
                subsetString = u'"fundortnummer" IN ('
                for siteNumber in siteList:
                    subsetString += u'\'{0}\','.format(siteNumber)
                subsetString = subsetString[:-1]
                subsetString += u')'
                siteLayer = self.getSpatialiteLayer('fundort', subsetString)

                if polygon:
                    # load PolygonLayer
                    self.loadLayer(siteLayer)

                if point:
                    # generate PointLayer
                    centerPointLayer = self.generateCenterPointLayer(siteLayer)
                    # load PointLayer
                    self.loadLayer(centerPointLayer)

                self.close()

    def loadSiteInterpretationInQgis(self):
        siteList = self.askForSiteList([2])
        if siteList:
            interpretationsToLoad = []
            noInterpretations = []
            intBaseDir = self.settings.value("APIS/int_base_dir")
            intDir = self.settings.value("APIS/int_dir")
            for siteNumber, kgName in siteList:
                country, siteNumberN = siteNumber.split(".")
                siteNumberN = siteNumberN.zfill(6)
                if country == u"AUT":
                    kgName = u"{0} ".format(kgName.lower().replace(".", "").replace("-", " ").replace("(", "").replace(")", ""))
                else:
                    kgName = ""
                #QMessageBox.information(None, 'info', u"{0}, {1}, {2}, {3}".format(siteNumber, siteNumberN, country, kgName))

                shpFile = u"luftint_{0}.shp".format(siteNumberN)
                intShpPath = os.path.normpath(os.path.join(intBaseDir, country, u"{0}{1}".format(kgName, siteNumberN), intDir, shpFile))
                if os.path.isfile(intShpPath):
                    interpretationsToLoad.append(intShpPath)
                else:
                    noInterpretations.append(siteNumber)

            if len(interpretationsToLoad) > 0:
                for intShp in interpretationsToLoad:
                    # TODO load Shape Files with ApisLayerHandling
                    self.apisLayer.requestShapeFile(intShp, epsg=None, layerName=None, groupName="Interpretationen",useLayerFromTree=True, addToCanvas=True)

                    #QMessageBox.information(None, u"Interpretation", intShp)
            else:
                QMessageBox.warning(None, u"Fundort Interpretation", u"Für die ausgewählten Fundorte ist keine Interpretation vorhanden.")


            #subsetString += u'\'{0}\','.format(siteNumber)
            #subsetString = subsetString[:-1]
            #subsetString += u')'
            #siteLayer = self.getSpatialiteLayer('fundort_interpretation', subsetString)
            #count = siteLayer.dataProvider().featureCount()
            #QMessageBox.information(None, "Feature Count", "Feature Count: {0}".format(count))
            #count = 0
            #if count > 0:
            #    pass
                #siteListLayer = list(set(siteLayer.getValues('fundortnummer')[0]))
                #siteListLayer = [sub_list[0] for sub_list in list(siteLayer.getValues('fundortnummer'))]
                #QMessageBox.warning(None, u"Fundort Interpretation", u"Layer: {0}".format(u", ".join(siteListLayer)))
                #QMessageBox.warning(None, u"Fundort Interpretation", u"Selection: {0}".format(u",".join(siteList)))

                #noInterpretation = list(set(siteList) - set(siteListLayer))
                #if len(noInterpretation) > 0:
                 #   QMessageBox.warning(None, u"Fundort Interpretation", u"Für einige Fundorte ist keine Interpretation vorhanden. [{0}]".format(u", ".join(noInterpretation)))

                #self.loadLayer(siteLayer)
                #self.close()
           # else:
           #     QMessageBox.warning(None, u"Fundort Interpretation", u"Für die ausgewählten Fundorte ist keine Interpretation vorhanden.")

    def exportSiteAsShp(self):
        siteList = self.askForSiteList()
        if siteList:
            # QMessageBox.warning(None, self.tr(u"SiteList"), u"{0}".format(u", ".join(siteList)))
            polygon, point = self.askForGeometryType()
            if polygon or point:
                # QMessageBox.warning(None, self.tr(u"SiteList"), u"{0}, {1}".format(polygon, point))

                # get PolygonLayer
                subsetString = u'"fundortnummer" IN ('
                for siteNumber in siteList:
                    subsetString += u'\'{0}\','.format(siteNumber)
                subsetString = subsetString[:-1]
                subsetString += u')'
                siteLayer = self.getSpatialiteLayer('fundort', subsetString)

                now = QDateTime.currentDateTime()
                time = now.toString("yyyyMMdd_hhmmss")
                if polygon:
                    # save PolygonLayer
                    self.exportLayer(siteLayer, time)

                if point:
                    # generate PointLayer
                    centerPointLayer = self.generateCenterPointLayer(siteLayer)
                    # save PointLayer
                    self.exportLayer(centerPointLayer, time)

    def exportSiteAsPdf(self):
        siteList = self.askForSiteList()
        if siteList:

            if SitesHaveFindSpots(self.dbm.db, siteList):
                # At least one site has a FindSpot
                msgBox = QMessageBox()
                msgBox.setWindowTitle(u'Fundort als PDF exportieren')
                msgBox.setText(u"Wählen Sie eine der folgenden Druckoptionen.")
                msgBox.addButton(QPushButton(u'FO Detail'), QMessageBox.ActionRole)
                msgBox.addButton(QPushButton(u'FO Detail und FS Liste'), QMessageBox.ActionRole)
                msgBox.addButton(QPushButton(u'FO Detail, FS Liste und Detail'), QMessageBox.ActionRole)
                msgBox.addButton(QPushButton(u'Abbrechen'), QMessageBox.RejectRole)
                printMode = msgBox.exec_()

                if printMode not in [0, 1, 2]:
                    return
            else:
                # All sites have no FindSpot
                printMode = 0

            # Setup Output
            saveDir = self.settings.value("APIS/working_dir", QDir.home().dirName())
            timeStamp = QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")
            if printMode == 0:
                if len(siteList) == 1:
                    saveDialogTitle = u"Fundort"
                    targetFileNameTemplate = u"Fundort_{0}_{1}".format(siteList[0], timeStamp)
                else:
                    saveDialogTitle = u"Fundorte Sammlung"
                    targetFileNameTemplate = u"Fundorte_Sammlung_{0}".format(timeStamp)

            elif printMode == 1:
                if len(siteList) == 1:
                    saveDialogTitle = u"Fundort mit Fundstellenliste"
                    targetFileNameTemplate = u"Fundort_{0}_Fundstellenliste_{1}".format(siteList[0], timeStamp)
                else:
                    saveDialogTitle = u"Fundorte Sammlung mit Fundstellenlisten"
                    targetFileNameTemplate = u"Fundorte_Sammlung_Fundstellenlisten_{0}".format(timeStamp)

            elif printMode == 2:
                if len(siteList) == 1:
                    saveDialogTitle = u"Fundort mit Fundstellen"
                    targetFileNameTemplate = u"Fundort_{0}_Fundstellen_{1}".format(siteList[0], timeStamp)
                else:
                    saveDialogTitle = u"Fundorte Sammlung mit Fundstellen"
                    targetFileNameTemplate = u"Fundorte_Sammlung_Fundstellen_{0}".format(timeStamp)
            else:
                return

            targetFileName = QFileDialog.getSaveFileName(self, saveDialogTitle, os.path.join(saveDir, targetFileNameTemplate), "*.pdf")

            if targetFileName:

                if printMode in [0, 1, 2]:
                    # print details for all Sites
                    # Temp Folder
                    if printMode == 0 and len(siteList) == 1:
                        foDetailsPrinter = ApisSitePrinter(self, self.dbm, self.imageRegistry)
                        foDetailsPrinter.setStylesDir(self.apisLayer.getStylesDir())
                        sitePdfs = foDetailsPrinter.exportSiteDetailsPdf(siteList, targetFileName, timeStamp, False)
                    else:
                        targetDirName = os.path.join(os.path.dirname(os.path.abspath(targetFileName)), u"temp_apis_print")
                        try:
                            os.makedirs(targetDirName)
                        except OSError:
                            if not os.path.isdir(targetDirName):
                                raise

                        foDetailsPrinter = ApisSitePrinter(self, self.dbm, self.imageRegistry)
                        foDetailsPrinter.setStylesDir(self.apisLayer.getStylesDir())
                        sitePdfs = {}
                        for siteNumber in siteList:
                            sitePdf = foDetailsPrinter.exportSiteDetailsPdf([siteNumber], targetDirName, timeStamp, True)
                            sitePdfs[siteNumber] = sitePdf[siteNumber]

                if printMode in [1, 2]:
                    # print FindSpotLists for all Sites
                    findSpotListsDict = {}
                    for siteNumber in siteList:
                        if SiteHasFindSpot(self.dbm.db, siteNumber):
                            qryStr = u"SELECT fs.fundortnummer || '.' || fs.fundstellenummer AS Fundstellenummer, fo.katastralgemeindenummer AS 'KG Nummer', fo.katastralgemeinde AS 'KG Name', datierung_zeit || ',' || datierung_periode || ',' || datierung_periode_detail || ',' || phase_von || '-' || phase_bis AS Datierung, fundart AS Fundart FROM fundstelle fs, fundort fo WHERE fs.fundortnummer = fo.fundortnummer AND fs.fundortnummer = '{0}' ORDER BY fs.fundstellenummer".format(siteNumber)
                            fN = os.path.join(targetDirName, u"Fundstellenliste_{0}_{1}.pdf".format(siteNumber, timeStamp))
                            printer = ApisListPrinter(self, self.dbm, self.imageRegistry, False, True, fN, 1)
                            printer.setupInfo(u"Fundstellenliste", u"Fundstellenliste speichern", u"Fundstellenliste", 22)
                            printer.setQuery(qryStr)
                            findSpotListPdf = printer.printList()
                            findSpotListsDict[siteNumber] = findSpotListPdf

                if printMode == 2:
                    # print all FindSpots of each Site
                    findSpotList = GetFindSpotNumbers(self.dbm.db, siteList)
                    if findSpotList:
                        fsDetailsPrinter = ApisFindSpotPrinter(self, self.dbm, self.imageRegistry)
                        findSpots = fsDetailsPrinter.exportDetailsPdf(findSpotList, targetDirName, timeStamp, True)


                # Order files
                if not (printMode == 0 and len(siteList) == 1):
                    pdfFiles = []
                    for siteNumber in siteList:
                        #Site
                        pdfFiles.append(sitePdfs[siteNumber])
                        # FindSpotList for Site
                        if printMode in [1, 2]:
                            if siteNumber in findSpotListsDict:
                                pdfFiles.append(findSpotListsDict[siteNumber])
                        # FindSpots for Site
                        if printMode == 2:
                            if siteNumber in findSpots:
                                for findSpot in findSpots[siteNumber]:
                                    pdfFiles.append(findSpot)
                    if pdfFiles:
                        MergePdfFiles(targetFileName, pdfFiles)

                OpenFileOrFolder(targetFileName)



    def exportListAsPdf(self):
        siteList = self.askForSiteList()
        if siteList:
            #qryStr = u"SELECT filmnummer AS Filmnummer, strftime('%d.%m.%Y', flugdatum) AS Flugdatum, anzahl_bilder AS Bildanzahl, weise AS Weise, art_ausarbeitung AS Art, militaernummer AS Militärnummer, militaernummer_alt AS 'Militärnummer Alt', CASE WHEN weise = 'senk.' THEN (SELECT count(*) from luftbild_senk_cp WHERE film.filmnummer = luftbild_senk_cp.filmnummer) ELSE (SELECT count(*) from luftbild_schraeg_cp WHERE film.filmnummer = luftbild_schraeg_cp.filmnummer) END AS Kartiert, 0 AS Gescannt FROM film WHERE filmnummer IN ({0}) ORDER BY filmnummer".format(u",".join(u"'{0}'".format(site) for site in siteList))
            qryStr = u"SELECT fundortnummer AS Fundortnummer, katastralgemeindenummer AS 'KG Nummer', katastralgemeinde AS 'KG Name', flurname AS Flurname, fundgewinnung AS Fundgewinnung, sicherheit AS Sicherheit FROM fundort WHERE fundortnummer IN ({0}) ORDER BY land, katastralgemeindenummer, fundortnummer_nn".format(u",".join(u"'{0}'".format(site) for site in siteList))
            printer = ApisListPrinter(self, self.dbm, self.imageRegistry, True, False, None, 1)
            printer.setupInfo(u"Fundortliste", u"Fundortliste speichern", u"Fundortliste", 22)
            printer.setQuery(qryStr)
            printer.printList()

    def askForSiteList(self, plusCols=None):
        if self.uiSiteListTableV.selectionModel().hasSelection():
            #Abfrage ob Fundorte der selektierten Bilder Exportieren oder alle
            msgBox = QMessageBox()
            msgBox.setWindowTitle(u'Fundorte')
            msgBox.setText(u'Wollen Sie die ausgewählten Fundorte oder die gesamte Liste verwenden?')
            msgBox.addButton(QPushButton(u'Auswahl'), QMessageBox.YesRole)
            msgBox.addButton(QPushButton(u'Gesamte Liste'), QMessageBox.NoRole)
            msgBox.addButton(QPushButton(u'Abbrechen'), QMessageBox.RejectRole)
            ret = msgBox.exec_()

            if ret == 0:
                siteList = self.getSiteList(False, plusCols)
            elif ret == 1:
                siteList = self.getSiteList(True, plusCols)
            else:
                return None
        else:
            siteList = self.getSiteList(True, plusCols)

        return siteList

    def getSiteList(self, getAll, plusCols=None):
        siteList = []
        site = []
        if self.uiSiteListTableV.selectionModel().hasSelection() and not getAll:
            rows = self.uiSiteListTableV.selectionModel().selectedRows()
            for row in rows:
                if plusCols:
                    site = []
                if not self.uiSiteListTableV.isRowHidden(row.row()):
                    if plusCols:
                        site.append(self.model.item(row.row(), 0).text())
                        for col in plusCols:
                            site.append(self.model.item(row.row(), col).text())
                        siteList.append(site)
                    else:
                        siteList.append(self.model.item(row.row(), 0).text())
        else:
            for row in range(self.model.rowCount()):
                if plusCols:
                    site = []
                if not self.uiSiteListTableV.isRowHidden(row):
                    if plusCols:
                        site.append(self.model.item(row, 0).text())
                        for col in plusCols:
                            site.append(self.model.item(row, col).text())
                        siteList.append(site)
                    else:
                        siteList.append(self.model.item(row, 0).text())

        return siteList

    def askForGeometryType(self):
        # Abfrage ob Fundorte der selektierten Bilder Exportieren oder alle
        msgBox = QMessageBox()
        msgBox.setWindowTitle(u'Fundorte')
        msgBox.setText(u'Wollen Sie für die Fundorte Polygone, Punkte oder beide Layer verwenden?')
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

        #symbol_layer = QgsSimpleLineSymbolLayerV2()
        #symbol_layer.setWidth(0.6)
        #symbol_layer.setColor(QColor(100, 50, 140, 255))
        #self.siteLayer.rendererV2().symbols()[0].changeSymbolLayer(0, symbol_layer)

    def loadLayer(self, layer):
        QgsMapLayerRegistry.instance().addMapLayer(layer)

    def exportLayer(self, layer, time):
        geomType = "Punkt" if layer.geometryType() == 0 else "Polygon"
        saveDir = self.settings.value("APIS/working_dir", QDir.home().dirName())
        layerName = QFileDialog.getSaveFileName(self, u'Fundorte {0} Export Speichern'.format(geomType), saveDir + "\\" + 'Fundorte_{0}_{1}'.format(geomType, time), '*.shp')
        if layerName:
            check = QFile(layerName)
            if check.exists():
                if not QgsVectorFileWriter.deleteShapeFile(layerName):
                    QMessageBox.warning(None, "Fundorte Export", u"Es ist nicht möglich die SHP Datei {0} zu überschreiben!".format(layerName))
                    return

            error = QgsVectorFileWriter.writeAsVectorFormat(layer, layerName, "UTF-8", layer.crs(), "ESRI Shapefile")

            if error == QgsVectorFileWriter.NoError:
                #QMessageBox.information(None, "Fundorte Export", u"Die ausgewählten Fundorte wurden in eine SHP Datei exportiert.")
                msgBox = QMessageBox()
                msgBox.setWindowTitle(u'Fundorte Export')
                msgBox.setText(u"Die ausgewählten Fundorte wurden in eine SHP Datei exportiert.")
                msgBox.addButton(QPushButton(u'SHP Datei laden'), QMessageBox.ActionRole)
                msgBox.addButton(QPushButton(u'Ordner öffnen'), QMessageBox.ActionRole)
                msgBox.addButton(QPushButton(u'SHP Datei laden und Ordner öffnen'), QMessageBox.ActionRole)
                msgBox.addButton(QPushButton(u'OK'), QMessageBox.AcceptRole)
                ret = msgBox.exec_()

                if ret == 0 or ret == 2:
                    # Shp Datei in QGIS laden
                    self.iface.addVectorLayer(layerName, "", 'ogr')

                if ret == 1 or ret == 2:
                    # ordner öffnen
                    OpenFileOrFolder(os.path.split(layerName)[0])

            else:
                QMessageBox.warning(None, "Fundorte Export", u"Beim erstellen der SHP Datei ist ein Fehler aufgetreten.")


    def generateCenterPointLayer(self, polygonLayer, displayName=None):
        if not displayName:
            displayName = polygonLayer.name()
        epsg = polygonLayer.crs().authid()
        #QMessageBox.warning(None, "EPSG", u"{0}".format(epsg))
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