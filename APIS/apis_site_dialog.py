# -*- coding: utf-8 -*

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from PyQt4.QtXml import *
from qgis.core import *
from qgis.gui import QgsMapCanvas, QgsMapCanvasLayer

from apis_db_manager import *
from apis_film_number_selection_dialog import *
from apis_new_film_dialog import *
from apis_edit_weather_dialog import *
from apis_search_film_dialog import *
from apis_film_selection_list_dialog import *
from apis_view_flight_path_dialog import *
from apis_image_selection_list_dialog import *
from apis_site_selection_list_dialog import *
from apis_text_editor_dialog import *
from apis_sharding_selection_list_dialog import *
from apis_findspot_dialog import *
from apis_findspot_selection_list_dialog import *
from apis_representative_image_dialog import *
from apis_site_edit_findspot_handling_dialog import *
from apis_utils import *

from functools import partial
import subprocess
import string
import shutil
import glob

from apis_exif2points import Exif2Points

from py_tiled_layer.tilelayer import TileLayer, TileLayerType
from py_tiled_layer.tiles import TileServiceInfo, BoundingBox #, TileLayerDefinition

from py_tiled_layer_070.tilelayer import TileLayer as TileLayer070, TileLayerType as TileLayerType070
from py_tiled_layer_070.tiles import TileLayerDefinition as TileLayerDefinition070, BoundingBox as BoundingBox070#, TileServiceInfo


import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/composer")

# --------------------------------------------------------
# Fundort - Eingabe, Pflege
# --------------------------------------------------------
from apis_site_form import *

class ApisSiteDialog(QDialog, Ui_apisSiteDialog):

    #FIRST, PREV, NEXT, LAST = range(4)
    siteEditsSaved = pyqtSignal(bool)
    siteDeleted = pyqtSignal(bool)
    siteAndGeometryEditsSaved = pyqtSignal(QDialog, str, QgsGeometry, QgsGeometry, str, dict)
    siteAndGeometryEditsCanceled = pyqtSignal(QDialog)
    copyImageFinished = pyqtSignal(bool)

    def __init__(self, iface, dbm, imageRegistry, apisLayer, parent=None):
        QDialog.__init__(self, parent)
        self.iface = iface
        self.dbm = dbm
        self.imageRegistry = imageRegistry
        self.apisLayer = apisLayer

        self.setupUi(self)

        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)

        self.editMode = False
        self.addMode = False
        self.initalLoad = True
        self.geometryEditing = False
        self.isGeometryEditingSaved = False
        self.repImageLoaded = False
        self.repImagePath = None
        #self.isActive = None
        # Signals/Slot Connections
        self.rejected.connect(self.onReject)
        #self.uiButtonBox.rejected.connect(self.onReject)
        self.uiOkBtn.clicked.connect(self.onAccept)
        self.uiCancelBtn.clicked.connect(self.cancelEdit)
        self.uiSaveBtn.clicked.connect(self.saveEdits)

        self.uiPlotNumberBtn.clicked.connect(lambda: self.openTextEditor("Parzellennummer", self.uiPlotNumberEdit))
        self.uiCommentBtn.clicked.connect(lambda: self.openTextEditor("Bemerkung zur Lage", self.uiCommentEdit))

        self.uiListShardingsOfSiteBtn.clicked.connect(self.openShardingSelectionListDialog)

        self.uiFindSpotListTableV.doubleClicked.connect(self.openFindSpotDialog)

        #self.uiFilmSelectionBtn.clicked.connect(self.openFilmSelectionDialog)

        #self.uiNewFilmBtn.clicked.connect(self.openNewFilmDialog)
        #self.uiSearchFilmBtn.clicked.connect(self.openSearchFilmDialog)
        #self.uiEditWeatherBtn.clicked.connect(self.openEditWeatherDialog)
        #self.uiExportPdfBtn.clicked.connect(self.exportDetailsPdf)
        #self.uiShowFlightPathBtn.clicked.connect(partial(self.openViewFlightPathDialog, [self.uiCurrentFilmNumberEdit.text()]))
        #self.uiShowFlightPathBtn.clicked.connect(lambda: self.openViewFlightPathDialog([self.uiCurrentFilmNumberEdit.text()]))
        #self.uiListSitesOfFilmBtn.clicked.connect(self.openSiteSelectionListDialog)
        #self.uiListImagesOfFilmBtn.clicked.connect(self.openImageSelectionListDialog)
        #self.uiExtractGpsFromImagesBtn.clicked.connect(self.extractGpsFromImages)

        #self.uiWeatherCodeEdit.textChanged.connect(self.generateWeatherCode)

        # init Project Btn
        #self.uiAddProjectBtn.clicked.connect(self.addProject)
        #self.uiRemoveProjectBtn.clicked.connect(self.removeProject)
        #self.uiButtonBox.button(QDialogButtonBox.Ok).setDefault(False)
        #self.uiButtonBox.button(QDialogButtonBox.Ok).setAutoDefault(False)
        #self.uiButtonBox.button(QDialogButtonBox.Cancel).setDefault(False)
        #self.uiButtonBox.button(QDialogButtonBox.Cancel).setAutoDefault(False)

        # Setup Sub-Dialogs
        self.findSpotDlg = None
        self.shardingDlg = None
        self.findSpotHandlingDlg = None

        self.uiLoadSiteInQGisBtn.clicked.connect(self.loadSiteInQGis)
        self.uiLoadSiteInterpretationInQGisBtn.clicked.connect(self.loadSiteInterpretationInQGis)
        self.uiListImagesOfSiteBtn.clicked.connect(self.openImageSelectionListDialog)
        self.uiSelectRepresentativeImageBtn.clicked.connect(self.openRepresentativeImageDialog)
        self.uiDeleteSiteBtn.clicked.connect(self.deleteSite)
        self.uiExportPdfBtn.clicked.connect(self.exportPdf)

        self.uiAddNewFindSpotBtn.clicked.connect(self.addNewFindSpot)

        #self.setupComboBox(self.uiProjectSelectionCombo, "projekt", 0, None)
        #self.setupComboBox(self.newFilmDlg.uiProducerCombo, "hersteller", 2, None)

        # self.setupNavigation()

        #self.uiSiteMapCanvas.useImageToRender(False)
        self.uiSiteMapCanvas.setCanvasColor(Qt.white)
        self.uiSiteMapCanvas.setCrsTransformEnabled(True)
        self.uiSiteMapCanvas.setDestinationCrs(QgsCoordinateReferenceSystem(3857, QgsCoordinateReferenceSystem.EpsgCrsId))

        self.rubberBand = None
        self.siteLayerId = None

        self.copyImageFinished.connect(self.onCopyImageFinished)

        self.initalLoad = False

    def openInViewMode(self, siteNumber):
        self.initalLoad = True
        self.siteNumber = siteNumber

        # Setup site model
        self.model = QSqlRelationalTableModel(self, self.dbm.db)
        self.model.setTable("fundort")
        self.model.setFilter("fundortnummer='{0}'".format(self.siteNumber))
        res = self.model.select()
        self.setupMapper()
        self.mapper.toFirst()

        self.setupFindSpotList()

        self.loadSiteInSiteMapCanvas()

        #self.loadRepresentativeImageForSite()
        self.initalLoad = False

    def openInEditMode(self, siteNumber, newPolygon, oldPolygon, country, kgCode, kgName, siteArea):
        self.initalLoad = True
        self.siteNumber = siteNumber
        self.newPolygon = newPolygon
        self.oldPolygon = oldPolygon
        self.country = country

        self.geometryEditing = True

        # Setup site model
        self.model = QSqlRelationalTableModel(self, self.dbm.db)
        self.model.setTable("fundort")
        self.model.setFilter("fundortnummer='{0}'".format(self.siteNumber))
        res = self.model.select()
        self.setupMapper()
        self.mapper.toFirst()

        self.setupFindSpotList()

        self.loadSiteInSiteMapCanvas(newPolygon)

        self.startEditMode()
        self.initalLoad = False

        #update Editors
        if self.uiCadastralCommunityNumberEdit.text() != kgCode:
            self.uiCadastralCommunityNumberEdit.setText(kgCode)
        if self.uiCadastralCommunityEdit.text() != kgName:
            self.uiCadastralCommunityEdit.setText(kgName)
        if self.uiAreaEdit.text() != siteArea:
            self.uiAreaEdit.setText(unicode(siteArea))


    def openInAddMode(self, siteNumber, isFilmBased):
        self.initalLoad = True
        self.siteNumber = siteNumber
        self.isFilmBased = isFilmBased

        # Setup site model
        self.model = QSqlRelationalTableModel(self, self.dbm.db)
        self.model.setTable("fundort")
        self.model.setFilter("fundortnummer='{0}'".format(self.siteNumber))
        res = self.model.select()
        self.setupMapper()
        self.mapper.toFirst()

        self.setupFindSpotList()

        self.loadSiteInSiteMapCanvas()

        self.addMode = True
        self.startEditMode()

        self.initalLoad = False


    def setupMapper(self):
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
        self.mapper.setItemDelegate(SiteDelegate())

        self.mapper.setModel(self.model)

        self.mandatoryEditors = [self.uiSiteDiscoveryCombo, self.uiSiteCreationCombo, self.uiSiteReliabilityCombo]

        # LineEdits & PlainTextEdits
        self.intValidator = QIntValidator()
        self.doubleValidator = QDoubleValidator()

        self.lineEditMaps = {
            "fundortnummer": {
                "editor": self.uiSiteNumberEdit
            },
            "filmnummer_projekt": {
                "editor": self.uiProjectOrFilmEdit
            },
            "katastralgemeindenummer":{
                "editor": self.uiCadastralCommunityNumberEdit
            },
            "land":{
                "editor": self.uiCountryEdit
            },
            "katastralgemeinde":{
                "editor": self.uiCadastralCommunityEdit
            },
            "flurname":{
                "editor": self.uiFieldNameEdit
            },
            "parzellennummern":{
                "editor": self.uiPlotNumberEdit
            },
            "kommentar_lage":{
                "editor": self.uiCommentEdit
            },
            "erstmeldung_jahr":{
                "editor": self.uiFirstReportYearEdit,
                "validator": self.intValidator
            },
            "bildnummer": {
                "editor": self.uiImagesEdit
            },
            "raster": {
                "editor": self.uiRasterEdit
            },
            "ortshoehe":{
                "editor": self.uiElevationEdit,
                "validator": self.doubleValidator
            },
            "flaeche":{
                "editor": self.uiAreaEdit,
                "validator": self.doubleValidator
            },
            "literatur":{
                "editor": self.uiLiteraturePTxt
            },
            "detailinterpretation":{
                "editor": self.uiDetailinterpretationPTxt
            },
            "befund": {
                "editor": self.uiFindingsPTxt
            }
        }
        for key, item in self.lineEditMaps.items():
            self.mapper.addMapping(item["editor"], self.model.fieldIndex(key))
            if "validator" in item:
                item["editor"].setValidator(item["validator"])
            #item["editor"].textChanged.connect(partial(self.onLineEditChanged, item["editor"]))
            item["editor"].textChanged.connect(self.onLineEditChanged)

        # Date and Times
        self.mapper.addMapping(self.uiInitalEntryDate, self.model.fieldIndex("datum_ersteintrag"))
        self.mapper.addMapping(self.uiLastChangesDate, self.model.fieldIndex("datum_aenderung"))

        # ComboBox without Model
        self.mapper.addMapping(self.uiSiteReliabilityCombo, self.model.fieldIndex("sicherheit"))
        self.uiSiteReliabilityCombo.editTextChanged.connect(self.onLineEditChanged)
        self.uiSiteReliabilityCombo.setAutoCompletion(True)
        self.uiSiteReliabilityCombo.lineEdit().setValidator(InListValidator([self.uiSiteReliabilityCombo.itemText(i) for i in range(self.uiSiteReliabilityCombo.count())], self.uiSiteReliabilityCombo.lineEdit(), None, self))

        # ComboBox with Model
        self.comboBoxMaps = {
            "fundgewinnung": {
                "editor": self.uiSiteDiscoveryCombo,
                "table": "fundgewinnung",
                "modelcolumn": 0,
                "depend": None
            },
            "fundgewinnung_quelle": {
                "editor": self.uiSiteCreationCombo,
                "table": "fundgewinnung_quelle",
                "modelcolumn": 0,
                "depend": None
            }
        }
        for key, item in self.comboBoxMaps.items():
            self.mapper.addMapping(item["editor"], self.model.fieldIndex(key))
            self.setupComboBox(item["editor"], item["table"], item["modelcolumn"], item["depend"])
            item["editor"].editTextChanged.connect(self.onLineEditChanged)


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


    def setupFindSpotList(self):

        query = QSqlQuery(self.dbm.db)
        query.prepare("SELECT fundstellenummer AS 'Nummer', datierung_zeit AS 'Datierung', fundart AS 'Fundart', fundart_detail AS 'Fundart Detail' FROM fundstelle WHERE fundortnummer = '{0}'".format(self.siteNumber))
        query.exec_()

        model = QStandardItemModel()
        while query.next():
            newRow = []
            rec = query.record()
            for col in range(rec.count()):
                value = rec.value(col)
                newCol = QStandardItem(unicode(value))
                newRow.append(newCol)

            model.appendRow(newRow)

        rec = query.record()
        for col in range(rec.count()):
            model.setHeaderData(col, Qt.Horizontal, rec.fieldName(col))

        self.uiFindSpotListTableV.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.uiFindSpotListTableV.setModel(model)
        self.uiFindSpotListTableV.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.uiFindSpotListTableV.resizeColumnsToContents()
        self.uiFindSpotListTableV.resizeRowsToContents()
        self.uiFindSpotListTableV.horizontalHeader().setResizeMode(QHeaderView.Stretch)

        query.finish()


    def openFindSpotDialog(self, idx):
        findSpotNumber = self.uiFindSpotListTableV.model().item(idx.row(), 0).text()
        siteNumber = self.uiSiteNumberEdit.text()
        if self.findSpotDlg == None:
            self.findSpotDlg = ApisFindSpotDialog(self.iface, self.dbm, self.imageRegistry, self.apisLayer, self)
            self.findSpotDlg.findSpotEditsSaved.connect(self.setupFindSpotList)
            self.findSpotDlg.findSpotDeleted.connect(self.setupFindSpotList)
            if isinstance(self.parentWidget(), ApisFindSpotSelectionListDialog):
                self.findSpotDlg.findSpotEditsSaved.connect(self.updateParentTable)
                self.findSpotDlg.findSpotDeleted.connect(self.updateParentTable)
        self.findSpotDlg.openInViewMode(siteNumber, findSpotNumber)
        self.findSpotDlg.show()
        # Run the dialog event loop

        if self.findSpotDlg.exec_():
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
            # QMessageBox.warning(None, self.tr(u"Load Site"), self.tr(u"For Site: {0}".format(siteNumber)))

        self.findSpotDlg.uiDatingTimeCombo.currentIndexChanged.disconnect(self.findSpotDlg.loadPeriodContent)
        self.findSpotDlg.uiDatingPeriodCombo.currentIndexChanged.disconnect(self.findSpotDlg.loadPeriodDetailsContent)


    def openFindSpotDialogInAddMode(self, siteNumber, findSpotNumber):

        if self.findSpotDlg == None:
            self.findSpotDlg = ApisFindSpotDialog(self.iface, self.dbm, self.imageRegistry, self.apisLayer, self)
            self.findSpotDlg.findSpotEditsSaved.connect(self.setupFindSpotList)
            self.findSpotDlg.findSpotDeleted.connect(self.setupFindSpotList)
            if isinstance(self.parentWidget(), ApisFindSpotSelectionListDialog):
                self.findSpotDlg.findSpotEditsSaved.connect(self.updateParentTable)
                self.findSpotDlg.findSpotDeleted.connect(self.updateParentTable)

        self.findSpotDlg.openInAddMode(siteNumber, findSpotNumber)
        self.findSpotDlg.show()

        if self.findSpotDlg.exec_():
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
            # QMessageBox.warning(None, self.tr(u"Load Site"), self.tr(u"For Site: {0}".format(siteNumber)))

        self.findSpotDlg.uiDatingTimeCombo.currentIndexChanged.disconnect(self.findSpotDlg.loadPeriodContent)
        self.findSpotDlg.uiDatingPeriodCombo.currentIndexChanged.disconnect(self.findSpotDlg.loadPeriodDetailsContent)

    def updateParentTable(self):
        parent = self.parentWidget()
        parent.reloadTable(True)

    def getNextFindSpotNumber(self, siteNumber):
        query = QSqlQuery(self.dbm.db)
        query.prepare(u"SELECT CASE WHEN max(fundstellenummer) IS NULL THEN 1 ELSE max(fundstellenummer)+1 END AS nextFindSpot FROM fundstelle WHERE fundortnummer = '{0}'".format(siteNumber))
        res = query.exec_()
        query.first()
        return query.value(0)

    def getSiteInfo(self, siteNumber):
        query = QSqlQuery(self.dbm.db)
        query.prepare(u"SELECT parzellennummern,gkx,gky,meridian,longitude,latitude,flaeche, AsBinary(geometry) FROM fundort WHERE fundortnummer = '{0}'".format(siteNumber))
        res = query.exec_()
        query.first()
        return [query.value(0), query.value(1), query.value(2), query.value(3), query.value(4), query.value(5), query.value(6)], query.value(7)

    def addNewFindSpot(self):

        #QMessageBox.information(None, "Neue Fundstelle", "Neue Fundstelle Nummer: {0}".format(findSpotNumber))

        findSpotNumber = self.getNextFindSpotNumber(self.siteNumber)
        siteInfo, siteGeometry = self.getSiteInfo(self.siteNumber)

        query = QSqlQuery(self.dbm.db)
        query.prepare(u"INSERT INTO fundstelle(geometry,fundortnummer,fundstellenummer,parzellennummern,gkx,gky,meridian,longitude,latitude,flaeche,erstmeldung_jahr,datum_ersteintrag,datum_aenderung,aktion,aktionsdatum,aktionsuser) VALUES (GeomFromWKB(?, 4312), ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)")

        query.addBindValue(siteGeometry)
        query.addBindValue(self.siteNumber)
        query.addBindValue(findSpotNumber)

        for info in siteInfo:
            query.addBindValue(info)

        now = QDate.currentDate()
        query.addBindValue(now.toString("yyyy"))
        query.addBindValue(now.toString("yyyy-MM-dd"))
        query.addBindValue(now.toString("yyyy-MM-dd"))

        import getpass
        query.addBindValue('new')
        query.addBindValue(now.toString("yyyy-MM-dd"))
        query.addBindValue(getpass.getuser())

        res = query.exec_()
        #MessageBox.information(None, "Neue Fundstelle", "Neue Fundstelle Result: {0}, {1}".format(res, query.lastError().text()))

        query.finish()

        # load find spot layer dialog in addMode
        self.openFindSpotDialogInAddMode(self.siteNumber, findSpotNumber)

    def enableItemsInLayout(self, layout, enable):
        for i in range(layout.count()):
            if layout.itemAt(i).widget():
                layout.itemAt(i).widget().setEnabled(enable)


    def onLineEditChanged(self):
        sender = self.sender()
        if not self.editMode and not self.initalLoad:
            self.startEditMode()
        if not self.initalLoad:
            sender.setStyleSheet("{0} {{background-color: rgb(153, 204, 255);}}".format(sender.metaObject().className()))
            self.editorsEdited.append(sender)


    def onComboBoxChanged(self, editor):
        pass

    def apisLogger(self, action, fromTable, primaryKeysWhere):
        toTable = fromTable + u"_log"
        query = QSqlQuery(self.dbm.db)
        query.prepare(u"INSERT INTO {0} SELECT * FROM {1} WHERE {2}".format(toTable, fromTable, primaryKeysWhere))

        res = query.exec_()
        #QMessageBox.information(None, "SqlQuery", query.executedQuery())
        if not res:
            QMessageBox.information(None, "SqlError", query.lastError().text())
        import getpass
        query.prepare(u"UPDATE {0} SET aktion = '{1}', aktionsdatum = '{2}', aktionsuser = '{3}' WHERE rowid = (SELECT max(rowid) FROM {0})".format(toTable, action, QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss"), getpass.getuser(), primaryKeysWhere))
        res = query.exec_()
        #QMessageBox.information(None, "SqlQuery", query.executedQuery())
        if not res:
            QMessageBox.information(None, "SqlError", query.lastError().text())

    def openTextEditor(self, title, editor):
        textEditorDlg = ApisTextEditorDialog()
        textEditorDlg.setWindowTitle(title)
        textEditorDlg.setText(editor.text())
        if textEditorDlg.exec_():
            editor.setText(textEditorDlg.getText())

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
               return "ABC"
            else:
                self.show()
        else:
            self.close()


    def openShardingSelectionListDialog(self):
        #if self.shardingDlg == None:
        self.shardingDlg = ApisShardingSelectionListDialog(self.iface, self.dbm)
        siteNumber = self.uiSiteNumberEdit.text()
        self.shardingDlg.loadShardingListBySiteNumber(siteNumber)
        if self.shardingDlg.exec_():
            pass
            #self.shardingDlg = None


    def openImageSelectionListDialog(self):
        #layer = self.uiSiteMapCanvas.layers()
        layer = self.uiSiteMapCanvas.layers()[0]

        i = 0
        for feature in layer.getFeatures():
            if i == 0:
                searchGeometry = QgsGeometry.fromWkt(feature.geometry().exportToWkt())
                searchGeometry.convertToMultiType()
            else:
                searchGeometry.addPartGeometry(feature.geometry())
            i += 1

        epsg = 4312
        query = QSqlQuery(self.dbm.db)

        # LuftbildSuche
        query.prepare("select cp.bildnummer as bildnummer, cp.filmnummer as filmnummer, cp.radius as mst_radius, f.weise as weise, f.art_ausarbeitung as art from film as f, luftbild_schraeg_cp AS cp WHERE f.filmnummer = cp.filmnummer AND cp.bildnummer IN (SELECT fp.bildnummer FROM luftbild_schraeg_fp AS fp WHERE NOT IsEmpty(fp.geometry) AND Intersects(GeomFromText('{0}',{1}), fp.geometry) AND rowid IN (SELECT rowid FROM SpatialIndex WHERE f_table_name = 'luftbild_schraeg_fp' AND search_frame = GeomFromText('{0}',{1}) )) UNION ALL SELECT  cp_s.bildnummer AS bildnummer, cp_S.filmnummer AS filmnummer, cp_s.massstab, f_s.weise, f_s.art_ausarbeitung FROM film AS f_s, luftbild_senk_cp AS cp_s WHERE f_s.filmnummer = cp_s.filmnummer AND cp_s.bildnummer IN (SELECT fp_s.bildnummer FROM luftbild_senk_fp AS fp_s WHERE NOT IsEmpty(fp_s.geometry) AND Intersects(GeomFromText('{0}',{1}), fp_s.geometry) AND rowid IN (SELECT rowid FROM SpatialIndex WHERE f_table_name = 'luftbild_senk_fp' AND search_frame = GeomFromText('{0}',{1}) ) ) ORDER BY filmnummer, bildnummer".format(searchGeometry.exportToWkt(), epsg))
        query.exec_()
        imageSelectionListDlg = ApisImageSelectionListDialog(self.iface, self.dbm, self.imageRegistry)
        res = imageSelectionListDlg.loadImageListBySpatialQuery(query)
        if res:
            imageSelectionListDlg.show()
            if imageSelectionListDlg.exec_():
                pass

    # def addNewSite(self, sitePoint, sitePolygon, filmNumberOrProject, imageNumber):
    #     self.initalLoad = True
    #     self.addMode = True
    #     self.startEditMode()
    #
    #     row = self.model.rowCount()
    #     self.mapper.submit()
    #     while (self.model.canFetchMore()):
    #         self.model.fetchMore()
    #
    #     self.model.insertRow(row)
    #
    #     self.mapper.setCurrentIndex(row)
    #
    #     # Mapper Edits
    #
    #
    #     self.uiTotalFilmCountLbl.setText(unicode(self.model.rowCount()))
    #     self.uiFlightDate.setDate(flightDate)
    #     self.uiProducerEdit.setText(producer)
    #     if not useLastEntry:
    #         self.uiWeatherCodeEdit.setText("9990X")
    #
    #     now = QDate.currentDate()
    #     self.uiInitalEntryDate.setDate(now)
    #     self.uiLastChangesDate.setDate(now)
    #     self.uiFilmModeCombo.setEnabled(True)
    #
    #
    #     #Filmnummer
    #     hh = producerCode
    #     yyyy = flightDate.toString("yyyy")
    #     mm = flightDate.toString("MM")
    #
    #     query = QSqlQuery(self.dbm.db)
    #     qryStr = "select max(filmnummer_nn) from film where filmnummer_hh_jjjj_mm = '{0}{1}{2}' limit 1".format(hh, yyyy, mm)
    #     query.exec_(qryStr)
    #     query.first()
    #     fn = query.value(0)
    #
    #     if isinstance(fn, long):
    #         nn = str(fn + 1).zfill(2)
    #     else:
    #         nn = "01"
    #     self.uiCurrentFilmNumberEdit.setText("{0}{1}{2}{3}".format(hh, yyyy, mm, nn))
    #
    #     self.initalLoad = False

    def removeNewSite(self):
        self.initalLoad = True
        row = self.mapper.currentIndex()
        self.model.removeRow(row)
        self.model.submitAll()
        #while (self.model.canFetchMore()):
        #    self.model.fetchMore()
        #self.uiTotalFilmCountLbl.setText(unicode(self.model.rowCount()))
        #self.mapper.toLast()
        self.initalLoad = False

    def saveEdits(self):
        # Check Mandatory fields
        flag = False
        fSEditActions = {}
        for mEditor in self.mandatoryEditors:
            cName = mEditor.metaObject().className()
            if cName == 'QLineEdit':
                value = mEditor.text()
            elif cName == 'QComboBox':
                if mEditor.isEditable():
                    value = mEditor.lineEdit().text()
                else:
                    if mEditor.currentIndex == -1:
                        value = ''
                    else:
                        value = '1'
            if value.strip() == "":
                flag = True
                # RED
                mEditor.setStyleSheet("{0} {{background-color: rgb(240, 160, 160);}}".format(cName))
                if mEditor not in self.editorsEdited:
                    self.editorsEdited.append(mEditor)
            else:
                if mEditor in self.editorsEdited:
                    #BLUE
                    mEditor.setStyleSheet("{0} {{background-color: rgb(153, 204, 255);}}".format(cName))
                #else:
                    #mEditor.setStyleSheet("")
        if flag:
            QMessageBox.warning(None, self.tr(u"Benötigte Felder Ausfüllen"), self.tr(u"Füllen Sie bitte alle Felder aus, die mit * gekennzeichnet sind."))
            return False

        # Check if fins spots will change due to site geometry edits
        if self.geometryEditing and SiteHasFindSpot(self.dbm.db, self.siteNumber): # SiteHasFindSpot in apis_utils.py
            fSEditActions = self.openSiteEditFindSpotHandlingDialog()
            if fSEditActions == None:
                return True #Only return False if Dialog should be shown again

        #saveToModel
        currIdx = self.mapper.currentIndex()
        now = QDate.currentDate()
        self.uiLastChangesDate.setDate(now)

        if self.addMode:
            action = u"new"
        else:
            action = u"editAG" if self.geometryEditing else u"editA"
            #Update AKTION
            self.model.setData(self.model.createIndex(currIdx, self.model.fieldIndex("aktion")),action)
            self.model.setData(self.model.createIndex(currIdx, self.model.fieldIndex("aktionsdatum")), now.toString("yyyy-MM-dd"))
            import getpass
            self.model.setData(self.model.createIndex(currIdx, self.model.fieldIndex("aktionsuser")), getpass.getuser())

        self.mapper.submit()

        #emit signal
        self.siteEditsSaved.emit(True)
        if self.geometryEditing:
            self.siteAndGeometryEditsSaved.emit(self, self.siteNumber, self.newPolygon, self.oldPolygon, self.country, fSEditActions)
            self.geometryEditing = False
        else:
            # log only if not geometryEditing envolved, otherwise log in site_mapping_dialog.saveSiteEdits()
            self.apisLogger(action, u"fundort", u"fundortnummer = '{0}' ".format(self.siteNumber))

        self.mapper.setCurrentIndex(currIdx)
        self.endEditMode()

        #
        if not self.isGeometryEditingSaved:
            self.isGeometryEditingSaved = True
        return True

    def cancelEdit(self):
        currIdx = self.mapper.currentIndex()
        if self.editMode:
            if self.addMode:
                header = self.tr(u"Neuer Fundort wurden hinzugefügt!")
                question = self.tr(u"Möchten Sie den neuen Fundort speichern?")
            elif self.geometryEditing:
                header = self.tr(u"Änderungen an der Fundort Geometrie wurden vorgenommen!")
                question = self.tr(u"Möchten Sie die Änerungen der Geometrie und Attribute speichern?")
            else:
                header = self.tr(u"Änderungen wurden vorgenommen!")
                question = self.tr(u"Möchten Sie die Änerungen der Attribute speichern?")
            result = QMessageBox.question(None,
                                          header,
                                          question,
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
                if self.geometryEditing:
                    self.siteAndGeometryEditsCanceled.emit(self)
                    self.geometryEditing = False
                if self.addMode:
                    self.removeNewSite()
                    self.endEditMode()
                    self.close()
                    return True
                else:
                    self.mapper.setCurrentIndex(currIdx)
                    self.endEditMode()
                    return True

    def startEditMode(self):
        self.editMode = True
        self.uiFindSpotGrp.setEnabled(False)
        self.enableItemsInLayout(self.uiBottomHorizontalLayout, False)
        self.uiOkBtn.setEnabled(False)
        self.uiSaveBtn.setEnabled(True)
        self.uiCancelBtn.setEnabled(True)
        self.editorsEdited = []

    def endEditMode(self):
        self.editMode = False
        self.addMode = False
        self.uiFindSpotGrp.setEnabled(True)
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

    def isGeometrySaved(self):
        return self.isGeometryEditingSaved and self.geometryEditing

    #def showEvent(self, evnt):
     #   pass
        #self.model.select()
        #while (self.model.canFetchMore()):
        #    self.model.fetchMore()

    def deleteSite(self):
        # has findSpots
        findSpotCount = self.siteHasFindSpots(self.siteNumber)
        if findSpotCount:
            QMessageBox.warning(None, u"Fundort löschen", u"Der Fundort ({0}) hat {1} Fundstellen. Bitte löschen Sie diese damit Sie den Fundort löschen können.".format(self.siteNumber, findSpotCount))
            return
        else:
            # Abfrage wirklich löschen
            header = u"Fundort löschen "
            question = u"Möchten Sie den Fundort wirklich aus der Datenbank löschen?"
            result = QMessageBox.question(None,
                                          header,
                                          question,
                                          QMessageBox.Yes | QMessageBox.No,
                                          QMessageBox.Yes)

            # save or not save

            if result == QMessageBox.Yes:

                # get path from settings
                path = self.settings.value("APIS/repr_image_dir", QDir.home().dirName())
                # get filename from SQL
                repImageName = self.getRepresentativeImage(self.siteNumber)
                if repImageName:
                    path += u"\\" + repImageName + u".jpg"
                    # Check if exists
                    repImageFile = QFile(path)

                    if repImageFile.exists():
                        repImageFile.remove()

                # log eintragen
                self.apisLogger(u"delete", u"fundort", u"fundortnummer = '{0}'".format(self.siteNumber))
                # löschen
                self.model.deleteRowFromTable(self.mapper.currentIndex())

                self.siteDeleted.emit(True)
                self.iface.mapCanvas().refreshAllLayers()
                self.done(1)


    def siteHasFindSpots(self, siteNumber):
        query = QSqlQuery(self.dbm.db)
        query.prepare(u"SELECT count(*) FROM fundstelle WHERE fundortnummer = '{0}'".format(siteNumber))
        res = query.exec_()
        query.first()
        return query.value(0)


    def exportPdf(self):
        if self.siteHasFindSpots(self.siteNumber):
            msgBox = QMessageBox()
            msgBox.setWindowTitle(u'Fundort als PDF exportieren')
            msgBox.setText(u"Wählen Sie eine der folgenden Druckoptionen.".format(self.siteNumber))
            msgBox.addButton(QPushButton(u'Fundort'), QMessageBox.ActionRole)
            msgBox.addButton(QPushButton(u'Fundort und Liste der Fundstellen'), QMessageBox.ActionRole)
            msgBox.addButton(QPushButton(u'Fundort, Liste und Fundstellen im Detail'), QMessageBox.ActionRole)
            msgBox.addButton(QPushButton(u'Abbrechen'), QMessageBox.RejectRole)
            ret = msgBox.exec_()

            if ret == 0:
                self.exportSiteDetailsPdf()
            elif ret == 1:
                self.exportSiteDetailsPdf(True)
            elif ret == 2:
                return
            else:
                return
        else:
            self.exportSiteDetailsPdf()

    def exportSiteDetailsPdf(self, isTemp=False):
        saveDir = self.settings.value("APIS/working_dir", QDir.home().dirName())
        fileName = QFileDialog.getSaveFileName(self, 'Fundort Details', saveDir + "\\" + 'FundortDetails_{0}_{1}'.format(self.siteNumber,QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")),'*.pdf')

        if fileName:

            query = QSqlQuery(self.dbm.db)
            query.prepare(u"SELECT * FROM fundort WHERE fundortnummer = '{0}'".format(self.siteNumber))
            query.exec_()

            siteDict = {}
            query.seek(-1)
            while query.next():
                rec = query.record()
                for col in range(rec.count()-1): # -1 geometry wird nicht benötigt!
                    #val = unicode(rec.value(col))
                    #QMessageBox.information(None, "type", u"{0}".format(type(rec.value(col))))
                    val = u"{0}".format(rec.value(col))
                    if val.replace(" ", "") == '' or val == 'NULL':
                        val = u"---"

                    siteDict[unicode(rec.fieldName(col))] = val

                siteDict['datum_druck'] = QDate.currentDate().toString("dd.MM.yyyy")
                siteDict['datum_ersteintrag'] = QDate.fromString(siteDict['datum_ersteintrag'], "yyyy-MM-dd").toString("dd.MM.yyyy")
                siteDict['datum_aenderung'] = QDate.fromString(siteDict['datum_aenderung'], "yyyy-MM-dd").toString("dd.MM.yyyy")


                if siteDict['sicherheit'] == u"1":
                    siteDict['sicherheit'] = u"sicher"
                elif siteDict['sicherheit'] == u"2":
                    siteDict['sicherheit'] = u"wahrscheinlich"
                elif siteDict['sicherheit'] == u"3":
                    siteDict['sicherheit'] = u"fraglich"
                elif siteDict['sicherheit'] == u"4":
                    siteDict['sicherheit'] = u"kein Fundort"

                if siteDict['meridian'] == u"28":
                    siteDict['epsg_gk'] = u"31254"
                elif siteDict['meridian'] == u"31":
                    siteDict['epsg_gk'] = u"31255"
                elif siteDict['meridian'] == u"34":
                    siteDict['epsg_gk'] = u"31256"
                else:
                    siteDict['epsg_gk'] = u"---"

                siteDict['epsg_mgi'] = u"4312"

            query.prepare(u"SELECT kg.katastralgemeindenummer as kgcode, kg.katastralgemeindename as kgname, round(100*Area(Intersection(Transform(fo.geometry, 31287), kg.geometry))/Area(Transform(fo.geometry, 31287))) as percent FROM katastralgemeinden kg, fundort fo WHERE fundortnummer = '{0}' AND intersects(Transform(fo.geometry, 31287), kg.geometry) AND kg.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'katastralgemeinden' AND search_frame = Transform(fo.geometry, 31287)) ORDER  BY percent DESC".format(self.siteNumber))
            query.exec_()
            query.seek(-1)
            val = u""
            while query.next():
                rec = query.record()
                val += u"{0} {1} ({2} %)\n".format(rec.value(0), rec.value(1), rec.value(2))

            siteDict['kgs_lage'] = val
            #QMessageBox.information(None, "KGS", val)

            # MapSettings
            mapSettings = QgsMapSettings()
            mapSettings.setCrsTransformEnabled(True)
            mapSettings.setDestinationCrs(QgsCoordinateReferenceSystem(3416, QgsCoordinateReferenceSystem.EpsgCrsId))

            mapSettings.setMapUnits(QGis.UnitType(0))
            mapSettings.setOutputDpi(300)

            layerSet = []
            # Site Layer
            siteLayer = self.getSpatialiteLayer(u"fundort", u'"fundortnummer" = "{0}"'.format(self.siteNumber), u"fundort")
            siteLayer.setCrs(QgsCoordinateReferenceSystem(4312, QgsCoordinateReferenceSystem.EpsgCrsId))
            siteLayer.setCoordinateSystem()

            # TODO replace with loadNamedStyle
            siteLayer.setRendererV2(self.getSiteRenderer())

            QgsMapLayerRegistry.instance().addMapLayer(siteLayer, False)  # False = don't add to Layers (TOC)
            layerSet.append(siteLayer.id())
            extent = mapSettings.layerExtentToOutputExtent(siteLayer, siteLayer.extent())

            scaleVal = max(extent.width(), extent.height())
            baseVal = max(5000.0, scaleVal*1.1)
            #QMessageBox.information(None, "MAP", "w: {0}, h: {1}".format(extent.width(), extent.height()))
            extent.scale(baseVal/scaleVal)
            #QMessageBox.information(None, "MAP", "w: {0}, h: {1}".format(extent.width(), extent.height()))
            mapWidth = 94.0
            mapHeight = 70.0
            if (extent.width()/extent.height()) > (mapWidth/mapHeight):
                newHeight = extent.width() * mapHeight / mapWidth
                yMin = extent.center().y() - (newHeight / 2.0)
                yMax = extent.center().y() + (newHeight / 2.0)
                newRect = QgsRectangle(extent.xMinimum(), yMin, extent.xMaximum(), yMax)
                extent.combineExtentWith(newRect)
            elif (extent.width()/extent.height()) < (mapWidth/mapHeight):
                newWidth = extent.height() * mapWidth / mapHeight
                xMin = extent.center().x() - (newWidth / 2.0)
                xMax = extent.center().x() + (newWidth / 2.0)
                newRect = QgsRectangle(xMin, extent.yMinimum(), xMax, extent.yMaximum())
                extent.combineExtentWith(newRect)

            # ÖK Background
            oekLayer28 = QgsRasterLayer(self.settings.value("APIS/oek50_gk_qgis_m28"), u"OKM28")
            oekLayer28.setCrs(QgsCoordinateReferenceSystem(31254, QgsCoordinateReferenceSystem.EpsgCrsId))
            QgsMapLayerRegistry.instance().addMapLayer(oekLayer28, False)
            oekLayer28.setExtent(mapSettings.mapToLayerCoordinates(oekLayer28, extent))

            oekLayer31 = QgsRasterLayer(self.settings.value("APIS/oek50_gk_qgis_m31"), u"OKM31")
            oekLayer31.setCrs(QgsCoordinateReferenceSystem(31255, QgsCoordinateReferenceSystem.EpsgCrsId))
            QgsMapLayerRegistry.instance().addMapLayer(oekLayer31, False)
            oekLayer31.setExtent(mapSettings.mapToLayerCoordinates(oekLayer31, extent))

            oekLayer34 = QgsRasterLayer(self.settings.value("APIS/oek50_gk_qgis_m34"), u"OKM34")
            oekLayer34.setCrs(QgsCoordinateReferenceSystem(31256, QgsCoordinateReferenceSystem.EpsgCrsId))
            QgsMapLayerRegistry.instance().addMapLayer(oekLayer34, False)
            oekLayer34.setExtent(mapSettings.mapToLayerCoordinates(oekLayer34, extent))

            layerSet.append(oekLayer28.id())
            layerSet.append(oekLayer31.id())
            layerSet.append(oekLayer34.id())

            # import math
            # mapWidth = 94  # 160
            # mapHeight = 70  # 120
            # c = 40075016.6855785
            # mpW = extent.width() / mapWidth
            # mpH = extent.height() / mapHeight
            # zW = math.log(c / mpW, 2) - 8
            # zH = math.log(c / mpH, 2) - 8
            # z = math.floor(min(zW, zH)) + 2
            # # self.iface.messageBar().pushMessage(self.tr('Zoom'), "z: {0}".format(z), level=QgsMessageBar.INFO)
            #
            #
            # # Tile Layer (Background Map)
            # # TODO: Move To Settings ...
            # ds = {}
            # # ds['type'] = 'TMS'
            # ds['title'] = 'basemap.at'
            # ds['attribution'] = 'basemap.at'
            # ds['attributionUrl'] = 'http://www.basemap.at'
            # ds['serviceUrl'] = "http://maps.wien.gv.at/basemap/bmaphidpi/normal/google3857/{z}/{y}/{x}.jpeg"  #geolandbasemap "https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}"
            # ds['yOriginTop'] = 1
            # ds['zmin'] = 0
            # ds['zmax'] = int(z)
            # ds['bbox'] = BoundingBox070(-180, -85.05, 180, 85.05)
            #
            # layerDef = TileLayerDefinition070(ds['title'], ds['attribution'], ds['attributionUrl'], ds['serviceUrl'],ds['yOriginTop'], ds['zmin'], ds['zmax'], ds['bbox'])
            #
            # tileLayer = TileLayer070(layerDef, False)
            # tileLayer.setCrs(QgsCoordinateReferenceSystem(3857, QgsCoordinateReferenceSystem.EpsgCrsId))
            #
            # if not tileLayer.isValid():
            #     error_message = self.tr('Background Layer %s can\'t be added to the map!') % ds['alias']
            #     self.iface.messageBar().pushMessage(self.tr('Error'),
            #                                         error_message,
            #                                         level=QgsMessageBar.CRITICAL)
            #     QgsMessageLog.logMessage(error_message, level=QgsMessageLog.CRITICAL)
            # else:
            #     QgsMapLayerRegistry.instance().addMapLayer(tileLayer, False)
            #     layerSet.append(tileLayer.id())
            #
            # # Set LayerSet
            # tileLayer.setExtent(extent)

            mapSettings.setExtent(extent)
            mapSettings.setLayers(layerSet)

            # Template
            template = os.path.dirname(__file__) + "/composer/templates/FundortDetail.qpt"  # map_print_test.qpt"
            templateDom = QDomDocument()
            templateDom.setContent(QFile(template), False)

            # Composition
            composition = QgsComposition(mapSettings)
            composition.setPlotStyle(QgsComposition.Print)
            composition.setPrintResolution(300)

            # Composer Items
            try:
                composition.loadFromTemplate(templateDom, siteDict)
            except Exception as e:
                QMessageBox.information(None, "Error", "error: {0}".format(e))


            pageCount = 1

            adjustItemHightTxt = ["parzelle", "flur", "hoehe", "flaeche", "kommentar_lage", "kgs_lage", "befund", "literatur", "detailinterpretation"]

            for itemId in adjustItemHightTxt:
                itemTxt = composition.getComposerItemById(itemId + "Txt")
                if itemTxt:
                    fontHeight = QgsComposerUtils.fontHeightMM(itemTxt.font())
                    #oldHeight = itemTxt.rectWithFrame().height()
                    displayText = unicode(itemTxt.displayText())
                    w = itemTxt.rectWithFrame().width()
                    boxWidth = w - 2 * itemTxt.marginX()
                    lineCount = 0
                    oldLineCount = 0
                    spaceWidth = QgsComposerUtils.textWidthMM(itemTxt.font(), " ")
                    newText = u""
                    for line in displayText.splitlines():
                        lineWidth = max(1.0, QgsComposerUtils.textWidthMM(itemTxt.font(), line))
                        oldLineCount += math.ceil(lineWidth / boxWidth)
                        if lineWidth > boxWidth:
                            lineCount += 1
                            if lineCount > 1:
                                newText += u"\n"
                            accWordWidth = 0
                            wordNum = 0
                            for word in line.split():
                                wordNum += 1
                                wordWidth = QgsComposerUtils.textWidthMM(itemTxt.font(), word)
                                accWordWidth += wordWidth
                                if accWordWidth > boxWidth:
                                    if wordNum > 1:
                                        lineCount += 1
                                    if wordWidth > boxWidth:
                                        accCharWidth = 0
                                        newWord = u""
                                        for char in word:
                                            charWidth = QgsComposerUtils.textWidthMM(itemTxt.font(), char)
                                            accCharWidth += charWidth
                                            newWord += char
                                            if accCharWidth >= boxWidth - 5:
                                                #INSERT LINE BREAK
                                                lineCount += 1
                                                accCharWidth = 0
                                                newText += newWord
                                                newWord = u"\n"
                                        newText += newWord + u" "
                                        accWordWidth = accCharWidth + spaceWidth

                                    else:
                                        if wordNum > 1:
                                            newText += u"\n" + word + u" "

                                        accWordWidth = wordWidth + spaceWidth

                                else:
                                    accWordWidth += spaceWidth
                                    newText += word + u" "


                        else:
                            lineCount += 1 #math.ceil(textWidth / boxWidth)
                            if lineCount > 1:
                                newText += u"\n"
                            newText += line

                    itemTxt.setText(newText)

                    #QMessageBox.information(None, "LineCount", u"feld: {0}, old: {1}, new: {2}".format(itemId, oldLineCount, lineCount))

                    newHeight = fontHeight * (lineCount + 0.5)
                    newHeight += 2 * itemTxt.marginY() + 2

                    x = itemTxt.pos().x()
                    y = itemTxt.pos().y()
                    itemTxt.setItemPosition(x, y, w, newHeight, QgsComposerItem.UpperLeft, True, 1)



            adjustItems = ["parzelle", "flur", "hoehe", "flaeche", "kommentar_lage", "kgs_lage", "media", "befund", "literatur", "detailinterpretation"]

            bottomBorder = 30.0
            topBorder = 27.0
            i = 0
            newY = 0.0
            for itemId in adjustItems:
                itemTxt = composition.getComposerItemById(itemId + "Txt")
                itemLbl = composition.getComposerItemById(itemId +"Lbl")
                #itemBox = composition.getComposerItemById(itemId + "Box")


                if itemId == "media":
                    itemMap = composition.getComposerItemById("fundort_karte")
                    itemImg = composition.getComposerItemById("rep_luftbild")

                    y = newY + 5.0

                    itemMap.setItemPosition(itemMap.pos().x(), y, itemMap.rectWithFrame().width(), itemMap.rectWithFrame().height(), QgsComposerItem.UpperLeft, True, pageCount)
                    itemImg.setItemPosition(itemImg.pos().x(), y, itemImg.rectWithFrame().width(), itemImg.rectWithFrame().height(), QgsComposerItem.UpperLeft, True, pageCount)

                    itemMap.zoomToExtent(extent)

                    path = self.settings.value("APIS/repr_image_dir", QDir.home().dirName())
                    repImageName = self.getRepresentativeImage(self.siteNumber)
                    if repImageName:
                        path += u"\\" + repImageName + u".jpg"

                        repImageFile = QFile(path)
                        if repImageFile.exists():
                            itemImg.setPicturePath(path)

                    newY = itemImg.pos().y() + itemImg.rectWithFrame().height() + 5.0


                if itemTxt and itemLbl:

                    x = itemTxt.pos().x()
                    if i == 0:
                        y = itemTxt.pos().y()
                    else:
                        y = newY
                    w = itemTxt.rectWithFrame().width()
                    h  = itemTxt.rectWithFrame().height()
                    newY = y + h
                    if newY > composition.paperHeight() - bottomBorder:
                        pageCount += 1
                        y = topBorder
                        newY = y + newHeight
                        #copy Header
                        header = 1
                        while composition.getComposerItemById("header_{0}".format(header)):
                            self.cloneLabel(composition, composition.getComposerItemById("header_{0}".format(header)), pageCount)
                            header += 1
                        #copyFooter
                        footer = 1
                        while composition.getComposerItemById("footer_{0}".format(footer)):
                            self.cloneLabel(composition, composition.getComposerItemById("footer_{0}".format(footer)),pageCount)
                            footer += 1

                    itemTxt.setItemPosition(x, y, w, h, QgsComposerItem.UpperLeft, True, pageCount)
                    itemLbl.setItemPosition(itemLbl.pos().x(), y, itemLbl.rectWithFrame().width(), itemLbl.rectWithFrame().height(), QgsComposerItem.UpperLeft, True, pageCount)

                    i += 1

                    #if itemBox:
                        #h = (itemBox.rectWithFrame().height() - oldHeight) + newHeight
                        #itemBox.setItemPosition(itemBox.pos().x(), itemBox.pos().y(), itemBox.rectWithFrame().width(), h, QgsComposerItem.UpperLeft, True, pageCount)
            addLineAfterItems = ["lage_und_koordinaten", "kgs_lageLbl"]
            for itemId in addLineAfterItems:
                continue
            #QMessageBox.information(None, "info", u"w: {0}, h: {1}, w: {2}, h: {3}, , x: {4}, y: {5}".format(width, height, l.rectWithFrame().width(), l.rectWithFrame().height(), l.pos().x(), l.pos().y()))

            composition.setNumPages(pageCount)

            # Create PDF
            composition.exportAsPDF(fileName)

            # Open PDF
            if sys.platform == 'linux2':
                subprocess.call(["xdg-open", fileName])
            else:
                os.startfile(fileName)

    def cloneLabel(self, comp, l, pageCount):
        label = QgsComposerLabel(comp)
        label.setItemPosition(l.pos().x(), l.pos().y(), l.rectWithFrame().width(), l.rectWithFrame().height(), QgsComposerItem.UpperLeft, True, pageCount)
        label.setBackgroundEnabled(True)
        label.setBackgroundColor(QColor("#CCCCCC"))
        label.setText(l.text())
        label.setVAlign(l.vAlign())
        label.setHAlign(l.hAlign())
        label.setMarginX(l.marginX())
        label.setMarginY(l.marginY())
        label.setFont(l.font())
        comp.addItem(label)


    def loadSiteInQGis(self):

        polygon, point = self.askForGeometryType()
        if polygon or point:
            # get PolygonLayer
            siteNumber = self.uiSiteNumberEdit.text()
            subsetString = u'"fundortnummer" = "{0}"'.format(siteNumber)
            siteLayer = self.getSpatialiteLayer(u"fundort", subsetString, u"fundort polygon {0}".format(siteNumber))

            if polygon:
                # load PolygonLayer
                QgsMapLayerRegistry.instance().addMapLayer(siteLayer)

            if point:
                # generate PointLayer
                centerPointLayer = self.generateCenterPointLayer(siteLayer, u"fundort punkt {0}".format(siteNumber))
                # load PointLayer
                QgsMapLayerRegistry.instance().addMapLayer(centerPointLayer)

    def loadSiteInterpretationInQGis(self):
        siteNumber = self.uiSiteNumberEdit.text()
        country, siteNumberN = siteNumber.split(".")
        if country == u"AUT":
            kgName = u"{0} ".format(self.uiCadastralCommunityEdit.text().lower().replace(".","").replace("-", " ").replace("(","").replace(")", ""))
        else:
            kgName = ""
        ##Generate Path

        siteNumberN = siteNumberN.zfill(6)
        intBaseDir = self.settings.value("APIS/int_base_dir")
        intDir = self.settings.value("APIS/int_dir")
        shpFile = u"luftint_{0}.shp".format(siteNumberN)
        intShpPath = os.path.normpath(os.path.join(intBaseDir, country, u"{0}{1}".format(kgName, siteNumberN), intDir, shpFile))


        if os.path.isfile(intShpPath):
            #QMessageBox.information(None, u"Interpretation", intShpPath)
            msgBox = QMessageBox()
            msgBox.setWindowTitle(u'Fundort Interpretation')
            msgBox.setText(u"Für den Fundort {0} ist eine Interpretation vorhanden:".format(
                    siteNumber))
            msgBox.addButton(QPushButton(u'In QGIS laden'), QMessageBox.ActionRole)
            msgBox.addButton(QPushButton(u'Verzeichnis öffnen'), QMessageBox.ActionRole)
            msgBox.addButton(QPushButton(u'Laden und öffnen'), QMessageBox.ActionRole)
            msgBox.addButton(QPushButton(u'Abbrechen'), QMessageBox.RejectRole)
            ret = msgBox.exec_()
            if ret == 0 or ret == 2:
                # Load in QGIS
                self.apisLayer.requestShapeFile(intShpPath, epsg=None, layerName=None, groupName="Interpretationen", useLayerFromTree=True, addToCanvas=True)
            if ret == 1 or ret == 2:
                # Open Folder
                OpenFileOrFolder(os.path.dirname(intShpPath))

            if ret == 3:
                return


        else:
            msgBox = QMessageBox()
            msgBox.setWindowTitle(u'Fundort Interpretation')
            msgBox.setText(u"Für den Fundort {0} ist keine Interpretation vorhanden. Wollen Sie eine Interpretation Erstellen?".format(siteNumber))
            msgBox.addButton(QPushButton(u'Vorbereiten'), QMessageBox.ActionRole)
            msgBox.addButton(QPushButton(u'Vorbereiten und laden'), QMessageBox.ActionRole)
            msgBox.addButton(QPushButton(u'Abbrechen'), QMessageBox.RejectRole)
            ret = msgBox.exec_()

            if ret == 0 or ret == 1:
                # Create Folder Path
                intPath = os.path.normpath(os.path.join(intBaseDir, country, u"{0}{1}".format(kgName, siteNumberN), intDir))
                try:
                    os.makedirs(intPath)
                except Exception as e:
                    pass
                # Copy Dummy Template
                srcPath = os.path.normpath(os.path.join(os.path.dirname(__file__), u"master_templates"))
                template = self.settings.value("APIS/int_master_shp")
                for srcFile in glob.glob(os.path.normpath(os.path.join(srcPath, u'{0}.*'.format(template)))):
                    extension = os.path.splitext(srcFile)[1]
                    dstFile = os.path.normpath(os.path.join(intPath, u"luftint_{0}{1}".format(siteNumberN, extension)))
                    #QMessageBox.information(None, "Template", u"{0}, {1}".format(srcFile, dstFile))
                    shutil.copy(srcFile, dstFile)

                # Open Folder
                OpenFileOrFolder(intPath)
            else:
                return

            if ret == 1:
                self.apisLayer.requestShapeFile(intShpPath, epsg=None, layerName=None, groupName="Interpretationen", useLayerFromTree=True, addToCanvas=True)
                #pass
                # TODO load with ApisLayerHandling Into Group Interpretationen

        #TODO : REMOVE
        # subsetString = u'"fundortnummer" = "{0}"'.format(siteNumber)
        # siteInterpretationLayer = self.getSpatialiteLayer(u"fundort_interpretation", subsetString, u"fundort interpretation {0}".format(siteNumber))
        # count = siteInterpretationLayer.dataProvider().featureCount()
        # if count > 0:
        #     QgsMapLayerRegistry.instance().addMapLayer(siteInterpretationLayer)
        # else:
        #     QMessageBox.warning(None, u"Fundort Interpretation", u"Für den Fundort ist keine Interpretation vorhanden.")

    def askForGeometryType(self):
        # Abfrage ob Fundorte der selektierten Bilder Exportieren oder alle
        msgBox = QMessageBox()
        msgBox.setWindowTitle(u'Fundorte')
        msgBox.setText(u'Wollen Sie für den Fundort Polygon, Punkt oder beide Layer verwenden?')
        msgBox.addButton(QPushButton(u'Polygon'), QMessageBox.ActionRole)
        msgBox.addButton(QPushButton(u'Punkt'), QMessageBox.ActionRole)
        msgBox.addButton(QPushButton(u'Polygon und Punkt'), QMessageBox.ActionRole)
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

    def getSiteRenderer(self):
        # Symbology für Layer
        symbol = QgsFillSymbolV2.createSimple({})
        symbol.deleteSymbolLayer(0)  # Remove default symbol layer

        symbol_layer = QgsSimpleLineSymbolLayerV2()
        symbol_layer.setWidth(0.6)
        symbol_layer.setColor(QColor(100, 50, 140, 255))
        symbol.appendSymbolLayer(symbol_layer)

        symbol_centroid = QgsMarkerSymbolV2.createSimple({u'name': u'circle', u'color': u'210,180,200,255', u'outline_color': u'100,50,140,255', u'outline_width': u'0.4'})

        symbol_layer = QgsCentroidFillSymbolLayerV2()
        symbol_layer.setPointOnSurface(True)
        symbol_layer.setSubSymbol(symbol_centroid)
        symbol.appendSymbolLayer(symbol_layer)

        renderer = QgsSingleSymbolRendererV2(symbol)

        return renderer


    def loadSiteInSiteMapCanvas(self, polygon=None):
        siteNumber = self.uiSiteNumberEdit.text()
        uri = QgsDataSourceURI()
        uri.setDatabase(self.dbm.db.databaseName())
        uri.setDataSource('', 'fundort', 'geometry')

        siteLayer = QgsVectorLayer(uri.uri(), 'fundort {0}'.format(siteNumber), 'spatialite')
        self.siteLayerId = siteLayer.id()
        siteLayer.setSubsetString(u'"fundortnummer" = "{0}"'.format(siteNumber))

        # TODO replace with loadNamedStyle
        siteLayer.setRendererV2(self.getSiteRenderer())

        extent = siteLayer.extent()
        extent.scale(1.1)

        QgsMapLayerRegistry.instance().addMapLayer(siteLayer, False)
        canvasLayer = QgsMapCanvasLayer(siteLayer)
        layerSet = []
        layerSet.append(canvasLayer)

        # ÖK Background

        oekLayer28 = QgsRasterLayer(self.settings.value("APIS/oek50_gk_qgis_m28"), u"ok50_m28")
        oekLayer31 = QgsRasterLayer(self.settings.value("APIS/oek50_gk_qgis_m31"), u"ok50_m31")
        oekLayer34 = QgsRasterLayer(self.settings.value("APIS/oek50_gk_qgis_m34"), u"ok50_m34")

        # oekLayer.setCrs(QgsCoordinateReferenceSystem(31254, QgsCoordinateReferenceSystem.EpsgCrsId))
        QgsMapLayerRegistry.instance().addMapLayer(oekLayer28, False)
        QgsMapLayerRegistry.instance().addMapLayer(oekLayer31, False)
        QgsMapLayerRegistry.instance().addMapLayer(oekLayer34, False)
        canvasLayerBg28 = QgsMapCanvasLayer(oekLayer28)
        canvasLayerBg31 = QgsMapCanvasLayer(oekLayer31)
        canvasLayerBg34 = QgsMapCanvasLayer(oekLayer34)
        layerSet.append(canvasLayerBg28)
        layerSet.append(canvasLayerBg31)
        layerSet.append(canvasLayerBg34)

        # # Tile Layer (Background Map)
        # ds = {}
        # ds['type'] = 'TMS'
        # ds['alias'] = 'basemap'
        # ds['copyright_text'] = 'basemaop'
        # ds['copyright_link'] = 'http://www.basemap.at'
        # #ds['tms_url'] = "https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}"
        # #ds['tms_url'] = "http://maps.wien.gv.at/basemap/bmaporthofoto30cm/normal/google3857/{z}/{y}/{x}.jpeg"
        # ds['tms_url'] = "http://maps.wien.gv.at/basemap/geolandbasemap/normal/google3857/{z}/{y}/{x}.png"
        #
        # #service_info = TileServiceInfo(ds['alias'], ds['alias'], ds['tms_url'])
        # #service_info.zmin = 0
        # #service_info.zmax = 17 #int(z)
        # #if ds.tms_y_origin_top is not None:
        # #   service_info.yOriginTop = ds.tms_y_origin_top
        # #service_info.epsg_crs_id = 3857
        # #service_info.postgis_crs_id = None
        # #service_info.custom_proj = None
        # #service_info.bbox = BoundingBox(-180, -85.05, 180, 85.05)
        #
        # service_info = TileServiceInfo(ds['alias'], ds['copyright_text'], ds['tms_url'])
        # service_info.zmin = 0
        # service_info.zmax = 17
        # #if ds.tms_y_origin_top is not None:
        # #    service_info.yOriginTop = ds.tms_y_origin_top
        # service_info.epsg_crs_id = 3857
        # service_info.postgis_crs_id = None
        # service_info.custom_proj = None
        # layer = TileLayer(service_info, False)
        #
        #
        # if not layer.isValid():
        #     error_message = ('Layer %s can\'t be added to the map!') % ds['alias']
        #     self.iface.messageBar().pushMessage('Error',
        #                                    error_message,
        #                                    level=QgsMessageBar.CRITICAL)
        #     QgsMessageLog.logMessage(error_message, level=QgsMessageLog.CRITICAL)
        # else:
        #     # Set attribs
        #     layer.setAttribution(ds['copyright_text'])
        #     layer.setAttributionUrl(ds['copyright_link'])
        #     # Insert layer
        #     #toc_root = QgsProject.instance().layerTreeRoot()
        #     #position = len(toc_root.children())  # Insert to bottom if wms\tms
        #     QgsMapLayerRegistry.instance().addMapLayer(layer, False)
        #     canvasLayer2 = QgsMapCanvasLayer(layer)
        #     layerSet.append(canvasLayer2)
        #     #toc_root.insertLayer(position, layer)
        #     #self.iface.mapCanvass()
        #
        #     # Save link
        #     #service_layers.append(layer)
        #     # Set OTF CRS Transform for map
        #     #if PluginSettings.enable_otf_3857() and ds.type == KNOWN_DRIVERS.TMS:
        #     self.uiSiteMapCanvas.setCrsTransformEnabled(True)
        #     self.uiSiteMapCanvas.setDestinationCrs(TileLayer.CRS_3857)
        #     #self.iface.mapCanvas().setDestinationCrs(QgsCoordinateReferenceSystem(3857, QgsCoordinateReferenceSystem.EpsgCrsId))


        # ds = {}
        # ds['title'] = 'basemap.at'
        # ds['attribution'] = 'basemap.at'
        # ds['attributionUrl'] = 'http://www.basemap.at'
        # ds['serviceUrl'] = "http://maps.wien.gv.at/basemap/geolandbasemap/normal/google3857/{z}/{y}/{x}.png"  # "https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}"
        # ds['yOriginTop'] = 1
        # ds['zmin'] = 0
        # ds['zmax'] = 19
        # ds['bbox'] = BoundingBox(-180, -85.05, 180, 85.05)
        #layerDef = TileLayerDefinition(ds['title'], ds['attribution'], ds['attributionUrl'], ds['serviceUrl'], ds['yOriginTop'], ds['zmin'], ds['zmax'], ds['bbox'])
        #tileLayer = TileLayer(self, service_info, False)
        #tileLayer = TileLayer(layerDef, False)
        #tileLayer.setCrs(QgsCoordinateReferenceSystem(3857, QgsCoordinateReferenceSystem.EpsgCrsId))
        #tileLayer = TileLayer(service_info, 0)
        #tileLayer.setCrs(QgsCoordinateReferenceSystem(3857, QgsCoordinateReferenceSystem.EpsgCrsId))

       # if not tileLayer.isValid():
        #    QMessageBox.information(None, "TileLayer", "TileLayer Is Not Valid")
            #error_message = self.tr('Background Layer %s can\'t be added to the map!') % ds['alias']
            #self.iface.messageBar().pushMessage(self.tr('Error'),
            #                                    error_message,
            #                                    level=QgsMessageBar.CRITICAL)
            #QgsMessageLog.logMessage(error_message, level=QgsMessageLog.CRITICAL)
        #else:
            # Set Attributes
            #QMessageBox.information(None, "TileLayer", "TileLayer Is Valid")
            #tileLayer.setAttribution(ds['copyright_text'])
            #tileLayer.setAttributionUrl(ds['copyright_url'])
        #    QgsMapLayerRegistry.instance().addMapLayer(tileLayer, False)
        #    canvasLayer2 = QgsMapCanvasLayer(tileLayer)
        #    layerSet.append(canvasLayer2)


        self.uiSiteMapCanvas.setLayerSet(layerSet)
        #self.uiSiteMapCanvas.refreshAllLayers()

        if polygon:
            if self.rubberBand:
                self.uiSiteMapCanvas.scene().removeItem(self.rubberBand)
                self.rubberBand = None

            self.rubberBand = QgsRubberBand(self.uiSiteMapCanvas, QGis.Polygon)
            self.rubberBand.setWidth(1)
            self.rubberBand.setFillColor(QColor(220, 0, 0, 120))
            self.rubberBand.setBorderColor(QColor(220, 0, 0))
            self.rubberBand.setLineStyle(Qt.DotLine)
            self.rubberBand.addGeometry(polygon, siteLayer)
            self.rubberBand.show()
            extentNewPolygon = polygon.boundingBox()
            extentNewPolygon.scale(1.1)
            extent.combineExtentWith(extentNewPolygon)


        else:
            if self.rubberBand:
                self.uiSiteMapCanvas.scene().removeItem(self.rubberBand)
                self.rubberBand = None

        targetExtent = self.uiSiteMapCanvas.mapSettings().layerExtentToOutputExtent(siteLayer, extent)

        self.uiSiteMapCanvas.setExtent(targetExtent)
       # self.saveCanvasAsImage() # FIXME: DELTETE NOT NEEDED
       # self.uiSiteMapCanvas.zoomToFeatureIds(siteLayer, set([0]))

    def reloadMapCanvas(self):
        if self.rubberBand:
            self.uiSiteMapCanvas.scene().removeItem(self.rubberBand)
            self.rubberBand = None

        siteLayer = QgsMapLayerRegistry.instance().mapLayer(self.siteLayerId)
        if siteLayer:
            siteLayer.reload()
            siteLayer.updateExtents()
            extent = siteLayer.extent()
            extent.scale(1.1)
            targetExtent = self.uiSiteMapCanvas.mapSettings().layerExtentToOutputExtent(siteLayer, extent)
            self.uiSiteMapCanvas.refresh()
            self.uiSiteMapCanvas.setExtent(targetExtent)
        #self.saveCanvasAsImage()
        #self.uiSiteMapCanvas.refreshAllLayers()

    def removeSitesFromSiteMapCanvas(self):
        layers = self.uiSiteMapCanvas.layers()
        for layer in layers:
            QgsMapLayerRegistry.instance().removeMapLayer(layer.id())

    def saveCanvasAsImage(self):
        saveDir = self.settings.value("APIS/site_image_dir", QDir.home().dirName())
        # fileName = QFileDialog.getSaveFileName(self, 'Film Details', 'c://FilmDetails_{0}'.format(self.uiCurrentFilmNumberEdit.text()), '*.pdf')
        fileName = saveDir + "\\" + "Fundort_{0}.png".format(self.siteNumber)
        self.uiSiteMapCanvas.saveAsImage(fileName)

    def getRepresentativeImage(self, siteNumber):
        query = QSqlQuery(self.dbm.db)
        #query.prepare(u"SELECT CASE WHEN repraesentatives_luftbild IS NULL THEN replace(fundortnummer_legacy, '.','_') WHEN repraesentatives_luftbild ='_1' THEN replace(fundortnummer_legacy, '.','_') || '_1' ELSE repraesentatives_luftbild END as repImage FROM fundort WHERE fundortnummer = '{0}'".format(siteNumber))
        query.prepare(u"SELECT CASE WHEN repraesentatives_luftbild IS NULL THEN 0 WHEN repraesentatives_luftbild ='_1' THEN 0 ELSE repraesentatives_luftbild END as repImage FROM fundort WHERE fundortnummer = '{0}'".format(siteNumber))
        res = query.exec_()
        query.first()
        if query.value(0) == 0:
            return False
        else:
            return unicode(query.value(0))

    def getSiteNumberLegacy(self, siteNumber):
        query = QSqlQuery(self.dbm.db)
        query.prepare(u"SELECT fundortnummer_legacy FROM fundort WHERE fundortnummer = '{0}'".format(siteNumber))
        res = query.exec_()
        query.first()
        return unicode(query.value(0))

    def loadRepresentativeImageForSite(self):
        # get path from settings
        path = self.settings.value("APIS/repr_image_dir", QDir.home().dirName())
        # get filename from SQL
        self.scene = QGraphicsScene()
        self.uiSiteImageView.setScene(self.scene)
        repImageName = self.getRepresentativeImage(self.siteNumber)
        if repImageName:
            path += u"\\" + repImageName + u".jpg"
            # Check if exists
            repImageFile = QFile(path)

            if repImageFile.exists():
                self.loadImage(repImageFile.fileName())
                #QMessageBox.information(None, "FileInfo", u"True, {0}".format(repImageFile.fileName()))
            else:
                self.loadText(u"Kein repräsentatives Luftbild vorhanden ...")
        else:
            self.loadText(u"Kein repräsentatives Luftbild vorhanden ...")

        self.repImageLoaded = True

    def openRepresentativeImageDialog(self):
        repImageDlg = ApisRepresentativeImageDialog(self.dbm, self.imageRegistry, self.repImagePath, self.uiProjectOrFilmEdit.text())
        repImageDlg.show()
        if repImageDlg.exec_():
            # if new Image saved Reload Image
            #update SQL
            self.copyNewImageToDestination(repImageDlg.newPath)

    def copyNewImageToDestination(self, sourceFileName):
        destinationDir = QDir(self.settings.value("APIS/repr_image_dir"))
        #TODO RM: destinationFileName = self.getSiteNumberLegacy(self.siteNumber).replace('.', '_')
        destinationFileName = self.siteNumber.replace('.', '_')
        destinationFilePath = os.path.normpath(os.path.normpath(destinationDir.absolutePath() + "\\{0}.jpg".format(destinationFileName)))

        sourceFile = QFile(os.path.normpath(sourceFileName))
        destinationFile = QFile(os.path.normpath(destinationFilePath))

        #QMessageBox.information(None, "info", sourceFile.fileName() +"\n"+ destinationFile.fileName())

        if not sourceFile.fileName() == destinationFile.fileName():
            self.loadText(u"Repräsentatives Luftbild wird geladen ...")
            if destinationFile.exists():
                destinationFile.remove()
            copyResult = sourceFile.copy(destinationFilePath)
            sqlResult = self.saveNewFileNameInDb(destinationFileName)
            self.copyImageFinished.emit(copyResult)


    def saveNewFileNameInDb(self, repImage):
        query = QSqlQuery(self.dbm.db)
        query.prepare(u"UPDATE fundort SET repraesentatives_luftbild = '{0}' WHERE fundortnummer = '{1}'".format(repImage, self.siteNumber))
        return query.exec_()

    def onCopyImageFinished(self, result):
        #if result:
        path = self.settings.value("APIS/repr_image_dir")
        # get filename from SQL
        repImageName = self.getRepresentativeImage(self.siteNumber)
        if repImageName:
            path += u"\\" + repImageName + u".jpg"
            # Check if exists
            repImageFile = QFile(path)

            if repImageFile.exists():
                self.loadImage(repImageFile.fileName())
                # QMessageBox.information(None, "FileInfo", u"True, {0}".format(repImageFile.fileName()))
            else:
                self.loadText(u"Kein repräsentatives Luftbild vorhanden ...")
        else:
            self.loadText(u"Kein repräsentatives Luftbild vorhanden ...")

    def loadImage(self, path):
        self.repImagePath = path
        self.scene.clear()
        image = QImage(path)
        size = image.size()
        self.rect = QRectF(0, 0, size.width(), size.height())
        self.scene.addPixmap(QPixmap.fromImage(image))
        self.scene.setSceneRect(self.rect)
        self.uiSiteImageView.fitInView(self.rect, Qt.KeepAspectRatio)

    def loadText(self, text):
        self.repImagePath = None
        # QMessageBox.information(None, "FileInfo", u"False, {0}".format(repImageFile.fileName()))
        self.scene.clear()
        noImageTxt = QGraphicsTextItem()
        noImageTxt.setPlainText(text)
        self.rect = noImageTxt.boundingRect()
        self.scene.addItem(noImageTxt)
        self.scene.setSceneRect(self.rect)
        self.uiSiteImageView.fitInView(self.rect, Qt.KeepAspectRatio)


    def openSiteEditFindSpotHandlingDialog(self):
        if self.findSpotHandlingDlg == None:
            self.findSpotHandlingDlg = ApisSiteEditFindSpotHandlingDialog(self.iface, self.dbm, {self.siteNumber: [self.newPolygon, self.oldPolygon, self.newPolygon.buffer(0.0001, 12)]})
        res = self.findSpotHandlingDlg.exec_()
        if res:
            # fortfahren, get desissions made ...
            #QMessageBox.information(None, u"FO Updates", u"Fortfahren")
            actions = self.findSpotHandlingDlg.getActions()
            return actions
        else:
            # cancel all edits and close dialog
            # QMessageBox.information(None, u"FO Updates", u"Abbrechen")
            return None


    def showEvent(self, event):
        self.loadRepresentativeImageForSite()
        #self.isActive = True
        if self.addMode and self.isFilmBased:
            self.openRepresentativeImageDialog()


    def resizeEvent(self, event):
        if self.repImageLoaded:
            self.uiSiteImageView.fitInView(self.rect, Qt.KeepAspectRatio)


class SiteDelegate(QSqlRelationalDelegate):
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

        elif editor.metaObject().className() == 'QLineEdit':
            editor.setText(value)

        elif editor.metaObject().className() == 'QComboBox':
            if index.column() == 25: #sicherheit
                if value == '':
                    editor.setCurrentIndex(-1)
                else:
                    editor.setCurrentIndex(int(value)-1)
            else:
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


        if editor.metaObject().className() == 'QDateEdit':
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
        elif editor.metaObject().className() == 'QComboBox':
            if index.column() == 25: #sicherheit
                model.setData(index, editor.currentIndex()+1)
            else:
                model.setData(index, editor.currentText())
        else:
            QSqlRelationalDelegate.setModelData(self, editor, model, index)

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
