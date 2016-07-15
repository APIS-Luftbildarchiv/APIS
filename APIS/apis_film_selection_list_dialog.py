# -*- coding: utf-8 -*

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from qgis.gui import *
from qgis.core import *

from PyPDF2 import PdfFileMerger, PdfFileReader


from apis_db_manager import *
from apis_printer import *
from apis_image_registry import *

from apis_points2path import Points2Path

from functools import partial

import sys, math
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

# --------------------------------------------------------
# Film - Eingabe, Pflege
# --------------------------------------------------------
from apis_film_selection_list_form import *
from functools import partial

class ApisFilmSelectionListDialog(QDialog, Ui_apisFilmSelectionListDialog):

    def __init__(self, iface, model, dbm, imageRegistry, parent):
        QDialog.__init__(self)
        self.iface = iface
        self.model = model
        self.dbm = dbm
        self.imageRegistry = imageRegistry
        self.setupUi(self)
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)

        self.uiDisplayFlightPathBtn.clicked.connect(lambda: parent.openViewFlightPathDialog(self.getFilmList(), self))
        self.uiExportListAsPdfBtn.clicked.connect(self.DEVexportListAsPdf)
        self.uiExportDetailsAsPdfBtn.setEnabled(False)
        self.uiExportDetailsAsPdfBtn.clicked.connect(self.DEVexportDetailsAsPdf)

        self.accepted.connect(self.onAccepted)

        self.setupTable()

    def setupTable(self):
        self.uiFilmListTableV.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.uiFilmListTableV.setModel(self.model)
        self.uiFilmListTableV.setEditTriggers(QAbstractItemView.NoEditTriggers)

        #hide and sort Columns
        self.visibleColumns = ['filmnummer', 'flugdatum', 'anzahl_bilder', 'weise', 'art_ausarbeitung', 'militaernummer', 'militaernummer_alt']
        vCIdx = []
        for vC in self.visibleColumns:
            vCIdx.append(self.model.fieldIndex(vC))

        for c in range(self.model.columnCount()):
            if c not in vCIdx:
                self.uiFilmListTableV.hideColumn(c)

        hH = self.uiFilmListTableV.horizontalHeader()
        for i in range(len(vCIdx)):
            hH.moveSection(hH.visualIndex(vCIdx[i]), i)

        self.uiFilmListTableV.resizeColumnsToContents()
        self.uiFilmListTableV.resizeRowsToContents()
        self.uiFilmListTableV.horizontalHeader().setResizeMode(QHeaderView.Stretch)

        # signals
        self.uiFilmListTableV.doubleClicked.connect(self.viewFilm)
        self.uiFilmListTableV.selectionModel().selectionChanged.connect(self.onSelectionChanged)

        self.uiFilmListTableV.sortByColumn(0, Qt.AscendingOrder)

    def getFilmList(self, getAll=False):
        filmList = []
        if self.uiFilmListTableV.selectionModel().hasSelection() and not getAll:
            rows = self.uiFilmListTableV.selectionModel().selectedRows()
            for row in rows:
                #get filmnummer
                filmList.append(self.model.data(self.model.createIndex(row.row(), self.model.fieldIndex("filmnummer"))))
        else:
            for row in  range(self.model.rowCount()):
                filmList.append(self.model.data(self.model.createIndex(row, self.model.fieldIndex("filmnummer"))))

        return filmList

    def getFilmListWithRows(self, getAll=False):
        filmList = []
        if self.uiFilmListTableV.selectionModel().hasSelection() and not getAll:
            rows = self.uiFilmListTableV.selectionModel().selectedRows()
            for row in rows:
                rowContent = []
                for col in self.visibleColumns:
                    rowContent.append(self.model.data(self.model.createIndex(row.row(), self.model.fieldIndex(col))))
                filmList.append(rowContent)
        else:
            for row in  range(self.model.rowCount()):
                rowContent = []
                for col in self.visibleColumns:
                    #QMessageBox.warning(None, "Bild", u"{0}".format(self.model.data(self.model.createIndex(row, col))))
                    rowContent.append(self.model.data(self.model.createIndex(row, self.model.fieldIndex(col))))
                filmList.append(rowContent)

        return filmList

    def viewFilm(self):
        # QMessageBox.warning(None, "FilmNumber", "Double")
        filmIdx = self.model.createIndex(self.uiFilmListTableV.currentIndex().row(), self.model.fieldIndex("filmnummer"))
        self.filmNumberToLoad = self.model.data(filmIdx)
        self.accept()
        #QMessageBox.warning(None, "FilmNumber", unicode(self.model.data(filmIdx)))

    def onSelectionChanged(self, current, previous):
        if self.uiFilmListTableV.selectionModel().hasSelection() and len(self.uiFilmListTableV.selectionModel().selectedRows()) == 1:
            self.uiExportDetailsAsPdfBtn.setEnabled(True)
        else:
            self.uiExportDetailsAsPdfBtn.setEnabled(False)
        #QMessageBox.warning(None, "FilmNumber", "selection Changed")

    def checkSelection(self):
        if self.uiFilmListTableV.selectionModel().hasSelection():
            # Export selected or all items
            msgBox = QMessageBox()
            msgBox.setWindowTitle(u'Filme als PDF speichern')
            msgBox.setText(u'Wollen Sie die ausgewählten Filme oder die gesamte Liste als PDF speichern?')
            msgBox.addButton(QPushButton(u'Auswahl'), QMessageBox.YesRole)
            msgBox.addButton(QPushButton(u'Gesamte Liste'), QMessageBox.NoRole)
            msgBox.addButton(QPushButton(u'Abbrechen'), QMessageBox.RejectRole)
            ret = msgBox.exec_()

            return ret
        else:
            return 1

    def _generateWeatherCode(self, weatherCode):
        categories = ["Low Cloud Amount", "Visibility Kilometres", "Low Cloud Height", "Weather", "Remarks Mission", "Remarks Weather"]
        query = QSqlQuery(self.dbm.db)
        pos = 0
        help = 0
        weatherDescription = ""
        for c in weatherCode:
            qryStr = "select description from wetter where category = '{0}' and code = '{1}' limit 1".format(categories[pos-help], c)
            query.exec_(qryStr)
            query.first()
            fn = query.value(0)
            if pos <= 5:
                weatherDescription += categories[pos] + ': ' + fn
                if pos < 5:
                   weatherDescription += '\n'
            else:
                weatherDescription += '; ' + fn

            if pos >= 5:
                help += 1
            pos += 1
        return weatherDescription

    def exportDetailsAsPdf(self):

        selection = self.checkSelection()
        query = QSqlQuery(self.dbm.db)


        if selection == 0:
            filmList = self.getFilmList(False)
        elif selection == 1:
            filmList = self.getFilmList(True)
        else:
            return

        if filmList:
            saveDir = self.settings.value("APIS/working_dir", QDir.home().dirName())
            fileNames = []
            if len(filmList) <= 1:
                fn = u"Filmdetails_{0}".format(filmList[0])
            else:
                fn = u"Filmdetails_Sammlung"

            fileName = QFileDialog.getSaveFileName(self, u"Filmdetails speichern", saveDir + "\\" + '{0}_{1}'.format(fn,QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")), '*.pdf')

            if not fileName:
                return

            #Query Film Details!

            qryStr = "select * from film where filmnummer in ({0})".format("'"+"','".join(filmList)+"'")
            query.exec_(qryStr)



        #filmId = filmList[0]
        #if fileName:
            tempFileNames = []
            while query.next():

                filmDict = {}
                rec = query.record()
                for col in range(rec.count()):
                    val = unicode(rec.value(col))
                    if val.replace(" ", "")=='' or val=='NULL':
                        val = u"---"

                    filmDict[unicode(rec.fieldName(col))] = val

                filmDict['wetter_description'] = self._generateWeatherCode(filmDict['wetter'])
                filmDict['datum_druck'] =  QDate.currentDate().toString("yyyy-MM-dd")


                #for filmId in filmList:
                #QMessageBox.warning(None, "Save", fileName)
                #FIXME template from Settings ':/plugins/APIS/icons/settings.png'
                template = os.path.dirname(__file__) + "/composer/templates/FilmDetails.qpt" #':/plugins/APIS/composer/templates/FilmDetails.gpt' #'C:/Users/Johannes/.qgis2/python/plugins/APIS/composer/templates/FilmDetails.qpt'
                #if os.path.isfile(template):
                templateDOM = QDomDocument()
                templateDOM.setContent(QFile(template), False)

                #FIXME load correct Flightpath; from Settings
                printLayers = []
                flightpathDir = self.settings.value("APIS/flightpath_dir")
                #uri = flightpathDir + "\\2014\\02140301_lin.shp"
                #TODO RM uri = flightpathDir + "\\" + filmDict['flugdatum'][:4] + "\\" + IdToIdLegacy(filmDict["filmnummer"]) + "_lin.shp"
                uri = flightpathDir + "\\" + filmDict['flugdatum'][:4] + "\\" + filmDict["filmnummer"] + "_lin.shp"
                if not os.path.isfile(uri):
                    #TODO RM uri = flightpathDir + "\\" + filmDict['flugdatum'][:4] + "\\" + IdToIdLegacy(filmDict["filmnummer"]) + "_gps.shp"
                    uri = flightpathDir + "\\" + filmDict['flugdatum'][:4] + "\\" + filmDict["filmnummer"] + "_gps.shp"
                    if not os.path.isfile(uri):
                        uri = None  # flightpathDir + "\\2014\\02140301_lin.shp"
                        # FIXME: Create From GPS; KARTIERUNG
                printLayer = QgsVectorLayer(uri, "FlightPath", "ogr")
                printLayer.setCoordinateSystem()
                QgsMapLayerRegistry.instance().addMapLayer(printLayer, False) #False = don't add to Layers (TOC)
                #printLayer.updateExtents()
                #extent = printLayer.extent()

                #layerset.append(printLayer.id())
                printLayers.append(printLayer.id())

                #urlWithParams = ' '
                #urlWithParams = 'url=http://wms.jpl.nasa.gov/wms.cgi&layers=global_mosaic&styles=pseudo&format=image/jpeg&crs=EPSG:4326'
                #rlayer = QgsRasterLayer(urlWithParams, 'basemap', 'wms')
                #QgsMapLayerRegistry.instance().addMapLayer(rlayer)
                #printLayers.append(rlayer.id())



                ms = QgsMapSettings()
                ms.setCrsTransformEnabled(True)
                ms.setDestinationCrs(QgsCoordinateReferenceSystem(3857, QgsCoordinateReferenceSystem.EpsgCrsId))
                ms.setMapUnits(QGis.UnitType(0))
                ms.setOutputDpi(300)
                printLayer.setCoordinateSystem()

                extent = ms.layerExtentToOutputExtent(printLayer, printLayer.extent())
                ms.setExtent(extent)
                #mr.setLayerSet(layerset)

                #mapRectangle = QgsRectangle(140,-28,155,-15)
                #mr.setExtent(extent)

                comp = QgsComposition(ms)
                comp.setPlotStyle(QgsComposition.Print)
                comp.setPrintResolution(300)

                #m = self.mapper.model()
                #r = self.mapper.currentIndex()
                #filmDict = {'filmnummer':filmId}
               # for c in range(m.columnCount()):
                    #filmDict[m.headerData(c, Qt.Horizontal)] = unicode(m.data(m.createIndex(r, c)))
                    #QMessageBox.warning(None, "Save", "{0}:{1}".format(colName, value))


                comp.loadFromTemplate(templateDOM, filmDict)

                composerMap = comp.getComposerMapById(0)
                composerMap.setKeepLayerSet(True)
                composerMap.setLayerSet(printLayers)
                #composerMap.renderModeUpdateCachedImage()
                #ms.setLayers(printLayers)

                #if composerMap:
                    #QMessageBox.warning(None, "Save", composerMap)
               #composerMap.setKeepLayerSet(True)
                #composerMap.setLayerSet(layerset)


                if len(filmList) > 1:
                    tempFileName = fileName + "." + filmDict["filmnummer"] + ".pdf"
                    comp.exportAsPDF(tempFileName)
                    tempFileNames.append(tempFileName)
                else:
                    comp.exportAsPDF(fileName)
                #FIXME: Delete all alyers (array) not just one layer
                QgsMapLayerRegistry.instance().removeMapLayer(printLayer.id())
                #QgsMapLayerRegistry.instance().removeMapLayer(rlayer.id())

            if tempFileNames:
                #merge pdfs
                merger = PdfFileMerger()
                for filename in tempFileNames:
                    merger.append(PdfFileReader(file(filename, 'rb')))

                merger.write(fileName)

                for filename in tempFileNames:
                    try:
                        os.remove(filename)
                    except Exception, e:
                        continue

            try:
                if sys.platform == 'linux2':
                    subprocess.call(["xdg-open", fileName])
                else:
                    os.startfile(fileName)
            except Exception, e:
                pass

    def DEVexportDetailsAsPdf(self):
        #selection = self.checkSelection()

        #if selection == 0:
        #    filmList = self.getFilmList(False)
        #elif selection == 1:
        #    filmList = self.getFilmList(True)
        #else:
        #    return

        filmList = self.getFilmList(False)

        if len(filmList) <= 1:
            fn = u"Filmdetails_{0}".format(filmList[0])
        else:
            fn = u"Filmdetails_Sammlung"

        saveDir = self.settings.value("APIS/working_dir", QDir.home().dirName())
        fileName = QFileDialog.getSaveFileName(self, u"Filmdetails speichern", saveDir + "\\" + '{0}_{1}'.format(fn, QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")), '*.pdf')

        if fileName:
            qryStr = "SELECT * FROM film WHERE filmnummer IN ({0})".format(u",".join(u"'{0}'".format(film) for film in filmList))
            query = QSqlQuery(self.dbm.db)
            query.prepare(qryStr)
            query.exec_()

            tempFileNames = []

            query.seek(-1)
            while query.next():

                # Composer Items
                filmDict = {}

                # filmDict = {}
                rec = query.record()
                for col in range(rec.count()):
                    val = unicode(rec.value(col))
                    if val.replace(" ", "") == '' or val == 'NULL':
                        val = u"---"

                    filmDict[unicode(rec.fieldName(col))] = val

                filmDict['wetter_description'] = self._generateWeatherCode(filmDict['wetter'])
                filmDict['datum_druck'] = QDate.currentDate().toString("yyyy-MM-dd")

                layerSet = []

                # MapSettings
                mapSettings = QgsMapSettings()
                mapSettings.setCrsTransformEnabled(True)
                mapSettings.setDestinationCrs(QgsCoordinateReferenceSystem(3857, QgsCoordinateReferenceSystem.EpsgCrsId))
                mapSettings.setMapUnits(QGis.UnitType(0))
                mapSettings.setOutputDpi(300)

                # Vector Layer
                flightpathDir = self.settings.value("APIS/flightpath_dir")
                #TODO RM uri = flightpathDir + "\\" + filmDict['flugdatum'][:4] + "\\" + IdToIdLegacy(filmDict["filmnummer"]) + "_lin.shp"
                uri = flightpathDir + "\\" + filmDict['flugdatum'][:4] + "\\" + filmDict["filmnummer"] + "_lin.shp"
                if not os.path.isfile(uri):
                    #TODO RM uri = flightpathDir + "\\" + filmDict['flugdatum'][:4] + "\\" + IdToIdLegacy(filmDict["filmnummer"]) + "_gps.shp"
                    uri = flightpathDir + "\\" + filmDict['flugdatum'][:4] + "\\" + filmDict["filmnummer"] + "_gps.shp"
                    if not os.path.isfile(uri):
                        if filmDict["weise"] == u"senk.":
                            w = u"senk"
                        else:
                            w = u"schraeg"
                        uriDS = QgsDataSourceURI()
                        uriDS.setDatabase(self.dbm.db.databaseName())
                        uriDS.setDataSource('', 'luftbild_{0}_cp'.format(w), 'geometry')
                        mappingPnt = QgsVectorLayer(uriDS.uri(), 'mappingPnt', 'spatialite')
                        mappingPnt.setSubsetString(u'"filmnummer" = "{0}"'.format(filmDict["filmnummer"]))
                        if mappingPnt.dataProvider().featureCount() < 1:
                            uri = None  # flightpathDir + "\\2014\\02140301_lin.shp"
                        else:
                            p2p = Points2Path(mappingPnt, 'FlightPath', False, ["bildnummer_nn"])
                            vectorLayer = p2p.run()
                            uri = True
                    else:
                        gpsPnt = QgsVectorLayer(uri, "FlightPath", "ogr")
                        p2p = Points2Path(gpsPnt, 'FlightPath', False, ["bildnr"])  # bildnr > in filmnummer_gps.shp in aerloc
                        vectorLayer = p2p.run()
                else:
                    vectorLayer = QgsVectorLayer(uri, "FlightPath", "ogr")

                if uri:
                    #vectorLayer = QgsVectorLayer(uri, "FlightPath", "ogr")

                    # GET CRS FROM LAYER !!!!

                    # Sets layer's spatial reference system
                    vectorLayer.setCrs(QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId))
                    # Setup the coordinate system transformation for the layer.
                    vectorLayer.setCoordinateSystem()

                    lineSymbol = QgsLineSymbolV2.createSimple({'color': 'orange', 'line_width': '0.3'})
                    vectorLayer.rendererV2().setSymbol(lineSymbol)


                    QgsMapLayerRegistry.instance().addMapLayer(vectorLayer, False)  # False = don't add to Layers (TOC)


                    layerSet.append(vectorLayer.id())

                    extent = mapSettings.layerExtentToOutputExtent(vectorLayer, vectorLayer.extent())
                    extent.scale(1.1)

                    mapWidth = 85  # 160
                    mapHeight = 65  # 120
                    c = 40075016.6855785
                    mpW = extent.width() / mapWidth
                    mpH = extent.height() / mapHeight
                    zW = math.log(c / mpW, 2) - 8
                    zH = math.log(c / mpH, 2) - 8
                    z = math.floor(min(zW, zH)) + 2
                    # self.iface.messageBar().pushMessage(self.tr('Zoom'), "z: {0}".format(z), level=QgsMessageBar.INFO)

                    # Tile Layer (Background Map)
                    ds = {}
                    ds['type'] = 'TMS'
                    ds['alias'] = 'Google'
                    ds['copyright_text'] = 'Google'
                    ds['copyright_url'] = 'http://www.google.com'
                    ds['tms_url'] = "https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}"

                    service_info = TileServiceInfo(ds['alias'], ds['alias'], ds['tms_url'])
                    service_info.zmin = 0
                    service_info.zmax = int(z)
                    # if ds.tms_y_origin_top is not None:
                    #    service_info.yOriginTop = ds.tms_y_origin_top
                    service_info.epsg_crs_id = 3857
                    service_info.postgis_crs_id = None
                    service_info.custom_proj = None
                    service_info.bbox = BoundingBox(-180, -85.05, 180, 85.05)



                    #tileLayer = TileLayer(self, service_info, False)
                    tileLayer = TileLayer(service_info, False)
                    tileLayer.setCrs(QgsCoordinateReferenceSystem(3857, QgsCoordinateReferenceSystem.EpsgCrsId))

                    if not tileLayer.isValid():
                        error_message = self.tr('Background Layer %s can\'t be added to the map!') % ds['alias']
                        self.iface.messageBar().pushMessage(self.tr('Error'),
                                                            error_message,
                                                            level=QgsMessageBar.CRITICAL)
                        QgsMessageLog.logMessage(error_message, level=QgsMessageLog.CRITICAL)
                    else:
                        # Set Attributes
                        tileLayer.setAttribution(ds['copyright_text'])
                        tileLayer.setAttributionUrl(ds['copyright_url'])
                        QgsMapLayerRegistry.instance().addMapLayer(tileLayer, False)
                        layerSet.append(tileLayer.id())

                    # Set LayerSet
                    tileLayer.setExtent(extent)
                    mapSettings.setExtent(extent)

                    mapSettings.setLayers(layerSet)

                # Template
                template = os.path.dirname(__file__) + "/composer/templates/FilmDetails.qpt"  # map_print_test.qpt"
                templateDom = QDomDocument()
                templateDom.setContent(QFile(template), False)

                # Composition
                composition = QgsComposition(mapSettings)
                composition.setPlotStyle(QgsComposition.Print)
                composition.setPrintResolution(300)

                composition.loadFromTemplate(templateDom, filmDict)

                # Composer Map
                if uri:
                    composerMap = composition.getComposerMapById(0)
                    # self.iface.messageBar().pushMessage(self.tr('WH'), "w: {0}, h: {1}".format(composerMap.rect().width(), composerMap.rect().height()), level=QgsMessageBar.INFO)
                    composerMap.zoomToExtent(extent)

                if len(filmList) > 1:
                    tempFileName = fileName + "." + filmDict["filmnummer"] + ".pdf"
                    composition.exportAsPDF(tempFileName)
                    tempFileNames.append(tempFileName)
                else:
                    composition.exportAsPDF(fileName)


                # Remove Layers
                for layerId in layerSet:
                    QgsMapLayerRegistry.instance().removeMapLayer(layerId)


            if tempFileNames and len(filmList) > 1:
                merger = PdfFileMerger()
                for tempFileName in tempFileNames:
                    merger.append(PdfFileReader(file(fileName, 'rb')))

                merger.write(tempFileName)

                for tempFileName in tempFileNames:
                    try:
                        os.remove(tempFileName)
                    except Exception, e:
                        continue

            # Open PDF
            if sys.platform == 'linux2':
                subprocess.call(["xdg-open", fileName])
            else:
                os.startfile(fileName)

    def XXDEVexportDetailsAsPdf(self):
        selection = self.checkSelection()

        if selection == 0:
            filmList = self.getFilmList(False)
        elif selection == 1:
            filmList = self.getFilmList(True)
        else:
            return

        qryStr = "SELECT * FROM film WHERE filmnummer IN ({0})".format(u",".join(u"'{0}'".format(film) for film in filmList))
        printer = ApisFilmDetailPrinter(self, self.dbm, self.imageRegistry, True)
        printer.setQuery(qryStr)
        printer.printFilmDetail()

    def DEVexportListAsPdf(self):
        selection = self.checkSelection()

        if selection == 0:
            filmList = self.getFilmList(False)
        elif selection == 1:
            filmList = self.getFilmList(True)
        else:
            return

        qryStr = u"SELECT filmnummer AS Filmnummer, strftime('%d.%m.%Y', flugdatum) AS Flugdatum, anzahl_bilder AS Bildanzahl, weise AS Weise, art_ausarbeitung AS Art, militaernummer AS Militärnummer, militaernummer_alt AS 'Militärnummer Alt', CASE WHEN weise = 'senk.' THEN (SELECT count(*) from luftbild_senk_cp WHERE film.filmnummer = luftbild_senk_cp.filmnummer) ELSE (SELECT count(*) from luftbild_schraeg_cp WHERE film.filmnummer = luftbild_schraeg_cp.filmnummer) END AS Kartiert, 0 AS Gescannt FROM film WHERE filmnummer IN ({0}) ORDER BY filmnummer".format(u",".join(u"'{0}'".format(film) for film in filmList))

        printer = ApisListPrinter(self, self.dbm, self.imageRegistry, True, 1)
        printer.setupInfo(u"Filmliste", u"Filmliste speichern", u"Filmliste", 18)
        printer.setQuery(qryStr)
        printer.printList(u"Gescannt")

    def exportListAsPdf(self):

        selection = self.checkSelection()

        if selection == 0:
            filmList = self.getFilmListWithRows(False)
        elif selection == 1:
            filmList = self.getFilmListWithRows(True)
        else:
            return

        #fileName = 'C:\\apis\\temp\\BildListe.pdf'
        saveDir = self.settings.value("APIS/working_dir", QDir.home().dirName())
        fileName = QFileDialog.getSaveFileName(self, 'Filmliste Speichern', saveDir + "\\" + 'Filmliste_{0}'.format(QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")), '*.pdf')



        if fileName:

            ms = QgsMapSettings()
            comp = QgsComposition(ms)
            comp.setPlotStyle(QgsComposition.Print)
            comp.setPrintResolution(300)
            comp.setPaperSize(297.0, 210.0)

            #header
            hHight = 15
            fHight = 15
            margin = 15
            mTab = 5
            hWidth = comp.paperWidth()/2-margin
            fWidth = (comp.paperWidth()-(2*margin))/3

            page = 1
            prevPage = 0
            filmCount = 0
            filmCountTotal = 0
            pageBreak = 25
            for filmRow in filmList:
                filmCountTotal += 1
                filmCount += 1
                if filmCount > pageBreak:
                    filmCount = 1
                    page += 1
                if page > prevPage:
                    prevPage = page
                    #Header Left - Title
                    hLeft = QgsComposerLabel(comp)
                    hLeft.setItemPosition(margin, margin, hWidth , hHight, QgsComposerItem.UpperLeft, False, page)
                    hLeft.setBackgroundEnabled(True)
                    hLeft.setBackgroundColor(QColor("#CCCCCC"))
                    hLeft.setText(u"Filmliste")
                    hLeft.setVAlign(Qt.AlignVCenter)
                    hLeft.setMarginX(5)
                    hLeft.setFont(QFont("Arial", 16, 100))
                    comp.addItem(hLeft)
                    #Header Right - Stats
                    hRight = QgsComposerLabel(comp)
                    hRight.setItemPosition(comp.paperWidth()/2, margin, hWidth , hHight, QgsComposerItem.UpperLeft, False, page)
                    hRight.setBackgroundEnabled(True)
                    hRight.setBackgroundColor(QColor("#CCCCCC"))
                    hRight.setText(u"Anzahl:\t{0}".format(len(filmList)))
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



                    filmTab = QgsComposerTextTable(comp)
                    filmTab.setShowGrid(True)
                    filmTab.setGridStrokeWidth(0.2)
                    filmTab.setLineTextDistance(1.2)
                    filmTab.setHeaderFont(QFont("Arial",9,100))
                    #imageTab.setHeaderHAlignment(QgsComposerTable.HeaderCenter)
                    hLabels = [u"#", "Filmnummer", "Flugdatum", "Bildanzahl", "Weise", "Art", u"Militärnummer", u"Militärnummer Alt", "Kartiert", "Gescannt"]
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

                    filmTab.setHeaderLabels(hLabelsAdjust)
                    filmTab.setItemPosition(margin+mTab,margin+hHight+mTab, QgsComposerItem.UpperLeft, page)
                    comp.addItem(filmTab)

                if filmRow[3] == u"senk.":
                    fromTable = 'luftbild_senk_cp'
                    spatialIndicator = 'massstab'
                elif filmRow[3] == u"schräg":
                    fromTable = 'luftbild_schraeg_cp'
                filmid = filmRow[0]

                #QMessageBox.warning(None, "Bild", u"{0}, {1}".format(filmid, fromTable))

                query = QSqlQuery(self.dbm.db)
                qryStr = "select count(*) from {0} WHERE filmnummer = '{1}'".format(fromTable, filmid)
                query.exec_(qryStr)
                query.first()
                mappedImages = query.value(0)

                #imageDir = self.settings.value("APIS/image_dir")
                #TODO RM filmDirName = imageDir + "\\{0}".format(IdToIdLegacy(filmid))
                #filmDirName = imageDir + "\\{0}".format(filmid)
                #filmDir = QDir(filmDirName)
                #TODO RM scanns = len(filmDir.entryList([IdToIdLegacy(filmid)+"_*.jpg"], QDir.Files))
                # scanns = len(filmDir.entryList([filmid+"_*.jpg"], QDir.Files))
                #TODO RM scanns = self.imageRegistry.hasImageRE(IdToIdLegacy(filmid)+"_.+")
                scanns = self.imageRegistry.hasImageRE(filmid+"_.+")

                #imageTab.addRow([str(imageCountTotal).zfill(len(str(len(imageList))))])
                filmTab.addRow([str(filmCountTotal).zfill(len(str(len(filmList))))] + [unicode(item) for item in filmRow] + [unicode(mappedImages), unicode(scanns)])

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
                if sys.platform == 'linux2':
                    subprocess.call(["xdg-open", fileName])
                else:
                    os.startfile(fileName)
            except Exception, e:
                pass


    def onAccepted(self):
        self.accept()