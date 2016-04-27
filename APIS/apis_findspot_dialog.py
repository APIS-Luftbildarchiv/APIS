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

from functools import partial
import subprocess
import string

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

    def __init__(self, iface, dbm, parent=None):
        QDialog.__init__(self, parent)
        self.iface = iface
        self.dbm = dbm

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

        self.uiListShardingsOfSiteBtn.clicked.connect(self.openShardingSelectionListDialog)

        self.uiViewSiteBtn.clicked.connect(self.openSiteDialog)

        # Setup Sub-Dialogs
        self.shardingDlg = None

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

        #self.setupFindSpotList()

        self.initalLoad = False


    def openInEditMode(self, siteNumber, kgCode, kgName, siteArea):
        self.initalLoad = True
        self.siteNumber = siteNumber
        self.geometryEditing = True

        # Setup site model
        self.model = QSqlRelationalTableModel(self, self.dbm.db)
        self.model.setTable("fundort")
        self.model.setFilter("fundortnummer='{0}'".format(self.siteNumber))
        res = self.model.select()
        self.setupMapper()
        self.mapper.toFirst()

        self.startEditMode()
        self.initalLoad = False

        #update Editors
        if self.uiCadastralCommunityNumberEdit.text() != kgCode:
            self.uiCadastralCommunityNumberEdit.setText(kgCode)
        if self.uiCadastralCommunityEdit.text() != kgName:
            self.uiCadastralCommunityEdit.setText(kgName)
        if self.uiAreaEdit.text() != siteArea:
            self.uiAreaEdit.setText(unicode(siteArea))


    def openInAddMode(self, siteNumber):
        self.initalLoad = True
        self.siteNumber = siteNumber

        # Setup site model
        self.model = QSqlRelationalTableModel(self, self.dbm.db)
        self.model.setTable("fundort")
        self.model.setFilter("fundortnummer='{0}'".format(self.siteNumber))
        res = self.model.select()
        self.setupMapper()
        self.mapper.toFirst()

        self.addMode = True
        self.startEditMode()

        self.initalLoad = False


    def setupMapper(self):
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
        self.mapper.setItemDelegate(FindSpotDelegate())

        self.mapper.setModel(self.model)

        self.mandatoryEditors = [self.uiCaseWorkerEdit, self.uiFindSpotCreationCombo, self.uiSiteReliabilityCombo, self.uiDatingCombo, self.uiFindingTypeCombo]

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
            "literatur":{
                "editor": self.uiLiteraturePTxt
            },
            "fundbeschreibung":{
                "editor": self.uiFindingsPTxt
            },
            "fundverbleib": {
                "editor": self.uiFindingsPTxt
            },

            "sonstiges": {
                "editor": self.uiFindingsPTxt
            },
            "fundgeschichte": {
                "editor": self.uiFindingsPTxt
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
            "datierung": {
                "editor": self.uiDatingCombo,
                "table": "zeit",
                "modelcolumn": 0,
                "justshowcolumn": False,
                "depend": None
            },
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
            },
            # "fundart": {
            #     "editor": self.uiFindingTypeCombo,
            #     "table": "fundart",
            #     "modelcolumn": 0,
            #     "justshowcolumn": True,
            #     "depend": None
            # },
            "fundart_detail": {
                "editor": self.uiFindingTypeDetailCombo,
                "table": "fundart",
                "modelcolumn": 0,
                "justshowcolumn": False,
                "depend": None
            }
        }
        for key, item in self.comboBoxMaps.items():
            self.mapper.addMapping(item["editor"], self.model.fieldIndex(key))
            self.setupComboBox(item["editor"], item["table"], item["modelcolumn"], item["justshowcolumn"], item["depend"])
            item["editor"].editTextChanged.connect(self.onLineEditChanged)


        #fundart
        self.mapper.addMapping(self.uiFindingTypeCombo, self.model.fieldIndex("fundart"))
        #self.setupComboBox(item["editor"], item["table"], item["modelcolumn"], item["justshowcolumn"], item["depend"])
        query = u"SELECT DISTINCT {0} FROM {0}".format("fundart")
        self.setupComboBoxByQuery(self.uiFindingTypeCombo, query)

        self.uiFindingTypeCombo.editTextChanged.connect(self.onLineEditChanged)
        self.uiFindingTypeCombo.currentIndexChanged.connect(self.setupFindingTypeDetail)

        self.uiDatingCombo.currentIndexChanged.connect(self.joinRowValues)


    def setupFindingTypeDetail(self, row):
        editor = self.sender()
        # QMessageBox.warning(None, self.tr(u"Katastralgemeinde"), u"{0}".format(editor))
        record = editor.model().record(row)
        findingType = record.value(0)
        query = u"SELECT fundart_detail FROM fundart WHERE fundart = '{0}'".format(findingType)
        self.setupComboBoxByQuery(self.uiFindingTypeDetailCombo, query)

    #def setupComboBoxByQuery(self, editor, query):
    def setupComboBoxByQuery(self, editor, query, modelcolumn=0):
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

    def joinRowValues(self, row):
        editor = self.sender()
        #QMessageBox.warning(None, self.tr(u"Katastralgemeinde"), u"{0}".format(editor))
        record = editor.model().record(row)
        values = []
        for i in range(record.count()):
            values.append(record.value(i))
        editor.lineEdit().setText(", ".join(values))

    def setupFindSpotList(self):

        query = QSqlQuery(self.dbm.db)
        query.prepare("SELECT fundstellenummer AS 'Nummer', datierung AS 'Datierung', fundart AS 'Fundart', fundart_detail AS 'Fundart Detail' FROM fundstelle WHERE fundortnummer = '{0}'".format(self.siteNumber))
        query.exec_()

        model = QStandardItemModel()
        while query.next():
            newRow = []
            rec = query.record()
            for col in range(rec.count()):
                #if rec.value(col) == None:
                #    value = ''
                #else:
                value = rec.value(col)
                newCol = QStandardItem(unicode(value))
                newRow.append(newCol)

            model.appendRow(newRow)

        #if model.rowCount() < 1:
            #QMessageBox.warning(None, "Fundort Auswahl", u"Es wurden keine Fundorte gefunden!")
            #return False

        rec = query.record()
        for col in range(rec.count()):
            model.setHeaderData(col, Qt.Horizontal, rec.fieldName(col))

        self.uiFindSpotListTableV.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.uiFindSpotListTableV.setModel(model)
        self.uiFindSpotListTableV.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.uiFindSpotListTableV.resizeColumnsToContents()
        self.uiFindSpotListTableV.resizeRowsToContents()
        self.uiFindSpotListTableV.horizontalHeader().setResizeMode(QHeaderView.Stretch)


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
        self.shardingDlg.loadShardingListBySiteNumber(self.siteNumber)
        if self.shardingDlg.exec_():
            pass
            #self.shardingDlg = None


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
            uri = flightpathDir + "\\" + self.uiFlightDate.date().toString("yyyy") + "\\" + filmId + "_lin.shp"
            printLayer = QgsVectorLayer(uri, "FlightPath", "ogr")
            #printLayer.setCrs(QgsCoordinateReferenceSystem(4312, QgsCoordinateReferenceSystem.EpsgCrsId))
            #symbol = QgsLineSymbolV2.createSimple({'color':'orange', 'line_width':'0.8'})
            #printLayer.rendererV2().setSymbol(symbol)
            QgsMapLayerRegistry.instance().addMapLayer(printLayer, False) #False = don't add to Layers (TOC)
            extent = printLayer.extent()

            #layerset.append(printLayer.id())
            printLayers.append(printLayer.id())

            #urlWithParams = ' '
            #urlWithParams = 'url=http://wms.jpl.nasa.gov/wms.cgi&layers=global_mosaic&styles=pseudo&format=image/jpeg&crs=EPSG:4326'
            #rlayer = QgsRasterLayer(urlWithParams, 'basemap', 'wms')
            #QgsMapLayerRegistry.instance().addMapLayer(rlayer)
            #printLayers.append(rlayer.id())

            ms = QgsMapSettings()
            ms.setExtent(extent)
            #mr.setLayerSet(layerset)

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
            composerMap.setKeepLayerSet(True)
            composerMap.setLayerSet(printLayers)
            #composerMap.renderModeUpdateCachedImage()
            #ms.setLayers(printLayers)

            #if composerMap:
                #QMessageBox.warning(None, "Save", composerMap)
           #composerMap.setKeepLayerSet(True)
            #composerMap.setLayerSet(layerset)



            comp.exportAsPDF(fileName)
            #FIXME: Delete all alyers (array) not just one layer
            QgsMapLayerRegistry.instance().removeMapLayer(printLayer.id())
            #QgsMapLayerRegistry.instance().removeMapLayer(rlayer.id())

            if sys.platform == 'linux2':
                subprocess.call(["xdg-open", fileName])
            else:
                os.startfile(fileName)
            #else:
            #    QMessageBox.warning(None, "Save", "QGIS Template File Not Correct!")


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


    def openSiteDialog(self):
        from apis_site_dialog import ApisSiteDialog
        # if parent is instance of ApisSiteDialog then just close
        # if parent is ApisFindSpotSelectionListDialog then open ApisSiteDialog and close ApisFindSpotDialog
        if isinstance(self.parentWidget(), ApisSiteDialog):
            #QMessageBox.warning(None, "Test", u"{0}".format(self.parentWidget()))
            self.close()
        else:
            siteDlg = ApisSiteDialog(self.iface, self.dbm)
            siteDlg.openInViewMode(self.siteNumber)
            self.close()
            siteDlg.show()
            if siteDlg.exec_():
                pass


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
        now = QDate.currentDate()
        self.uiLastChangesDate.setDate(now)
        self.mapper.submit()

        #emit signal
        self.findSpotEditsSaved.emit(True)

        # Add "hidden" Values with Query
        #sqlQry = "UPDATE fundort "

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