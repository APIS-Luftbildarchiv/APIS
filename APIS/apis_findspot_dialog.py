# -*- coding: utf-8 -*

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from PyQt4.QtXml import *
from qgis.core import *
from qgis.gui import QgsMapCanvas, QgsMapCanvasLayer

from apis_db_manager import *
from apis_view_flight_path_dialog import *
from apis_site_dialog import *
from apis_text_editor_dialog import *
from apis_sharding_selection_list_dialog import *
from apis_findingtype_detail_dialog import *

from functools import partial
import subprocess
import string
import math
from apis_exif2points import Exif2Points


import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/composer")

# --------------------------------------------------------
# Fundort - Eingabe, Pflege
# --------------------------------------------------------
from apis_findspot_form import *

class ApisFindSpotDialog(QDialog, Ui_apisFindSpotDialog):

    #FIRST, PREV, NEXT, LAST = range(4)
    findSpotEditsSaved = pyqtSignal(bool)
    findSpotDeleted = pyqtSignal(bool)

    def __init__(self, iface, dbm, imageRegistry, parent=None):
        QDialog.__init__(self, parent)
        self.iface = iface
        self.dbm = dbm
        self.imageRegistry = imageRegistry

        self.setupUi(self)

        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)

        self.editMode = False
        self.addMode = False
        self.initalLoad = True
        self.geometryEditing = False
        self.isGeometryEditingSaved = False
        # Signals/Slot Connections
        self.rejected.connect(self.onReject)
        #self.uiButtonBox.rejected.connect(self.onReject)
        self.uiOkBtn.clicked.connect(self.onAccept)
        self.uiCancelBtn.clicked.connect(self.cancelEdit)
        self.uiSaveBtn.clicked.connect(self.saveEdits)

        self.uiPlotNumberBtn.clicked.connect(lambda: self.openTextEditor("Parzellennummer", self.uiPlotNumberEdit))
        self.uiCommentBtn.clicked.connect(lambda: self.openTextEditor("Bemerkung zur Lage", self.uiCommentEdit))
        self.uiFindingTypeDetailBtn.clicked.connect(self.openFindingTypeDetailDialog)

        self.uiLoadFindSpotInQGisBtn.clicked.connect(self.loadFindSpotInQGis)
        self.uiListShardingsOfSiteBtn.clicked.connect(self.openShardingSelectionListDialog)
        self.uiCloneFindSpotBtn.clicked.connect(self.cloneFindSpot)
        self.uiDeleteFindSpotBtn.clicked.connect(self.deleteFindSpot)
        self.uiExportPdfBtn.clicked.connect(self.exportDetailsPdf)


        self.uiViewSiteBtn.clicked.connect(self.openSiteDialog)

        self.uiDatingTimeCombo.editTextChanged.connect(self.onLineEditChanged)
        self.uiDatingPeriodCombo.editTextChanged.connect(self.onLineEditChanged)
        self.uiDatingPeriodDetailCombo.editTextChanged.connect(self.onLineEditChanged)



        # Setup Sub-Dialogs

        self.initalLoad = False

    def openInViewMode(self, siteNumber, findSpotNumber):
        self.initalLoad = True
        self.siteNumber = siteNumber
        self.findSpotNumber = findSpotNumber

        # Setup site model
        self.model = QSqlRelationalTableModel(self, self.dbm.db)
        self.model.setTable("fundstelle")
        self.model.setFilter("fundortnummer='{0}' AND fundstellenummer={1}".format(self.siteNumber, self.findSpotNumber))
        res = self.model.select()

        #QMessageBox.warning(None, "Funstellen Row Count", u"{0}".format(self.model.rowCount()))
        self.setupMapper()
        self.mapper.toFirst()

        #QMessageBox.warning(None, "Mapper", u"period detail: {0}".format(self.uiDatingPeriodDetailCombo.lineEdit().text()))

        query = u"SELECT DISTINCT {0} FROM {0}".format("zeit")
        self.setupComboBoxByQuery(self.uiDatingTimeCombo, query)
        self.loadPeriodContent(0)
        self.loadPeriodDetailsContent(0)
        self.uiDatingTimeCombo.currentIndexChanged.connect(self.loadPeriodContent)
        self.uiDatingPeriodCombo.currentIndexChanged.connect(self.loadPeriodDetailsContent)

        self.initalLoad = False




        #self.setupFindSpotList()

    def openInAddMode(self, siteNumber, findSpotNumber):
        self.initalLoad = True
        self.siteNumber = siteNumber
        self.findSpotNumber = findSpotNumber

        # Setup site model
        self.model = QSqlRelationalTableModel(self, self.dbm.db)
        self.model.setTable("fundstelle")
        self.model.setFilter("fundortnummer='{0}' AND fundstellenummer={1}".format(self.siteNumber, self.findSpotNumber))
        res = self.model.select()

        #QMessageBox.warning(None, "Funstellen Row Count", u"{0}".format(self.model.rowCount()))
        self.setupMapper()
        self.mapper.toFirst()

        #QMessageBox.warning(None, "Mapper", u"period detail: {0}".format(self.uiDatingPeriodDetailCombo.lineEdit().text()))

        query = u"SELECT DISTINCT {0} FROM {0}".format("zeit")
        self.setupComboBoxByQuery(self.uiDatingTimeCombo, query)
        self.loadPeriodContent(0)
        self.loadPeriodDetailsContent(0)
        self.uiDatingTimeCombo.currentIndexChanged.connect(self.loadPeriodContent)
        self.uiDatingPeriodCombo.currentIndexChanged.connect(self.loadPeriodDetailsContent)

        self.addMode = True
        self.startEditMode()

        self.initalLoad = False

    # def openInEditMode(self, siteNumber, kgCode, kgName, siteArea):
    #     self.initalLoad = True
    #     self.siteNumber = siteNumber
    #     self.geometryEditing = True
    #
    #     # Setup site model
    #     self.model = QSqlRelationalTableModel(self, self.dbm.db)
    #     self.model.setTable("fundort")
    #     self.model.setFilter("fundortnummer='{0}'".format(self.siteNumber))
    #     res = self.model.select()
    #     self.setupMapper()
    #     self.mapper.toFirst()
    #
    #     self.startEditMode()
    #     self.initalLoad = False
    #
    #     #update Editors
    #     if self.uiCadastralCommunityNumberEdit.text() != kgCode:
    #         self.uiCadastralCommunityNumberEdit.setText(kgCode)
    #     if self.uiCadastralCommunityEdit.text() != kgName:
    #         self.uiCadastralCommunityEdit.setText(kgName)
    #     if self.uiAreaEdit.text() != siteArea:
    #         self.uiAreaEdit.setText(unicode(siteArea))


    # def openInAddMode(self, siteNumber):
    #     self.initalLoad = True
    #     self.siteNumber = siteNumber
    #
    #     # Setup site model
    #     self.model = QSqlRelationalTableModel(self, self.dbm.db)
    #     self.model.setTable("fundort")
    #     self.model.setFilter("fundortnummer='{0}'".format(self.siteNumber))
    #     res = self.model.select()
    #     self.setupMapper()
    #     self.mapper.toFirst()
    #
    #     self.addMode = True
    #     self.startEditMode()
    #
    #     self.initalLoad = False



    def setupMapper(self):
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
        self.mapper.setItemDelegate(FindSpotDelegate())

        self.mapper.setModel(self.model)

        self.mandatoryEditors = [self.uiCaseWorkerEdit, self.uiFindSpotCreationCombo, self.uiSiteReliabilityCombo, self.uiDatingTimeCombo, self.uiDatingPeriodCombo, self.uiDatingPeriodDetailCombo, self.uiFindingTypeCombo]

        # LineEdits & PlainTextEdits
        self.intValidator = QIntValidator()
        self.doubleValidator = QDoubleValidator()

        self.uiFindSpotNumberEdit.setText("{0}.{1}".format(self.siteNumber, self.findSpotNumber))
        # From fundort: KG Nummer, KG Name, Flurname
        query = QSqlQuery(self.dbm.db)
        query.prepare("SELECT katastralgemeindenummer, katastralgemeinde, flurname FROM fundort WHERE fundortnummer = '{0}'".format(self.siteNumber))
        query.exec_()
        query.first()

        self.uiCadastralCommunityNumberEdit.setText(unicode(query.value(0)))
        self.uiCadastralCommunityEdit.setText(unicode(query.value(1)))
        self.uiFieldNameEdit.setText(unicode(query.value(2) if query.value(2) == 'NULL' else '' ))

        self.lineEditMaps = {
            "bearbeiter": {
                "editor": self.uiCaseWorkerEdit
            },
            "erstmeldung_jahr": {
                "editor": self.uiFirstReportYearEdit,
                "validator": self.intValidator
            },
            "erhaltung": {
                "editor": self.uiPreservationStateEdit
            },
            "parzellennummern": {
                "editor": self.uiPlotNumberEdit
            },
            "bdanummer": {
                "editor": self.uiBdaNumberEdit
            },
            "kommentar_lage": {
                "editor": self.uiCommentEdit
            },
            "flaeche": {
                "editor": self.uiAreaEdit,
                "validator": self.doubleValidator
            },
            "datum_abs_1": {
               "editor": self.uiAbsoluteDatingFromEdit
            },
            "datum_abs_2": {
                "editor": self.uiAbsoluteDatingToEdit
            },
            "fundart_detail":{
                "editor": self.uiFindingTypeDetailEdit
            },
            "literatur":{
                "editor": self.uiLiteraturePTxt
            },
            "fundbeschreibung":{
                "editor": self.uiFindingsPTxt
            },
            "fundverbleib": {
                "editor": self.uiFindingsStoragePTxt
            },
            "sonstiges": {
                "editor": self.uiMiscellaneousPTxt
            },
            "fundgeschichte": {
                "editor": self.uiFindingsHistoryPTxt
            },
            "befund": {
                "editor": self.uiFindingsInterpretationPTxt
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
            "fundgewinnung_quelle": {
                "editor": self.uiFindSpotCreationCombo,
                "table": "fundgewinnung_quelle",
                "modelcolumn": 0,
                "justshowcolumn": True,
                "depend": None
            },
            # "datierung_zeit": {
            #     "editor": self.uiDatingTimeCombo,
            #     "table": "zeit",
            #     "modelcolumn": 0,
            #     "justshowcolumn": True,
            #     "depend": None
            # },
            # "datierung_periode": {
            #     "editor": self.uiDatingPeriodCombo,
            #     "table": "zeit",
            #     "modelcolumn": 1,
            #     "justshowcolumn": True,
            #     "depend": None
            # },
            # "datierung_periode_detail": {
            #     "editor": self.uiDatingPeriodDetailCombo,
            #     "table": "zeit",
            #     "modelcolumn": 2,
            #     "justshowcolumn": True,
            #     "depend": None
            # },
            "phase_von": {
                "editor": self.uiFineDatingFromCombo,
                "table": "phase",
                "modelcolumn": 1,
                "justshowcolumn": True,
                "depend": None
            },
            "phase_bis": {
                 "editor": self.uiFineDatingToCombo,
                 "table": "phase",
                 "modelcolumn": 1,
                 "justshowcolumn": True,
                 "depend": None
            },
            "datierungsbasis": {
                "editor": self.uiDatingSourceCombo,
                "table": "datierung_quelle",
                "modelcolumn": 0,
                "justshowcolumn": True,
                "depend": None
            },
            "kultur": {
                "editor": self.uiCultureCombo,
                "table": "kultur",
                "modelcolumn": 0,
                "justshowcolumn": False,
                "depend": None
            }#,
            # "fundart": {
            #     "editor": self.uiFindingTypeCombo,
            #     "table": "fundart",
            #     "modelcolumn": 0,
            #     "justshowcolumn": True,
            #     "depend": None
            # },
            # "fundart_detail": {
            #     "editor": self.uiFindingTypeDetailCombo,
            #     "table": "fundart",
            #     "modelcolumn": 0,
            #     "justshowcolumn": False,
            #     "depend": None
            # }
        }
        for key, item in self.comboBoxMaps.items():
            self.mapper.addMapping(item["editor"], self.model.fieldIndex(key))
            self.setupComboBox(item["editor"], item["table"], item["modelcolumn"], item["justshowcolumn"], item["depend"])
            item["editor"].editTextChanged.connect(self.onLineEditChanged)


        #fundart
        self.mapper.addMapping(self.uiFindingTypeCombo, self.model.fieldIndex("fundart"))
        query = u"SELECT DISTINCT {0} FROM {0}".format("fundart")
        self.setupComboBoxByQuery(self.uiFindingTypeCombo, query)
        self.uiFindingTypeCombo.editTextChanged.connect(self.onLineEditChanged)
        self.uiFindingTypeCombo.currentIndexChanged.connect(self.resetFindingTypeDetail)


        #datierung
        self.mapper.addMapping(self.uiDatingTimeCombo, self.model.fieldIndex("datierung_zeit"))
        self.mapper.addMapping(self.uiDatingPeriodCombo, self.model.fieldIndex("datierung_periode"))
        self.mapper.addMapping(self.uiDatingPeriodDetailCombo, self.model.fieldIndex("datierung_periode_detail"))



        #query = u"SELECT DISTINCT {0} FROM {0}".format("zeit")
        #self.setupComboBoxByQuery(self.uiDatingTimeCombo, query)
        #self.uiDatingTimeCombo.setCurrentIndex(-1)

        #txt = self.uiDatingTimeCombo.lineEdit().text()
        #idx = self.uiDatingTimeCombo.findText(txt)
        #QMessageBox.warning(None, self.tr(u"Datierung"), u"{0}, {1}".format(txt, idx))
        #self.loadPeriodContent(0)
        #self.loadPeriodDetailsContent(0)

        #self.uiDatingTimeCombo.editTextChanged.connect(self.onLineEditChanged)
        #self.uiDatingPeriodCombo.editTextChanged.connect(self.onLineEditChanged)
        #self.uiDatingPeriodDetailCombo.editTextChanged.connect(self.onLineEditChanged)
        #self.uiDatingTimeCombo.currentIndexChanged.connect(self.loadPeriodContent)
        #self.uiDatingPeriodCombo.currentIndexChanged.connect(self.loadPeriodDetailsContent)
        # self.uiDatingCombo.currentIndexChanged.connect(self.joinRowValues)

    def loadPeriodContent(self, row):
        #QMessageBox.warning(None, self.tr(u"Datierung Sender"), u"TimeCombo Chagned: {0}".format(row))
        #pass
        #QMessageBox.warning(None, self.tr(u"Datierung Sender"), u"P: {0}".format(self.sender()))

        time = self.uiDatingTimeCombo.lineEdit().text()
        period = self.uiDatingPeriodCombo.lineEdit().text()
        #QMessageBox.warning(None, self.tr(u"Datierung"), u"{0}, {1}".format(time, period))
        #if time != "":
        #time = self.uiDatingTimeCombo.lineEdit().text()
        #period = self.uiDatingPeriodCombo.lineEdit().text()
        #QMessageBox.warning(None, self.tr(u"Datierung"), u"{0}".format(time))
        self.setupComboBoxByQuery(self.uiDatingPeriodCombo, u"SELECT DISTINCT periode FROM zeit WHERE zeit ='{0}'".format(time))

        index = self.uiDatingPeriodCombo.findText(period)
        if index < 0 and self.uiDatingPeriodCombo.count() == 1:
            self.uiDatingPeriodCombo.setCurrentIndex(0)
        #else:
        #    self.uiDatingPeriodCombo.setCurrentIndex(index)


    def loadPeriodDetailsContent(self, row):
        #QMessageBox.warning(None, self.tr(u"Datierung Sender"), u"PD: {0}".format(self.sender()))
        time = self.uiDatingTimeCombo.lineEdit().text()
        period = self.uiDatingPeriodCombo.lineEdit().text()
        periodDetail = self.uiDatingPeriodDetailCombo.lineEdit().text()

            #QMessageBox.warning(None, self.tr(u"Datierung"), u"{0}".format(periodDetail))
        self.setupComboBoxByQuery(self.uiDatingPeriodDetailCombo, u"SELECT DISTINCT periode_detail FROM zeit WHERE zeit = '{0}' AND periode = '{1}'".format(time, period))

        index = self.uiDatingPeriodDetailCombo.findText(periodDetail)
        if index < 0 and self.uiDatingPeriodDetailCombo.count() == 1:
            self.uiDatingPeriodDetailCombo.setCurrentIndex(0)
        #else:
        #        self.uiDatingPeriodDetailCombo.setCurrentIndex(index)

    def resetFindingTypeDetail(self, row):
        self.uiFindingTypeDetailEdit.clear()

    #def setupComboBoxByQuery(self, editor, query):
    def setupComboBoxByQuery(self, editor, query, modelcolumn=0):
        currentText = editor.lineEdit().text()
        model = QSqlQueryModel(self)
        #model.setQuery("SELECT DISTINCT {0} FROM {1} ORDER BY {2}".format(column, table, order), self.dbm.db)
        model.setQuery(query, self.dbm.db)

        tv = QTableView()
        editor.setView(tv)

        tv.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        tv.setSelectionMode(QAbstractItemView.SingleSelection)
        tv.setSelectionBehavior(QAbstractItemView.SelectRows)
        tv.setAutoScroll(False)
        tv.setWordWrap(True)

        editor.setModel(model)

        editor.setModelColumn(modelcolumn)
        editor.setInsertPolicy(QComboBox.NoInsert)

        tv.resizeColumnsToContents()
        tv.resizeRowsToContents()
        tv.verticalHeader().setVisible(False)
        tv.horizontalHeader().setVisible(True)
        tv.setMinimumWidth(tv.horizontalHeader().length()+100)
        tv.horizontalHeader().setResizeMode(QHeaderView.Stretch)

        editor.setAutoCompletion(True)
        editor.lineEdit().setValidator(InListValidator([editor.itemText(i) for i in range(editor.count())], editor.lineEdit(), None, self))

        editor.setCurrentIndex(editor.findText(currentText))
        #editor.setCurrentIndex(-1)

    def setupComboBox(self, editor, table, modelColumn, justShowColumn, depend):
        model = QSqlRelationalTableModel(self, self.dbm.db)
        model.setTable(table)
        model.select()

        tv = QTableView()
        editor.setView(tv)

        tv.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        tv.setSelectionMode(QAbstractItemView.SingleSelection)
        tv.setSelectionBehavior(QAbstractItemView.SelectRows)
        tv.setAutoScroll(False)
        tv.setWordWrap(True)

        editor.setModel(model)
        if justShowColumn:
            cCount = model.columnCount()
            for i in range(cCount):
                if i != modelColumn:
                    tv.hideColumn(i)

        editor.setModelColumn(modelColumn)
        editor.setInsertPolicy(QComboBox.NoInsert)

        tv.resizeColumnsToContents()
        tv.resizeRowsToContents()
        tv.verticalHeader().setVisible(False)
        tv.horizontalHeader().setVisible(True)

        #tv.setMinimumWidth(500)

        tv.setMinimumWidth(tv.horizontalHeader().length()+100)
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

    # def joinRowValues(self, row):
    #     editor = self.sender()
    #     #QMessageBox.warning(None, self.tr(u"Katastralgemeinde"), u"{0}".format(editor))
    #     record = editor.model().record(row)
    #     values = []
    #     for i in range(record.count()):
    #         values.append(record.value(i))
    #     editor.lineEdit().setText(", ".join(values))

    # def setupFindSpotList(self):
    #
    #     query = QSqlQuery(self.dbm.db)
    #     query.prepare("SELECT fundstellenummer AS 'Nummer', datierung AS 'Datierung', fundart AS 'Fundart', fundart_detail AS 'Fundart Detail' FROM fundstelle WHERE fundortnummer = '{0}'".format(self.siteNumber))
    #     query.exec_()
    #
    #     model = QStandardItemModel()
    #     while query.next():
    #         newRow = []
    #         rec = query.record()
    #         for col in range(rec.count()):
    #             #if rec.value(col) == None:
    #             #    value = ''
    #             #else:
    #             value = rec.value(col)
    #             newCol = QStandardItem(unicode(value))
    #             newRow.append(newCol)
    #
    #         model.appendRow(newRow)
    #
    #     #if model.rowCount() < 1:
    #         #QMessageBox.warning(None, "Fundort Auswahl", u"Es wurden keine Fundorte gefunden!")
    #         #return False
    #
    #     rec = query.record()
    #     for col in range(rec.count()):
    #         model.setHeaderData(col, Qt.Horizontal, rec.fieldName(col))
    #
    #     self.uiFindSpotListTableV.setSelectionBehavior(QAbstractItemView.SelectRows)
    #     self.uiFindSpotListTableV.setModel(model)
    #     self.uiFindSpotListTableV.setEditTriggers(QAbstractItemView.NoEditTriggers)
    #     self.uiFindSpotListTableV.resizeColumnsToContents()
    #     self.uiFindSpotListTableV.resizeRowsToContents()
    #     self.uiFindSpotListTableV.horizontalHeader().setResizeMode(QHeaderView.Stretch)


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



    def openTextEditor(self, title, editor):
        textEditorDlg = ApisTextEditorDialog()
        textEditorDlg.setWindowTitle(title)
        textEditorDlg.setText(editor.text())
        if textEditorDlg.exec_():
            editor.setText(textEditorDlg.getText())

    def openFindingTypeDetailDialog(self):
        findingTypeDetailDlg = ApisFindingTypeDetailDialog(self.iface, self.dbm)
        res = findingTypeDetailDlg.loadList(self.uiFindingTypeCombo.currentText(), self.uiFindingTypeDetailEdit.text())
        if res and findingTypeDetailDlg.exec_():
            self.uiFindingTypeDetailEdit.setText(findingTypeDetailDlg.getFindingTypeDetailText())

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


    def loadFindSpotInQGis(self):

        polygon, point = self.askForGeometryType()
        if polygon or point:
            # get PolygonLayer
            findSpotNumber = self.uiFindSpotNumberEdit.text()
            subsetString = u'"fundortnummer"  || \'.\' || "fundstellenummer" = "{0}"'.format(findSpotNumber)
            findSpotLayer = self.getSpatialiteLayer(u"fundstelle", subsetString, u"fundstelle polygon {0}".format(findSpotNumber))

            if polygon:
                # load PolygonLayer
                QgsMapLayerRegistry.instance().addMapLayer(findSpotLayer)

            if point:
                # generate PointLayer
                centerPointLayer = self.generateCenterPointLayer(findSpotLayer, u"fundstelle punkt {0}".format(findSpotNumber))
                # load PointLayer
                QgsMapLayerRegistry.instance().addMapLayer(centerPointLayer)

    def askForGeometryType(self):
        # Abfrage ob Fundstellen der selektierten Bilder Exportieren oder alle
        msgBox = QMessageBox()
        msgBox.setWindowTitle(u'Fundstellen')
        msgBox.setText(u'Wollen Sie für die Fundstelle Polygone, Punkte oder beide Layer verwenden?')
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

    def openShardingSelectionListDialog(self):
        #if self.shardingDlg == None:
        shardingDlg = ApisShardingSelectionListDialog(self.iface, self.dbm)
        shardingDlg.loadShardingListBySiteNumber(self.siteNumber)
        if shardingDlg.exec_():
            pass
            #self.shardingDlg = None


    def cloneFindSpot(self):
        self.initalLoad = True
        currentRecord = QSqlRecord(self.model.record(self.mapper.currentIndex()))
        siteNumber = currentRecord.value('fundortnummer')
        findSpotNumberSource = currentRecord.value('fundstellenummer')
        findSpotNumber = self.getNextFindSpotNumber(siteNumber)
        currentRecord.setValue('fundstellenummer', findSpotNumber)
        now = QDate.currentDate()
        currentRecord.setValue('datum_ersteintrag', now.toString("yyyy-MM-dd"))
        currentRecord.setValue('datum_aenderung', now.toString("yyyy-MM-dd"))

        import getpass
        currentRecord.setValue('aktion','clone')
        currentRecord.setValue('aktionsdatum', now.toString("yyyy-MM-dd"))
        currentRecord.setValue('aktionsuser', getpass.getuser())

        self.model.insertRowIntoTable(currentRecord)
        self.model.setFilter("fundortnummer='{0}' AND fundstellenummer={1}".format(siteNumber, findSpotNumber))
        res = self.model.select()
        #self.mapper.setModel(self.model)
        self.mapper.toFirst()
        self.uiFindSpotNumberEdit.setText("{0}.{1}".format(siteNumber, findSpotNumber))

        self.findSpotNumber = findSpotNumber
        self.siteNumber = siteNumber

        self.findSpotEditsSaved.emit(True)

        #in log eintragen
        self.apisLogger(u"clone", u"fundstelle", u"fundortnummer = '{0}' AND fundstellenummer = {1}".format(self.siteNumber, self.findSpotNumber))

        QMessageBox.information(None, u"Fundstelle Klonen", u"Die Fundstelle {0}.{1} wurde geklont und gespeichert: {0}.{2}".format(siteNumber, findSpotNumberSource, findSpotNumber))
        self.initalLoad = False

    def deleteFindSpot(self):
        # Abfrage wirklich löschen
        header = u"Fundstelle löschen"
        question = u"Möchten Sie die Fundstelle wirklich aus der Datenbank löschen?"
        result = QMessageBox.question(None,
                                      header,
                                      question,
                                      QMessageBox.Yes | QMessageBox.No,
                                      QMessageBox.Yes)

        # save or not save

        if result == QMessageBox.Yes:
            # TODO: in log eintragen
            self.apisLogger(u"delete", u"fundstelle", u"fundortnummer = '{0}' AND fundstellenummer = {1}".format(self.siteNumber, self.findSpotNumber))

            # löschen
            self.model.deleteRowFromTable(self.mapper.currentIndex())

            self.findSpotDeleted.emit(True)
            self.iface.mapCanvas().refreshAllLayers()
            self.done(1)

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

    def getNextFindSpotNumber(self, siteNumber):
        query = QSqlQuery(self.dbm.db)
        query.prepare(u"SELECT CASE WHEN max(fundstellenummer) IS NULL THEN 1 ELSE max(fundstellenummer)+1 END AS nextFindSpot FROM fundstelle WHERE fundortnummer = '{0}'".format(siteNumber))
        res = query.exec_()
        query.first()
        return query.value(0)

    def exportDetailsPdf(self):
        saveDir = self.settings.value("APIS/working_dir", QDir.home().dirName())
        fileName = QFileDialog.getSaveFileName(self, 'Fundstelle Details', saveDir + "\\" + 'FundstelleDetails_{0}.{1}_{2}'.format(self.siteNumber, self.findSpotNumber,QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")),'*.pdf')

        if fileName:

            qryStr = u"SELECT katastralgemeinde, katastralgemeindenummer, fundstelle.* FROM fundstelle, fundort WHERE fundstelle.fundortnummer = fundort.fundortnummer AND fundstelle.fundortnummer = '{0}' AND fundstelle.fundstellenummer = {1}".format(self.siteNumber, self.findSpotNumber)
            query = QSqlQuery(self.dbm.db)
            query.prepare(qryStr)
            query.exec_()

            findSpotDict = {}
            query.seek(-1)
            while query.next():
                rec = query.record()
                for col in range(rec.count()-1): #-1 geometry wird nicht benötigt!
                    #val = unicode(rec.value(col))
                    #QMessageBox.information(None, "type", u"{0}".format(type(rec.value(col))))
                    val = u"{0}".format(rec.value(col))
                    if val.replace(" ", "") == '' or val == 'NULL':
                        val = u"---"

                    findSpotDict[unicode(rec.fieldName(col))] = val

                findSpotDict['datum_druck'] = QDate.currentDate().toString("dd.MM.yyyy")
                findSpotDict['datum_ersteintrag'] = QDate.fromString(findSpotDict['datum_ersteintrag'], "yyyy-MM-dd").toString("dd.MM.yyyy")
                findSpotDict['datum_aenderung'] = QDate.fromString(findSpotDict['datum_aenderung'], "yyyy-MM-dd").toString("dd.MM.yyyy")


                if findSpotDict['sicherheit'] == u"1":
                    findSpotDict['sicherheit'] = u"sicher"
                elif findSpotDict['sicherheit'] == u"2":
                    findSpotDict['sicherheit'] = u"wahrscheinlich"
                elif findSpotDict['sicherheit'] == u"3":
                    findSpotDict['sicherheit'] = u"fraglich"
                elif findSpotDict['sicherheit'] == u"4":
                    findSpotDict['sicherheit'] = u"keine Fundstelle"

            # MapSettings
            mapSettings = QgsMapSettings()
            mapSettings.setMapUnits(QGis.UnitType(0))
            mapSettings.setOutputDpi(300)


            # Template
            template = os.path.dirname(__file__) + "/composer/templates/FundstelleDetail.qpt"  # map_print_test.qpt"
            templateDom = QDomDocument()
            templateDom.setContent(QFile(template), False)

            # Composition
            composition = QgsComposition(mapSettings)
            composition.setPlotStyle(QgsComposition.Print)
            composition.setPrintResolution(300)

            # Composer Items

            composition.loadFromTemplate(templateDom, findSpotDict)
            pageCount = 1

            adjustItems = ["kommentar_lage", "fundbeschreibung", "fundverbleib", "befund", "fundgeschichte", "literatur", "sonstiges"]
            #xShift = 0
            #yShift = 0
            bottomBorder = 30.0
            topBorder = 27.0
            i = 0
            for itemId in adjustItems:

                itemTxt = composition.getComposerItemById(itemId + "Txt")
                itemLbl = composition.getComposerItemById(itemId +"Lbl")
                itemBox = composition.getComposerItemById(itemId + "Box")

                if itemTxt and itemLbl:

                    #textWidth = QgsComposerUtils.textWidthMM(itemTxt.font(), itemTxt.displayText())
                    fontHeight = QgsComposerUtils.fontHeightMM(itemTxt.font())
                    oldHeight = itemTxt.rectWithFrame().height()
                    displayText = itemTxt.displayText()
                    boxWidth = itemTxt.rectWithFrame().width() - 2 * itemTxt.marginX()
                    lineCount = 0
                    for line in displayText.splitlines():
                        textWidth = max(1.0, QgsComposerUtils.textWidthMM(itemTxt.font(), line))
                        lineCount += math.ceil(textWidth / boxWidth)

                    newHeight = fontHeight * (lineCount + 1)
                    newHeight += 2 * itemTxt.marginY() + 2

                    x = itemTxt.pos().x()
                    if i == 0:
                        y = itemTxt.pos().y()
                    else:
                        y = newY
                    w = itemTxt.rectWithFrame().width()
                    newY = y + newHeight
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

                    itemTxt.setItemPosition(x, y, w, newHeight, QgsComposerItem.UpperLeft, True, pageCount)
                    itemLbl.setItemPosition(itemLbl.pos().x(), y, itemLbl.rectWithFrame().width(), itemLbl.rectWithFrame().height(), QgsComposerItem.UpperLeft, True, pageCount)

                    i += 1

                    if itemBox:
                        h = (itemBox.rectWithFrame().height() - oldHeight) + newHeight
                        itemBox.setItemPosition(itemBox.pos().x(), itemBox.pos().y(), itemBox.rectWithFrame().width(), h, QgsComposerItem.UpperLeft, True, pageCount)


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

    def openSiteDialog(self):
        from apis_site_dialog import ApisSiteDialog
        # if parent is instance of ApisSiteDialog then just close
        # if parent is ApisFindSpotSelectionListDialog then open ApisSiteDialog and close ApisFindSpotDialog
        if isinstance(self.parentWidget(), ApisSiteDialog):
            #QMessageBox.warning(None, "Test", u"{0}".format(self.parentWidget()))
            self.close()
        else:
            siteDlg = ApisSiteDialog(self.iface, self.dbm, self.imageRegistry, self.parentWidget())
            siteDlg.openInViewMode(self.siteNumber)
            self.close()
            siteDlg.show()
            if siteDlg.exec_():
                pass
            siteDlg.removeSitesFromSiteMapCanvas()


    def removeNewFindSpot(self):
        self.initalLoad = True
        row = self.mapper.currentIndex()
        self.model.removeRow(row)
        self.model.submitAll()
        self.initalLoad = False

    def saveEdits(self):
        # Check Mandatory fields
        flag = False
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
                # ROT wenn Plichtfeld leer
                mEditor.setStyleSheet("{0} {{background-color: rgb(240, 160, 160);}}".format(cName))
                if mEditor not in self.editorsEdited:
                    self.editorsEdited.append(mEditor)
            else:
                if mEditor in self.editorsEdited:
                    # BLAU wenn Pflichtfeld nicht leer und editiert
                    mEditor.setStyleSheet("{0} {{background-color: rgb(153, 204, 255);}}".format(cName))
                #else:
                    #mEditor.setStyleSheet("")
        if flag:
            QMessageBox.warning(None, self.tr(u"Benötigte Felder Ausfüllen"), self.tr(u"Füllen Sie bitte alle Felder aus, die mit * gekennzeichnet sind."))
            return False

        #saveToModel
        currIdx = self.mapper.currentIndex()
        now = QDate.currentDate()
        self.uiLastChangesDate.setDate(now)

        if self.addMode:
            action = u"new"
        else:
            action = u"editA"
            #Update AKTION only in EDIT Mode
            self.model.setData(self.model.createIndex(currIdx, self.model.fieldIndex("aktion")), u"editAG" if self.geometryEditing else u"editA")
            self.model.setData(self.model.createIndex(currIdx, self.model.fieldIndex("aktionsdatum")), now.toString("yyyy-MM-dd"))
            import getpass
            self.model.setData(self.model.createIndex(currIdx, self.model.fieldIndex("aktionsuser")), getpass.getuser())

        self.mapper.submit()

        #emit signal
        self.findSpotEditsSaved.emit(True)

        #log
        self.apisLogger(action, u"fundstelle", u"fundortnummer = '{0}' AND fundstellenummer = {1}".format(self.siteNumber, self.findSpotNumber))

        self.mapper.setCurrentIndex(currIdx)
        self.endEditMode()

        self.iface.mapCanvas().refreshAllLayers()
        #
        if not self.isGeometryEditingSaved:
            self.isGeometryEditingSaved = True
        return True



    def cancelEdit(self):
        currIdx = self.mapper.currentIndex()
        if self.editMode:
            if self.addMode:
                header = self.tr(u"Neue Fundstelle wurden hinzugefügt!")
                question = self.tr(u"Möchten Sie die neue Fundstelle speichern?")
            elif self.geometryEditing:
                header = self.tr(u"Änderungen an der Fundstellen Geometrie wurden vorgenommen!")
                question = self.tr(u"Möchten Sie die Änderungen der Geometrie und Attribute speichern?")
            else:
                header = self.tr(u"Änderungen wurden vorgenommen!")
                question = self.tr(u"Möchten Sie die Änderungen der Attribute speichern?")
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
                self.geometryEditing = False
                if self.addMode:
                    self.removeNewFindSpot()
                    self.endEditMode(False)
                    self.close()
                    return True
                else:
                    self.mapper.setCurrentIndex(currIdx)
                    self.endEditMode(False)
                    return True

    def startEditMode(self):
        self.editMode = True
        #self.setWindowModality(Qt.ApplicationModal)
        #self.setModal(True)
        #geomHelper = self.saveGeometry()
        #self.hide()
        #self.show()
        #self.restoreGeometry(geomHelper)
        self.enableItemsInLayout(self.uiBottomHorizontalLayout, False)
        self.uiOkBtn.setEnabled(False)
        self.uiSaveBtn.setEnabled(True)
        self.uiCancelBtn.setEnabled(True)
        self.editorsEdited = []

    def endEditMode(self, modalityFlag=True):
        self.editMode = False
        self.addMode = False
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



        #self.uiDatingTimeCombo.editTextChanged.disconnect(self.onLineEditChanged)
        #self.uiDatingPeriodCombo.editTextChanged.disconnect(self.onLineEditChanged)
        #self.uiDatingPeriodDetailCombo.editTextChanged.disconnect(self.onLineEditChanged)
        self.initalLoad = True
        self.uiDatingTimeCombo.currentIndexChanged.disconnect(self.loadPeriodContent)
        self.uiDatingPeriodCombo.currentIndexChanged.disconnect(self.loadPeriodDetailsContent)
        #self.loadPeriodContent(0)
        #self.loadPeriodDetailsContent(0)
        time = self.uiDatingTimeCombo.lineEdit().text()
        period = self.uiDatingPeriodCombo.lineEdit().text()
        periodDetail = self.uiDatingPeriodDetailCombo.lineEdit().text()
        #QMessageBox.warning(None, "Test", u"{0}, {1}, {2}".format(time, period, periodDetail))

        self.uiDatingTimeCombo.setCurrentIndex(self.uiDatingTimeCombo.findText(time))
        self.loadPeriodContent(0)
        self.loadPeriodDetailsContent(0)
        #self.setupComboBoxByQuery(self.uiDatingPeriodCombo, u"SELECT DISTINCT periode FROM zeit WHERE zeit ='{0}'".format(time))
        #self.uiDatingPeriodCombo.setCurrentIndex(self.uiDatingPeriodCombo.findText(period))
        #self.setupComboBoxByQuery(self.uiDatingPeriodDetailCombo, u"SELECT DISTINCT periode_detail FROM zeit WHERE zeit = '{0}' AND periode = '{1}'".format(time, period))
        #self.uiDatingPeriodDetailCombo.setCurrentIndex(self.uiDatingPeriodDetailCombo.findText(periodDetail))

        #self.uiDatingTimeCombo.editTextChanged.connect(self.onLineEditChanged)
        #self.uiDatingPeriodCombo.editTextChanged.connect(self.onLineEditChanged)
        #self.uiDatingPeriodDetailCombo.editTextChanged.connect(self.onLineEditChanged)
        self.uiDatingTimeCombo.currentIndexChanged.connect(self.loadPeriodContent)
        self.uiDatingPeriodCombo.currentIndexChanged.connect(self.loadPeriodDetailsContent)
        self.initalLoad = False
        #self.setWindowModality(Qt.NonModal)
        #self.setModal(False)
        #if modalityFlag:
        #    self.hide()
        #    self.show()

    def isGeometrySaved(self):
        return self.isGeometryEditingSaved and self.geometryEditing

class FindSpotDelegate(QSqlRelationalDelegate):
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

        elif editor.metaObject().className() == 'QLineEdit':
            editor.setText(value)

        elif editor.metaObject().className() == 'QComboBox':
            if index.column() == 2: #sicherheit
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

        # if index.column() == 0: #0 ... filmnummer, 1 ... filmnummer_legacy, 2 ... filmnummer_hh_jjjj_mm, 3 ... filmnummer_nn
        #     #QMessageBox.warning(None, "Test", unicode(index.column()) + editor.text())
        #     filmnummer = str(editor.text())
        #     model.setData(model.createIndex(index.row(), 2), filmnummer[:8]) # filmnummer_hh_jjjj_mm
        #     model.setData(model.createIndex(index.row(), 3), int(filmnummer[-2:])) # filmnummer_nn
        #     model.setData(model.createIndex(index.row(), 0), filmnummer) #filmnummer
        #     mil = ""
        #     if filmnummer[2:4] == "19":
        #         mil = "01"
        #     elif filmnummer[2:4] == "20":
        #         mil = "02"
        #     model.setData(model.createIndex(index.row(), 1), mil + filmnummer[4:]) # filmnummer_legacy

        # elif editor.metaObject().className() == 'QDateEdit':
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
            if index.column() == 2: #sicherheit
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
