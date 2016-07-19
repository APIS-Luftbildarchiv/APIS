# -*- coding: utf-8 -*

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from PyQt4.QtXml import *
from qgis.core import *
from qgis.gui import QgsMapCanvas, QgsMapCanvasLayer
from qgis.utils import *

from apis_db_manager import *
from apis_film_number_selection_dialog import *
from apis_new_film_dialog import *
from apis_edit_weather_dialog import *
from apis_search_film_dialog import *
from apis_film_selection_list_dialog import *
from apis_view_flight_path_dialog import *
from apis_image_selection_list_dialog import *
from apis_site_selection_list_dialog import *
from apis_image_registry import *

from py_tiled_layer_070.tilelayer import TileLayer, TileLayerType
from py_tiled_layer_070.tiles import TileLayerDefinition, BoundingBox #, TileServiceInfo

from apis_points2path import Points2Path

from functools import partial
import subprocess
import string

from apis_exif2points import Exif2Points


import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/composer")

# --------------------------------------------------------
# Film - Eingabe, Pflege
# --------------------------------------------------------
from apis_film_form import *

class ApisFilmDialog(QDialog, Ui_apisFilmDialog):

    FIRST, PREV, NEXT, LAST = range(4)

    def __init__(self, iface, dbm, imageRegistry, apisLayer):
        QDialog.__init__(self)
        self.iface = iface
        self.dbm = dbm
        self.imageRegistry = imageRegistry
        self.apisLayer = apisLayer
        self.setupUi(self)

        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)

        self.editMode = False
        self.addMode = False
        self.initalLoad = True
        # Signals/Slot Connections
        self.rejected.connect(self.onReject)
        #self.uiButtonBox.rejected.connect(self.onReject)
        self.uiOkBtn.clicked.connect(self.onAccept)
        self.uiCancelBtn.clicked.connect(self.cancelEdit)
        self.uiSaveBtn.clicked.connect(self.saveEdits)

        self.uiFilmSelectionBtn.clicked.connect(self.openFilmSelectionDialog)

        self.uiNewFilmBtn.clicked.connect(self.openNewFilmDialog)
        self.uiSearchFilmBtn.clicked.connect(self.openSearchFilmDialog)
        self.uiEditWeatherBtn.clicked.connect(self.openEditWeatherDialog)

        #self.uiExportPdfBtn.clicked.connect(self.exportDetailsPdf)
        self.uiExportPdfBtn.clicked.connect(self.mapPrintTest)

        #self.uiShowFlightPathBtn.clicked.connect(partial(self.openViewFlightPathDialog, [self.uiCurrentFilmNumberEdit.text()]))
        self.uiShowFlightPathBtn.clicked.connect(lambda: self.openViewFlightPathDialog([self.uiCurrentFilmNumberEdit.text()]))
        self.uiListSitesOfFilmBtn.clicked.connect(self.openSiteSelectionListDialog)
        self.uiListImagesOfFilmBtn.clicked.connect(self.openImageSelectionListDialog)
        self.uiExtractGpsFromImagesBtn.clicked.connect(self.extractGpsFromImages)

        self.uiWeatherCodeEdit.textChanged.connect(self.generateWeatherCode)
        self.uiFilmModeCombo.currentIndexChanged.connect(self.onFilmModeChanged)

        # init Project Btn
        self.uiAddProjectBtn.clicked.connect(self.addProject)
        self.uiRemoveProjectBtn.clicked.connect(self.removeProject)
        #self.uiButtonBox.button(QDialogButtonBox.Ok).setDefault(False)
        #self.uiButtonBox.button(QDialogButtonBox.Ok).setAutoDefault(False)
        #self.uiButtonBox.button(QDialogButtonBox.Cancel).setDefault(False)
        #self.uiButtonBox.button(QDialogButtonBox.Cancel).setAutoDefault(False)

        # Setup Sub-Dialogs
        self.filmSelectionDlg = ApisFilmNumberSelectionDialog(self.iface, self.dbm)
        self.newFilmDlg = ApisNewFilmDialog(self.iface)
        self.searchFilmDlg = ApisSearchFilmDialog(self.iface, self.dbm)
        self.editWeatherDlg = ApisEditWeatherDialog(self.iface, self.dbm)
        self.viewFlightPathDlg = ApisViewFlightPathDialog(self.iface, self.dbm)
        self.siteSelectionListDlg = ApisSiteSelectionListDialog(self.iface, self.dbm, self.imageRegistry, self.apisLayer)
        self.imageSelectionListDlg = ApisImageSelectionListDialog(self.iface, self.dbm, self.imageRegistry)


        # Setup film model
        self.model = QSqlRelationalTableModel(self, self.dbm.db)
        self.model.setTable("film")
        self.model.select()
        while (self.model.canFetchMore()):
            self.model.fetchMore()

        self.setupMapper()
        self.setupComboBox(self.uiProjectSelectionCombo, "projekt", 0, None)

        self.setupComboBox(self.newFilmDlg.uiProducerCombo, "hersteller", 2, None)

        self.setupNavigation()

        self.mapper.toFirst()

        self.initalLoad = False

    def setupMapper(self):
        self.mapper = QDataWidgetMapper(self)

        self.mapper.currentIndexChanged.connect(self.onCurrentIndexChanged)

        self.mapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
        self.mapper.setItemDelegate(FilmDelegate())

        self.mapper.setModel(self.model)

        self.mandatoryEditors = [self.uiImageCountEdit, self.uiCameraCombo, self.uiFilmMakeCombo, self.uiFilmModeCombo]
        self.disableEditorsIfOblique = [self.uiCameraNumberEdit, self.uiCalibratedFocalLengthEdit]
        # LineEdits & PlainTextEdits
        self.intValidator = QIntValidator()
        self.doubleValidator = QDoubleValidator()
        self.lineEditMaps = {
            "filmnummer": {
                "editor": self.uiCurrentFilmNumberEdit
            },
            "hersteller": {
                "editor": self.uiProducerEdit
            },
            "anzahl_bilder":{
                "editor": self.uiImageCountEdit,
                "validator": self.intValidator
            },
            "militaernummer":{
                "editor": self.uiMilitaryNumberEdit
            },
            "militaernummer_alt":{
                "editor": self.uiOldMilitaryNumberEdit
            },
            "form1":{
                "editor": self.uiFormat1Edit
            },
            "form2":{
                "editor": self.uiFormat2Edit
            },
            "kalibrierungsnummer":{
                "editor": self.uiCameraNumberEdit
            },
            "kammerkonstante":{
                "editor": self.uiCalibratedFocalLengthEdit,
                "validator": self.doubleValidator
            },
            "kassettennummer":{
                "editor": self.uiCassetteEdit
            },
            "art_ausarbeitung":{
                "editor": self.uiFilmMakeEdit
            },
            "fotograf":{
                "editor": self.uiPhotographerEdit
            },
            "pilot":{
                "editor": self.uiPilotEdit
            },
            "flugzeug":{
                "editor": self.uiAirplaneEdit
            },
            "abflug_flughafen":{
                "editor": self.uiDepartureAirportEdit
            },
            "ankunft_flughafen":{
                "editor": self.uiArrivalAirportEdit
            },
            "flugzeit":{
                "editor": self.uiFlightDurationEdit
            },
            "wetter":{
                "editor": self.uiWeatherCodeEdit
            },
            "kommentar": {
                "editor": self.uiCommentsPTxt
            }
        }
        for key, item in self.lineEditMaps.items():
            self.mapper.addMapping(item["editor"], self.model.fieldIndex(key))
            if "validator" in item:
                item["editor"].setValidator(item["validator"])
            #item["editor"].textChanged.connect(partial(self.onLineEditChanged, item["editor"]))
            item["editor"].textChanged.connect(self.onLineEditChanged)
        #Text
        #self.mapper.addMapping(self.uiCommentsPTxt, self.model.fieldIndex("kommentar"))

        # Date and Times
        #self.mapper.addMapping(self.uiFlightDate, self.model.fieldIndex("flugdatum"))
        self.mapper.addMapping(self.uiFlightQgsDate, self.model.fieldIndex("flugdatum"))
        #self.mapper.addMapping(self.uiInitalEntryDate, self.model.fieldIndex("datum_ersteintrag"))
        self.mapper.addMapping(self.uiInitalEntryQgsDate, self.model.fieldIndex("datum_ersteintrag"))
        #self.mapper.addMapping(self.uiLastChangesDate, self.model.fieldIndex("datum_aenderung"))
        self.mapper.addMapping(self.uiLastChangesQgsDate, self.model.fieldIndex("datum_aenderung"))

        self.mapper.addMapping(self.uiDepartureTime, self.model.fieldIndex("abflug_zeit"))
        self.mapper.addMapping(self.uiArrivalTime, self.model.fieldIndex("ankunft_zeit"))
        self.uiDepartureTime.timeChanged.connect(self.onFlightTimeChanged)
        self.uiArrivalTime.timeChanged.connect(self.onFlightTimeChanged)

        # ComboBox without Model
        self.mapper.addMapping(self.uiFilmModeCombo, self.model.fieldIndex("weise"))
        self.uiFilmModeCombo.editTextChanged.connect(self.onLineEditChanged)
        self.uiFilmModeCombo.setAutoCompletion(True)
        self.uiFilmModeCombo.lineEdit().setValidator(InListValidator([self.uiFilmModeCombo.itemText(i) for i in range(self.uiFilmModeCombo.count())], self.uiFilmModeCombo.lineEdit(), None, self))

        # ComboBox with Model
        self.comboBoxMaps = {
            "archiv": {
                "editor": self.uiArchiveCombo,
                "table": "hersteller",
                "modelcolumn": 2,
                "depend": None
            },
            "kamera": {
                "editor": self.uiCameraCombo,
                "table": "kamera",
                "modelcolumn": 0,
                "depend": [{"form1": self.uiFormat1Edit}, {"form2": self.uiFormat2Edit}]
            },
            "filmfabrikat": {
                "editor": self.uiFilmMakeCombo,
                "table": "film_fabrikat",
                "modelcolumn": 0,
                "depend": [{"art": self.uiFilmMakeEdit}]
            },
            "target": {
                "editor": self.uiTargetCombo,
                "table": "target",
                "modelcolumn": 0,
                "depend": None
            },
            "copyright": {
                "editor": self.uiCopyrightCombo,
                "table": "copyright",
                "modelcolumn": 0,
                "depend": None
            }
        }
        for key, item in self.comboBoxMaps.items():
            self.mapper.addMapping(item["editor"], self.model.fieldIndex(key))
            self.setupComboBox(item["editor"], item["table"], item["modelcolumn"], item["depend"])
            item["editor"].editTextChanged.connect(self.onLineEditChanged)

        self.mapper.addMapping(self.uiProjectList, self.model.fieldIndex("projekt"))


    def setupComboBox(self, editor, table, modelColumn, depend):
        model = QSqlRelationalTableModel(self, self.dbm.db)
        model.setTable(table)
        model.select()

        tv = QTableView()
        editor.setView(tv)

        tv.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        tv.setSelectionMode(QAbstractItemView.SingleSelection)
        tv.setSelectionBehavior(QAbstractItemView.SelectRows)
        tv.setAutoScroll(False)

        editor.setModel(model)

        editor.setModelColumn(modelColumn)
        editor.setInsertPolicy(QComboBox.NoInsert)

        tv.resizeColumnsToContents()
        tv.resizeRowsToContents()
        tv.verticalHeader().setVisible(False)
        tv.horizontalHeader().setVisible(True)
        #tv.setMinimumWidth(tv.horizontalHeader().length())
        tv.horizontalHeader().setResizeMode(QHeaderView.Stretch)

        editor.setAutoCompletion(True)
        editor.lineEdit().setValidator(InListValidator([editor.itemText(i) for i in range(editor.count())], editor.lineEdit(), depend, self))

        if depend:
            editor.currentIndexChanged.connect(partial(self.updateDepends, editor, depend))

    def updateDepends(self, editor, depend):
         for dep in depend:
            for key, value in dep.iteritems():
                idx = editor.model().createIndex(editor.currentIndex(), editor.model().fieldIndex(key))
                value.setText(unicode(editor.model().data(idx)))
                #QMessageBox.warning(None, "Test", str(idx))


    def setupNavigation(self):
        self.uiFirstFilmBtn.clicked.connect(partial(self.loadRecordByNavigation, ApisFilmDialog.FIRST))
        self.uiPreviousFilmBtn.clicked.connect(partial(self.loadRecordByNavigation, ApisFilmDialog.PREV))
        self.uiNextFilmBtn.clicked.connect(partial(self.loadRecordByNavigation, ApisFilmDialog.NEXT))
        self.uiLastFilmBtn.clicked.connect(partial(self.loadRecordByNavigation, ApisFilmDialog.LAST))

        self.uiTotalFilmCountLbl.setText(str(self.model.rowCount()))
        self.intRecordValidator = QIntValidator(1, self.model.rowCount())
        self.uiCurrentFilmCountEdit.setValidator(self.intRecordValidator)
        self.uiCurrentFilmCountEdit.setText(str(self.mapper.currentIndex() + 1))
        self.uiCurrentFilmCountEdit.editingFinished.connect(lambda: self.loadRecordById(int(self.uiCurrentFilmCountEdit.text()) - 1))
        # QMessageBox.warning(None, "Test", str(self.mapper.itemDelegate()))


    def enableItemsInLayout(self, layout, enable):
        for i in range(layout.count()):
            if layout.itemAt(i).widget():
                layout.itemAt(i).widget().setEnabled(enable)

    def loadRecordByNavigation(self, mode):
        #self.mapper.submit()
        #self.submitChanges()
        self.initalLoad = True
        if mode == ApisFilmDialog.FIRST:
            self.mapper.toFirst()
        elif mode == ApisFilmDialog.PREV:
            self.mapper.toPrevious()
        elif mode == ApisFilmDialog.NEXT:
            self.mapper.toNext()
        elif mode == ApisFilmDialog.LAST:
            self.mapper.toLast()
        self.initalLoad = False

    def loadRecordById(self, id):
        #self.submitChanges
        self.initalLoad = True
        self.mapper.setCurrentIndex(id)
        self.initalLoad = False

    def loadRecordByKeyAttribute(self, attribute, value):
        #self.model.setFilter(attribute + " = '" + value + "'")
        #self.model.select()
        # self.mapper.toFirst()

        query = QSqlQuery(self.dbm.db)
        #qryStr = "select {0} from film where {0} = '{1}' limit 1".format(attribute, value)
        #qryStr = "SELECT rowid FROM film WHERE {0} = '{1}' limit 1".format(attribute, value)
        qryStr = "SELECT" \
                 "  (SELECT COUNT(*)" \
                 "       FROM film AS t2" \
                 "       WHERE t2.rowid < t1.rowid" \
                 "      ) + (" \
                 "         SELECT COUNT(*)" \
                 "         FROM film AS t3" \
                 "        WHERE t3.rowid = t1.rowid AND t3.rowid < t1.rowid" \
                 "      ) AS rowNum" \
                 "   FROM film AS t1" \
                 "   WHERE {0} = '{1}'" \
                 "   ORDER BY t1.rowid ASC".format(attribute, value)

        query.exec_(qryStr)

        #QMessageBox.warning(None, "Test", str(query.size()) + ',' + str(query.numRowsAffected()))

        query.first()
        fn = query.value(0)

        if fn != None:
            self.loadRecordById(fn)
            return True
        else:
            # Film does not exist
            QMessageBox.warning(None, "Film Nummer", unicode("Der Film mit der Nummer {0} existiert nicht!".format(value)))
            return False

        #self.model.setFilter('')
        #self.model.select()
        #while (self.model.canFetchMore()):
            #self.model.fetchMore()

    def submitChanges(self):
        self.mapper.submit()

    def onCurrentIndexChanged(self):
        self.uiCurrentFilmCountEdit.setText(str(self.mapper.currentIndex() + 1))
        self.onFilmModeChanged()

    def onFlightTimeChanged(self):
        dTime = self.uiDepartureTime.time()
        aTime = self.uiArrivalTime.time()
        flightDuration = dTime.secsTo(aTime)
        self.uiFlightDurationEdit.setText(unicode(flightDuration/60))

    def disableIfOblique(self, isOblique):
        for editor in self.disableEditorsIfOblique:
            editor.setDisabled(isOblique)

    def onFilmModeChanged(self):
        if self.uiFilmModeCombo.currentText() == u'schräg':
            self.disableIfOblique(True)
        else:
            self.disableIfOblique(False)

    def onLineEditChanged(self):
        sender = self.sender()
        if not self.editMode and not self.initalLoad:
            self.startEditMode()
        if not self.initalLoad:
            sender.setStyleSheet("{0} {{background-color: rgb(153, 204, 255);}}".format(sender.metaObject().className()))
            self.editorsEdited.append(sender)

    def onComboBoxChanged(self, editor):
        pass

    def addProject(self):
        editor = self.uiProjectList
        value = self.uiProjectSelectionCombo.currentText()
        notInList = True
        for row in range(editor.count()):
            if value == editor.item(row).data(0):
                notInList = False
                break
        if notInList:
            editor.addItem(value)
            editor.sortItems()
            if not self.editMode and not self.initalLoad:
                self.startEditMode()
            if not self.initalLoad:
                editor.setStyleSheet("{0} {{background-color: rgb(153, 204, 255);}}".format(editor.metaObject().className()))
                self.editorsEdited.append(editor)

    def removeProject(self):
        editor =  self.uiProjectList
        editor.takeItem(self.uiProjectList.currentRow())
        if not self.editMode and not self.initalLoad:
            self.startEditMode()
        if not self.initalLoad:
            editor.setStyleSheet("{0} {{background-color: rgb(153, 204, 255);}}".format(editor.metaObject().className()))
            self.editorsEdited.append(editor)


    def onAccept(self):
        '''
        Check DB
        Save options when pressing OK button
        Update Plugin Status
        '''

        # Save Settings

        self.accept()

    def onReject(self):
        '''
        Run some actions when
        the user closes the dialog
        '''
        if self.editMode:
            res = self.cancelEdit()
            if res:
                self.close()
            else:
                self.show()
        else:
            self.close()

    def extractGpsFromImages(self):
        key = self.uiCurrentFilmNumberEdit.text()
        #TODO RM  e2p = Exif2Points(self.iface, IdToIdLegacy(key))   TODO RM LEGACY
        e2p = Exif2Points(self.iface, key)
        layer = e2p.run()
        if layer:
            self.iface.addVectorLayer(layer, "flugstrecke {0} gps p".format(key), 'ogr')


    def mapPrintTest(self):
        filmId = self.uiCurrentFilmNumberEdit.text()
        saveDir = self.settings.value("APIS/working_dir", QDir.home().dirName())
        fileName = QFileDialog.getSaveFileName(self, 'Film Details', saveDir + "\\" + 'FilmDetails_{0}_{1}'.format(filmId ,QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")), '*.pdf')

        if fileName:

            qryStr = u"SELECT * FROM film WHERE filmnummer IN ('{0}')".format(filmId)
            query = QSqlQuery(self.dbm.db)
            query.prepare(qryStr)
            query.exec_()

            filmDict = {}
            query.seek(-1)
            while query.next():
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
            #TODO RM uri = flightpathDir + "\\2010\\02101101_lin.shp"
            #TODO RM uri = flightpathDir + "\\" + filmDict['flugdatum'][:4] + "\\" + IdToIdLegacy(filmDict["filmnummer"]) + "_lin.shp"   TODO RM
            uri = flightpathDir + "\\" + filmDict['flugdatum'][:4] + "\\" + filmDict["filmnummer"] + "_lin.shp"
            if not os.path.isfile(uri):
                #TODO RM uri = flightpathDir + "\\" + filmDict['flugdatum'][:4] + "\\" + IdToIdLegacy(filmDict["filmnummer"]) + "_gps.shp" TODO RM
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
                    p2p = Points2Path(gpsPnt, 'FlightPath', False,
                                      ["bildnr"])  # bildnr > in filmnummer_gps.shp in aerloc
                    vectorLayer = p2p.run()
            else:
                vectorLayer = QgsVectorLayer(uri, "FlightPath", "ogr")

            if uri:
                #vectorLayer = QgsVectorLayer(uri, "FlightPath", "ogr")

                # GET CRS FROM LAYER !!!!

                #Sets layer's spatial reference system
                vectorLayer.setCrs(QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId))
                #Setup the coordinate system transformation for the layer.
                vectorLayer.setCoordinateSystem()

                lineSymbol = QgsLineSymbolV2.createSimple({'color':'orange', 'line_width':'0.3'})
                vectorLayer.rendererV2().setSymbol(lineSymbol)

                QgsMapLayerRegistry.instance().addMapLayer(vectorLayer, False) #False = don't add to Layers (TOC)
                layerSet.append(vectorLayer.id())

                extent = mapSettings.layerExtentToOutputExtent(vectorLayer, vectorLayer.extent())
                extent.scale(1.1)

                #QMessageBox.information(None, "Extent", "w: {0}, h: {1}".format(extent.width(), extent.height()))

                #e = vectorLayer.extent()
                #eGeo = QgsGeometry.fromRect(e)
                #gt = QgsCoordinateTransform(QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId), QgsCoordinateReferenceSystem(3857, QgsCoordinateReferenceSystem.EpsgCrsId))
                #eGeo.transform(gt)
                #eRect = eGeo.boundingBox()

                import math
                mapWidth = 85 #160
                mapHeight = 65 #120
                c = 40075016.6855785
                mpW = extent.width() / mapWidth
                mpH = extent.height() / mapHeight
                zW = math.log(c/mpW, 2) - 8
                zH = math.log(c/mpH, 2) - 8
                z = math.floor(min(zW,zH)) + 2
                #self.iface.messageBar().pushMessage(self.tr('Zoom'), "z: {0}".format(z), level=QgsMessageBar.INFO)


                # Tile Layer (Background Map)
                # TODO: Move To Settings ...
                ds = {}
                #ds['type'] = 'TMS'
                ds['title'] = 'basemap.at'
                ds['attribution'] = 'basemap.at'
                ds['attributionUrl'] = 'http://www.basemap.at'
                ds['serviceUrl'] = "http://maps.wien.gv.at/basemap/geolandbasemap/normal/google3857/{z}/{y}/{x}.png" #"https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}"
                ds['yOriginTop'] = 1
                ds['zmin'] = 0
                ds['zmax'] = int(z)
                ds['bbox'] = BoundingBox(-180, -85.05, 180, 85.05)
                #title, attribution, attributionUrl, serviceUrl, yOriginTop = 1, zmin = TileDefaultSettings.ZMIN, zmax = TileDefaultSettings.ZMAX, bbox = None)

                layerDef = TileLayerDefinition(ds['title'], ds['attribution'], ds['attributionUrl'], ds['serviceUrl'], ds['yOriginTop'], ds['zmin'], ds['zmax'], ds['bbox'])
                #service_info.zmin = 0
                #service_info.zmax = int(z)
                #if ds.tms_y_origin_top is not None:
                #    service_info.yOriginTop = ds.tms_y_origin_top
                #service_info.epsg_crs_id = 3857
               # service_info.postgis_crs_id = None
                #service_info.custom_proj = None
                #service_info.bbox = BoundingBox(-180, -85.05, 180, 85.05)

                #tileLayer = TileLayer(self, service_info, False)
                #tileLayer = TileLayer(service_info, False)
                #tileLayer = TileLayer(self, layerDef, False)
                tileLayer = TileLayer(layerDef, False)
                tileLayer.setCrs(QgsCoordinateReferenceSystem(3857, QgsCoordinateReferenceSystem.EpsgCrsId))


                if not tileLayer.isValid():
                    error_message = self.tr('Background Layer %s can\'t be added to the map!') % ds['alias']
                    self.iface.messageBar().pushMessage(self.tr('Error'),
                                                       error_message,
                                                       level=QgsMessageBar.CRITICAL)
                    QgsMessageLog.logMessage(error_message, level=QgsMessageLog.CRITICAL)
                else:
                    # Set Attributes
                    #tileLayer.setAttribution(ds['copyright_text'])
                    #tileLayer.setAttributionUrl(ds['copyright_url'])
                    QgsMapLayerRegistry.instance().addMapLayer(tileLayer, False)
                    layerSet.append(tileLayer.id())

                # Set LayerSet
                tileLayer.setExtent(extent)
                mapSettings.setExtent(extent)

                mapSettings.setLayers(layerSet)

            # Template
            template = os.path.dirname(__file__) + "/composer/templates/FilmDetails.qpt" #map_print_test.qpt"
            templateDom = QDomDocument()
            templateDom.setContent(QFile(template), False)

            # Composition
            composition = QgsComposition(mapSettings)
            composition.setPlotStyle(QgsComposition.Print)
            composition.setPrintResolution(300)

            # Composer Items

            composition.loadFromTemplate(templateDom, filmDict)

            # Composer Map
            if uri:
                composerMap = composition.getComposerMapById(0)
                #self.iface.messageBar().pushMessage(self.tr('WH'), "w: {0}, h: {1}".format(composerMap.rect().width(), composerMap.rect().height()), level=QgsMessageBar.INFO)
                composerMap.zoomToExtent(extent)
                #scomposerMap.resize()
                #composerMap.setOffset(0,0)
                #composerMap.updateCachedImage()
                #composerMap.renderModeUpdateCachedImage()


            # Create PDF
            composition.exportAsPDF(fileName)

            #Remove Layers
            for layerId in layerSet:
                QgsMapLayerRegistry.instance().removeMapLayer(layerId)

            # Open PDF
            if sys.platform == 'linux2':
                subprocess.call(["xdg-open", fileName])
            else:
                os.startfile(fileName)

    def exportDetailsPdf(self):
        filmId = self.uiCurrentFilmNumberEdit.text()
        saveDir = self.settings.value("APIS/working_dir", QDir.home().dirName())
        #fileName = QFileDialog.getSaveFileName(self, 'Film Details', 'c://FilmDetails_{0}'.format(self.uiCurrentFilmNumberEdit.text()), '*.pdf')
        fileName = QFileDialog.getSaveFileName(self, 'Film Details', saveDir + "\\" + 'Filmdetails_{0}_{1}'.format(filmId ,QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")), '*.pdf')

        if fileName:
            #QMessageBox.warning(None, "Save", fileName)
            #FIXME template from Settings ':/plugins/APIS/icons/settings.png'
            #template = 'C:/Users/Johannes/.qgis2/python/plugins/APIS/composer/templates/FilmDetails.qpt'
            template = os.path.dirname(__file__) + "/composer/templates/FilmDetails.qpt"
            #if os.path.isfile(template):
            templateDOM = QDomDocument()
            templateDOM.setContent(QFile(template), False)

            #FIXME load correct Flightpath; from Settings
            printLayers = []
            flightpathDir = self.settings.value("APIS/flightpath_dir")
            #uri = flightpathDir + "\\" + self.uiFlightDate.date().toString("yyyy") + "\\" + filmId + "_lin.shp"
            uri = flightpathDir + "\\2014\\02140301_lin.shp"
            printLayer = QgsVectorLayer(uri, "FlightPath", "ogr")
            #printLayer.setCrs(QgsCoordinateReferenceSystem(3857, QgsCoordinateReferenceSystem.EpsgCrsId))
            printLayer.setCrs(QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId))
            printLayer.setCoordinateSystem()
            symbol = QgsLineSymbolV2.createSimple({'color':'orange', 'line_width':'0.25'})
            printLayer.rendererV2().setSymbol(symbol)
            QgsMapLayerRegistry.instance().addMapLayer(printLayer, False) #False = don't add to Layers (TOC)
            e = printLayer.extent()
            #self.iface.messageBar().pushMessage(self.tr('Extent'), e.asWktPolygon(), level=QgsMessageBar.INFO)

            eGeo = QgsGeometry.fromRect(e)
            gt = QgsCoordinateTransform(QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId), QgsCoordinateReferenceSystem(3857, QgsCoordinateReferenceSystem.EpsgCrsId))
            eGeo.transform(gt)
            #self.iface.messageBar().pushMessage(self.tr('Extent'), eGeo.exportToWkt(), level=QgsMessageBar.INFO)
            extent = eGeo.boundingBox()

            #layerset.append(printLayer.id())
            printLayers.append(printLayer.id())

            ds = {}
            #ds['type'] = 'TMS'
            #ds['alias'] = 'Bing'
            #ds['copyright_text'] = 'Bing'
            #ds['copyright_url'] = 'http://www.virtualearth.net'
            #ds['tms_url'] = "http://ecn.t3.tiles.virtualearth.net/tiles/a{q}.jpeg?g=0&dir=dir_n'"


            ds['type'] = 'TMS'
            ds['alias'] = 'MapBox Gray'
            ds['copyright_text'] = 'MapBox'
            ds['copyright_url'] = 'http://www.mapbox.com'
            ds['tms_url'] = "https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}"

            #service_info = TileServiceInfo('Bing', 'Bing', ds['tms_url'])
            service_info = TileServiceInfo('MapBox', 'MapBox', ds['tms_url'])
            service_info.zmin = 0
            service_info.zmax = 20
            #if ds.tms_y_origin_top is not None:
            #    service_info.yOriginTop = ds.tms_y_origin_top
            service_info.epsg_crs_id = None
            service_info.postgis_crs_id = None
            service_info.custom_proj = None
            service_info.bbox = BoundingBox(-180, -85.05, 180, 85.05)
            layer = TileLayer(self, service_info, False)
            #layer.setExtent(QgsRectangle(-50,-50,50,50))
            layer.setCrs(QgsCoordinateReferenceSystem(3857, QgsCoordinateReferenceSystem.EpsgCrsId))
            #layer.setExtent(extent)
            #layer.setExtent(QgsRectangle(1700000.0, 6000000.0, 2000000.0, 6170000.0))
            #extent = layer.extent()
            #self.iface.messageBar().pushMessage(self.tr('Extent'), extent.asWktPolygon(), level=QgsMessageBar.INFO)
            if not layer.isValid():
                error_message = self.tr('Layer %s can\'t be added to the map!') % ds['alias']
                self.iface.messageBar().pushMessage(self.tr('Error'),
                                                   error_message,
                                                   level=QgsMessageBar.CRITICAL)
                QgsMessageLog.logMessage(error_message, level=QgsMessageLog.CRITICAL)
            else:
                # Set attribs
                layer.setAttribution(ds['copyright_text'])
                layer.setAttributionUrl(ds['copyright_url'])
                # Insert to bottom
                QgsMapLayerRegistry.instance().addMapLayer(layer, False)
                #toc_root = QgsProject.instance().layerTreeRoot()
                #toc_root.insertLayer(len(toc_root.children()), layer)
                # Save link
                #self.service_layers.append(layer)
                # Set OTF CRS Transform for map
                #if PluginSettings.enable_otf_3857() and ds.type == KNOWN_DRIVERS.TMS:
                #self.iface.mapCanvas().setCrsTransformEnabled(True)
                #self.iface.mapCanvas().setDestinationCrs(TileLayer.CRS_3857)
                printLayers.append(layer.id())

            #printLayers.append(printLayer.id())

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
            #ms.setExtent(extent)
            #self.iface.messageBar().pushMessage(self.tr('Extent'), ms.extent().asWktPolygon(), level=QgsMessageBar.INFO)
            ms.setLayers(printLayers)

            #mapRectangle = QgsRectangle(140,-28,155,-15)
            #mr.setExtent(extent)

            comp = QgsComposition(ms)
            comp.setPlotStyle(QgsComposition.Print)
            comp.setPrintResolution(300)

            m = self.mapper.model()
            r = self.mapper.currentIndex()
            filmDict = {}
            for c in range(m.columnCount()):
                val = unicode(m.data(m.createIndex(r, c)))
                if val.replace(" ", "")=='' or val=='NULL':
                    val = u"---"

                filmDict[m.headerData(c, Qt.Horizontal)] = val




                #QMessageBox.warning(None, "Save", "{0}:{1}".format(colName, value))

            filmDict['wetter_description'] = self._generateWeatherCode(filmDict['wetter'])
            filmDict['datum_druck'] =  QDate.currentDate().toString("yyyy-MM-dd")

            comp.loadFromTemplate(templateDOM, filmDict)

            composerMap = comp.getComposerMapById(0)
            composerMap.setUpdatesEnabled(True)
            composerMap.zoomToExtent(extent)

            #composerMap.setNewExtent(extent)
            #self.iface.messageBar().pushMessage(self.tr('Scale'), "{0}".format(composerMap.scale()), level=QgsMessageBar.INFO)
            #composerMap.setNewScale(1000000)

            #composerMap.setKeepLayerSet(True)
            #composerMap.setLayerSet(printLayers)
            #composerMap.renderModeUpdateCachedImage()
            #ms.setLayers(printLayers)

           # if composerMap:
            #    QMessageBox.warning(None, "Save", composerMap)
           #composerMap.setKeepLayerSet(True)
            #composerMap.setLayerSet(layerset)



            comp.exportAsPDF(fileName)
            # Delete all layers (array)
            for lid in printLayers:
                QgsMapLayerRegistry.instance().removeMapLayer(lid)

            if sys.platform == 'linux2':
                subprocess.call(["xdg-open", fileName])
            else:
                os.startfile(fileName)
            #else:
            #    QMessageBox.warning(None, "Save", "QGIS Template File Not Correct!")


    def openSearchFilmDialog(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.searchFilmDlg.show()
        #self.filmSelectionDlg.uiFilmNumberEdit.setFocus()
        # Run the dialog event loop and See if OK was pressed
        if self.searchFilmDlg.exec_():
            # QMessageBox.warning(None, "FilmNumber", self.searchFilmDlg.generateSearchQuery())
            model = QSqlRelationalTableModel(self, self.dbm.db)
            model.setTable("film")
            model.setFilter(self.searchFilmDlg.generateSearchQuery())
            model.select()
            while (model.canFetchMore()):
                model.fetchMore()

            if model.rowCount():
                # open film selection list dialog
                searchListDlg = ApisFilmSelectionListDialog(self.iface, model, self.dbm, self.imageRegistry, self)
                if searchListDlg.exec_():
                    #QMessageBox.warning(None, "FilmNumber", unicode(searchListDlg.filmNumberToLoad))
                    self.loadRecordByKeyAttribute("filmnummer", searchListDlg.filmNumberToLoad)
            else:
                QMessageBox.warning(None, u"Film Suche", u"Keine Ergebnisse mit den angegebenen Suchkriterien.")
                self.openSearchFilmDialog()
            # QMessageBox.warning(None, "FilmNumber", u"{0}, rows: {1}".format(self.searchFilmDlg.generateSearchQuery(), model.rowCount()))

            # Get Search String/Query
            #if not self.loadRecordByKeyAttribute("filmnummer", self.filmSelectionDlg.filmNumber()):
                #self.openFilmSelectionDialog()

    def openFilmSelectionDialog(self):
        """Run method that performs all the real work"""
        self.filmSelectionDlg.show()
        self.filmSelectionDlg.uiFilmNumberEdit.setFocus()
        if self.filmSelectionDlg.exec_():
            if not self.loadRecordByKeyAttribute("filmnummer", self.filmSelectionDlg.filmNumber()):
                self.openFilmSelectionDialog()


    def openNewFilmDialog(self):
        """Run method that performs all the real work"""
        self.newFilmDlg.show()
        if self.newFilmDlg.exec_():
            self.addNewFilm(self.newFilmDlg.flightDate(), self.newFilmDlg.useLastEntry(), self.newFilmDlg.producer(), self.newFilmDlg.producerCode())

    def openEditWeatherDialog(self):
        self.editWeatherDlg.setWeatherCode(self.uiWeatherCodeEdit.text())
        self.editWeatherDlg.show()

        if self.editWeatherDlg.exec_():
            self.uiWeatherCodeEdit.setText(self.editWeatherDlg.weatherCode())
            #self.uiWeatherPTxt.setPlainText(self.editWeatherDlg.weatherDescription())

    def generateWeatherCode(self):
        weatherDescription = self._generateWeatherCode(self.uiWeatherCodeEdit.text())
        self.uiWeatherPTxt.setPlainText(weatherDescription)

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

    def openViewFlightPathDialog(self, filmList, toClose=None):
        self.viewFlightPathDlg.viewFilms(filmList)
        self.viewFlightPathDlg.show()

        if self.viewFlightPathDlg.exec_():
            #TODO load Data in TOC, Close Windows
            if toClose:
                toClose.close()
            self.close()

    def openSiteSelectionListDialog(self):
        if self.uiFilmModeCombo.currentText() == u"senk.":
            fromTable = "luftbild_senk_fp"
        elif self.uiFilmModeCombo.currentText() == u"schräg":
            fromTable = "luftbild_schraeg_fp"
        else:
            #FIXME Introduce Error System
            sys.exit()
        query = QSqlQuery(self.dbm.db)
        query.prepare("SELECT fundortnummer, flurname, katastralgemeinde, fundgewinnung, sicherheit FROM fundort WHERE fundortnummer IN (SELECT DISTINCT fo.fundortnummer FROM fundort fo, {0} WHERE fo.geometry IS NOT NULL AND {0}.geometry IS NOT NULL AND {0}.filmnummer = '{1}' AND Intersects({0}.geometry, fo.geometry) AND fo.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'fundort' AND search_frame = {0}.geometry)) ORDER BY katastralgemeindenummer, land, fundortnummer_nn".format(fromTable, self.uiCurrentFilmNumberEdit.text()))
        query.exec_()
        info = u"gefunden, die vom Film {0} abgedeckt/geschnitten werden.".format(self.uiCurrentFilmNumberEdit.text())
        res = self.siteSelectionListDlg.loadSiteListBySpatialQuery(query, info)
        if res:
            self.siteSelectionListDlg.show()
            if self.siteSelectionListDlg.exec_():
                pass

    def openImageSelectionListDialog(self):
        res = self.imageSelectionListDlg.loadImageListByFilm(self.uiCurrentFilmNumberEdit.text(), self.uiFilmModeCombo.lineEdit().text())
        if res:
            self.imageSelectionListDlg.show()
            if self.imageSelectionListDlg.exec_():
                pass

    def addNewFilm(self, flightDate, useLastEntry, producer, producerCode):
        self.initalLoad = True
        self.addMode = True
        self.startEditMode()
        row = self.model.rowCount()
        self.mapper.submit()
        while (self.model.canFetchMore()):
            self.model.fetchMore()

        self.model.insertRow(row)

        if useLastEntry:
            #copy last row
            for c in range(self.model.columnCount()):
                value = self.model.data(self.model.createIndex(row-1, c))
                self.model.setData(self.model.createIndex(row,c), value)
                editor = self.mapper.mappedWidgetAt(c)

                if editor and not (value == 'NULL' or value == ''):
                    cName = editor.metaObject().className()
                    if (cName == "QLineEdit" or cName == "QDateEdit") and editor.isReadOnly():
                        pass
                    else:
                        editor.setStyleSheet("{0} {{background-color: rgb(153, 204, 255);}}".format(editor.metaObject().className()))
                        self.editorsEdited.append(editor)

        self.mapper.setCurrentIndex(row)

        self.uiTotalFilmCountLbl.setText(unicode(self.model.rowCount()))
        #self.uiFlightDate.setDate(flightDate)
        self.uiFlightQgsDate.setDate(flightDate)
        self.uiProducerEdit.setText(producer)
        self.uiArchiveCombo.lineEdit().setText(producer)
        if not useLastEntry:
            self.uiWeatherCodeEdit.setText("9990X")

        now = QDateTime.currentDateTime()
        #self.uiInitalEntryDate.setDate(now)
        self.uiInitalEntryQgsDate.setDateTime(now)
        #self.uiLastChangesDate.setDate(now)
        self.uiLastChangesQgsDate.setDateTime(now)
        self.uiFilmModeCombo.setEnabled(True)


        #Filmnummer
        hh = producerCode
        yyyy = flightDate.toString("yyyy")
        mm = flightDate.toString("MM")

        query = QSqlQuery(self.dbm.db)
        qryStr = "select max(filmnummer_nn) from film where filmnummer_hh_jjjj_mm = '{0}{1}{2}' limit 1".format(hh, yyyy, mm)
        query.exec_(qryStr)
        query.first()
        fn = query.value(0)

        if isinstance(fn, long):
            nn = str(fn + 1).zfill(2)
        else:
            nn = "01"
        self.uiCurrentFilmNumberEdit.setText("{0}{1}{2}{3}".format(hh, yyyy, mm, nn))

        self.initalLoad = False

    def removeNewFilm(self):
        self.initalLoad = True
        row = self.mapper.currentIndex()
        self.model.removeRow(row)
        self.model.submitAll()
        while (self.model.canFetchMore()):
            self.model.fetchMore()
        self.uiTotalFilmCountLbl.setText(unicode(self.model.rowCount()))
        self.mapper.toLast()
        self.initalLoad = False

    def saveEdits(self):
        # Check Mandatory fields
        flag = False
        for mEditor in self.mandatoryEditors:
            cName = mEditor.metaObject().className()
            if cName == 'QLineEdit':
                value = mEditor.text()
            elif cName == 'QComboBox':
                value = mEditor.lineEdit().text()
            if value.strip() == "":
                flag = True
                mEditor.setStyleSheet("{0} {{background-color: rgb(240, 160, 160);}}".format(cName))
                if mEditor not in self.editorsEdited:
                    self.editorsEdited.append(mEditor)
            else:
                if mEditor in self.editorsEdited:
                    mEditor.setStyleSheet("{0} {{background-color: rgb(153, 204, 255);}}".format(cName))
                #else:
                    #mEditor.setStyleSheet("")
        if flag:
            QMessageBox.warning(None, self.tr(u"Benötigte Felder Ausfüllen"), self.tr(u"Füllen Sie bitte alle Felder aus, die mit * gekennzeichnet sind."))
            return False

        #saveToModel
        currIdx = self.mapper.currentIndex()
        now = QDateTime.currentDateTime()
        #self.uiLastChangesDate.setDate(now)
        self.uiLastChangesQgsDate.setDateTime(now)

        res = self.mapper.submit()

        if not res:
            sqlError = self.mapper.model().lastError()
            QMessageBox.information(None, "Submit", u"Errpr: {0}, {1}".format(res, sqlError.text()))

        while (self.model.canFetchMore()):
            self.model.fetchMore()

        self.mapper.setCurrentIndex(currIdx)
        self.endEditMode()
        return True

    def cancelEdit(self):
        if self.editMode:
            result = QMessageBox.question(None,
                                          self.tr(u"Änderungen wurden vorgenommen!"),
                                          self.tr(u"Möchten Sie die Änerungen speichern?"),
                                          QMessageBox.Yes | QMessageBox.No ,
                                          QMessageBox.Yes)

            #save or not save
            if result == QMessageBox.Yes:
                res = self.saveEdits()
                if res:
                    return True
                else:
                    return False
            elif result == QMessageBox.No:
                if self.addMode:
                    self.removeNewFilm()

                self.mapper.setCurrentIndex(self.mapper.currentIndex())
                self.endEditMode()
                return True

    def startEditMode(self):
        self.editMode = True
        self.enableItemsInLayout(self.uiTopHorizontalLayout, False)
        self.enableItemsInLayout(self.uiBottomHorizontalLayout, False)
        self.uiOkBtn.setEnabled(False)
        self.uiSaveBtn.setEnabled(True)
        self.uiCancelBtn.setEnabled(True)
        self.editorsEdited = []

    def endEditMode(self):
        self.editMode = False
        self.addMode = False
        self.enableItemsInLayout(self.uiTopHorizontalLayout, True)
        self.enableItemsInLayout(self.uiBottomHorizontalLayout, True)
        self.uiOkBtn.setEnabled(True)
        self.uiSaveBtn.setEnabled(False)
        self.uiCancelBtn.setEnabled(False)
        for editor in self.editorsEdited:
            cName = editor.metaObject().className()
            if (cName == "QLineEdit" or cName == "QDateEdit") and editor.isReadOnly():
                editor.setStyleSheet("{0} {{background-color: rgb(218, 218, 218);}}".format(cName))
            else:
                editor.setStyleSheet("")
        self.editorsEdited = []

        self.uiFilmModeCombo.setEnabled(False)

    def showEvent(self, evnt):
        pass
        #self.model.select()
        #while (self.model.canFetchMore()):
        #    self.model.fetchMore()

class FilmDelegate(QSqlRelationalDelegate):
    def __init__(self):
       QSqlRelationalDelegate.__init__(self)

    def createEditor(self, parent, option, index):
        pass

    def setEditorData(self, editor, index):
        #QMessageBox.warning(None, "Test", str(editor.metaObject().className(index))()) + str
        value = unicode(index.model().data(index, Qt.EditRole))

        if value == 'NULL':
            value = ''

        if editor.metaObject().className() == 'QTimeEdit' and value == '':
            editor.setTime(QTime(0,0,0))
            #if value == '':
                #value ="00:00:00"
                #QMessageBox.warning(None, "Test", unicode(index.model().data(index, Qt.EditRole)))

        # elif editor.metaObject().className() == 'QDateEdit' and value == '':
        #     editor.setDate(QDate())

        elif editor.metaObject().className() == 'QgsDateTimeEdit' and value == '':
            editor.setEmpty()

        elif editor.metaObject().className() == 'QLineEdit':
            editor.setText(value)

        elif editor.metaObject().className() == 'QComboBox':
            editor.setEditText(value)

        elif editor.metaObject().className() == 'QListWidget':
            #QMessageBox.warning(None, "Test", unicode(index.model().data(index, Qt.EditRole)))
            editor.clear()
            editor.addItems(string.split(value, ";"))
        else:
            QSqlRelationalDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        #if editor.metaObject().className() == 'QLineEdit':
            #QMessageBox.warning(None, "Test", unicode(index.data(Qt.DisplayRole)) + ',' + unicode(editor.text()))
            #if unicode(index.data(Qt.DisplayRole)) != unicode(editor.text()):
            #    QMessageBox.warning(None, "Test", unicode(index.data(Qt.DisplayRole)) + ',' + unicode(editor.text()))
            #    model.setData(index, editor.text())

        if index.column() == 0: #0 ... filmnummer, 1 ... filmnummer_legacy, 2 ... filmnummer_hh_jjjj_mm, 3 ... filmnummer_nn
            QSqlRelationalDelegate.setModelData(self, editor, model, index)
            # QMessageBox.warning(None, "Test", unicode(index.column()) + editor.text())
            filmnummer = str(editor.text())
        #   model.setData(model.createIndex(index.row(), 0), filmnummer) #filmnummer
            mil = ""
            if filmnummer[2:4] == "19":
                mil = "01"
            elif filmnummer[2:4] == "20":
                mil = "02"
            model.setData(model.createIndex(index.row(), 1), mil + filmnummer[4:]) # filmnummer_legacy
            model.setData(model.createIndex(index.row(), 2), filmnummer[:8])  # filmnummer_hh_jjjj_mm
            model.setData(model.createIndex(index.row(), 3), int(filmnummer[-2:])) # filmnummer_nn
        elif editor.metaObject().className() == 'QgsDateTimeEdit':
            model.setData(index, editor.dateTime().toString("yyyy-MM-dd"))
        elif editor.metaObject().className() == 'QDateEdit':
            model.setData(index, editor.date().toString("yyyy-MM-dd"))
        elif editor.metaObject().className() == 'QTimeEdit':
            model.setData(index, editor.time().toString("HH:mm:ss"))
        elif editor.metaObject().className() == 'QListWidget':
            items = []
            for j in xrange(editor.count()):
                items.append(editor.item(j))
            model.setData(index, ";".join([i.text() for i in items]))
        #elif (editor.metaObject().className() == 'QLineEdit' and editor.text()==''):
        #    model.setData(model.createIndex(index.row(), 0), None)
        #elif (editor.metaObject().className() == 'QComboBox' and editor.currentText()==''):
        #    model.setData(model.createIndex(index.row(), 0), None)
        else:
            #QMessageBox.information(None, )
            QSqlRelationalDelegate.setModelData(self, editor, model, index)

# class DependDelegate(QSqlRelationalDelegate):
#     def __init__(self):
#        QSqlRelationalDelegate.__init__(self)
#
#     def createEditor(self, parent, option, index):
#         pass
#
#     def setEditorData(self, editor, index):
#         editor.setText(unicode(index.model().data(index, Qt.DisplayRole)))
#
#     def setModelData(self, editor, model, index):
#         pass
#
#
# class DropBoxDelegate(QStyledItemDelegate):
#     def __init__(self):
#         QStyledItemDelegate.__init__(self)
#
#     def createEditor(self, parent, option, index):
#         pass
#
#     def setEditorData(self, editor, index):
#         QMessageBox.warning(None, "Test", unicode(index.model().data(index, Qt.DisplayRole)))
#         pass
#
#     def setModelData(self, editor, model, index):
#         QMessageBox.warning(None, "Test", editor.text())
#         pass

class InListValidator(QValidator):
        def __init__(self, itemList, editor, depend, parent):
            QValidator.__init__(self, parent)

            self.itemList = itemList
            self.editor = editor
            self.depend = depend

        def validate(self, s, pos):

            if unicode(s) in self.itemList or unicode(s).strip()=='':
                if self.depend and unicode(s).strip()=='':
                    for dep in self.depend:
                        for key, value in dep.iteritems():
                            value.setText("")
                return (QValidator.Acceptable, s, pos)

            return (QValidator.Invalid, "", pos)


        def fixup(self, s):
            #QMessageBox.warning(None, "Test", unicode(s))
            self.editor.setText("")
