# -*- coding: utf-8 -*

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from PyQt4.QtXml import *
from qgis.core import *

from apis_db_manager import *
from apis_film_number_selection_dialog import *
from apis_new_film_dialog import *
from apis_edit_weather_dialog import *
from apis_search_film_dialog import *
from apis_film_selection_list_dialog import *

from functools import partial
import subprocess
import string

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/composer")

# --------------------------------------------------------
# Film - Eingabe, Pflege
# --------------------------------------------------------
from apis_film_form import *

class ApisFilmDialog(QDialog, Ui_apisFilmDialog):

    FIRST, PREV, NEXT, LAST = range(4)

    def __init__(self, iface, dbm):
        QDialog.__init__(self)
        self.iface = iface
        self.dbm = dbm
        self.setupUi(self)

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
        self.uiExportPdfBtn.clicked.connect(self.exportDetailsPdf)

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
        self.searchFilmDlg = ApisSearchFilmDialog(self.iface)
        self.editWeatherDlg = ApisEditWeatherDialog(self.iface, self.dbm)



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

    def cbValidate(self):
        #FIXME: Implement with QValidator
        QMessageBox.warning(None, "Test", unicode([self.uiArchiveCombo.itemText(i) for i in range(self.uiArchiveCombo.count())]))

    def setupMapper(self):
        self.mapper = QDataWidgetMapper(self)

        self.mapper.currentIndexChanged.connect(self.onCurrentIndexChanged)

        self.mapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
        self.mapper.setItemDelegate(FilmDelegate())

        self.mapper.setModel(self.model)

        self.mandatoryEdtis = [self.uiImageCountEdit, self.uiCameraCombo, self.uiFilmMakeCombo, self.uiFilmModeCombo]

        # LineEdits & PlainTextEdits
        self.lineEditMaps = {
            "filmnummer": {
                "editor": self.uiCurrentFilmNumberEdit
            },
            "hersteller": {
                "editor": self.uiProducerEdit
            },
            "anzahl_bilder":{
                "editor": self.uiImageCountEdit
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
                "editor": self.uiCalibratedFocalLengthEdit
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
            item["editor"].textChanged.connect(partial(self.onLineEditChanged, item["editor"]))

        #Text
        #self.mapper.addMapping(self.uiCommentsPTxt, self.model.fieldIndex("kommentar"))

        # Date and Times
        self.mapper.addMapping(self.uiFlightDate, self.model.fieldIndex("flugdatum"))
        self.mapper.addMapping(self.uiInitalEntryDate, self.model.fieldIndex("datum_ersteintrag"))
        self.mapper.addMapping(self.uiLastChangesDate, self.model.fieldIndex("datum_aenderung"))

        self.mapper.addMapping(self.uiDepartureTime, self.model.fieldIndex("abflug_zeit"))
        self.mapper.addMapping(self.uiArrivalTime, self.model.fieldIndex("ankunft_zeit"))

        self.uiDepartureTime.timeChanged.connect(self.onFlightTimeChanged)
        self.uiArrivalTime.timeChanged.connect(self.onFlightTimeChanged)


        # ComboBox without Model
        self.mapper.addMapping(self.uiFilmModeCombo, self.model.fieldIndex("weise"))

        # ComboBox with Model
        self.comboBoxMaps = {
            # "hersteller": {
            #     "editor": self.uiProducerCombo,
            #     "table": "hersteller",
            #     "modelcolumn": 2,
            #     "depend": None
            # },
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
            item["editor"].editTextChanged.connect(partial(self.onLineEditChanged, item["editor"]))

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
        tv.setMinimumWidth(tv.horizontalHeader().length())

        editor.setAutoCompletion(True)
        #editor.lineEdit().setValidator(InListValidator([editor.itemText(i) for i in range(editor.count())], editor.lineEdit(), self))
        #self.uiProducerCombo.lineEdit().editingFinished.connect(self.cbValidate)

        if depend:
            editor.currentIndexChanged.connect(partial(self.updateDepends, editor, depend))
            #mapper = QDataWidgetMapper(self)

            #mapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
            #mapper.setItemDelegate(DependDelegate())# Delegate with setData Pass!

            #mapper.setModel(model)
            #for dep in depend:
                #for key, value in dep.iteritems():
                    #QMessageBox.warning(None, "Test", str(key) + str(value))
                    #mapper.addMapping(value, model.fieldIndex(key))
                    #editor.currentIndexChanged.connect(lambda: mapper.setCurrentIndex(editor.currentIndex()))

    def updateDepends(self, editor, depend):
         for dep in depend:
                for key, value in dep.iteritems():
                    idx = editor.model().createIndex(editor.currentIndex(), editor.model().fieldIndex(key))
                    value.setText(unicode(editor.model().data(idx)))
                    #QMessageBox.warning(None, "Test", str(editor.model().data(idx)))


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

    def onFlightTimeChanged(self):
        dTime = self.uiDepartureTime.time()
        aTime = self.uiArrivalTime.time()
        flightDuration = dTime.secsTo(aTime)
        self.uiFlightDurationEdit.setText(unicode(flightDuration/60))

    def onLineEditChanged(self, editor):
        if not self.editMode and not self.initalLoad:
            self.startEditMode()
        if not self.initalLoad:
            editor.setStyleSheet("{0} {{background-color: rgb(153, 204, 255);}}".format(editor.metaObject().className()))
            self.editorsEdited.append(editor)

    def onComboBoxChanged(self, editor):
        pass

    def addProject(self):
        editor =  self.uiProjectList
        editor.addItem(self.uiProjectSelectionCombo.currentText())
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
            self.cancelEdit()
        self.close()

    def exportDetailsPdf(self):
        fileName = QFileDialog.getSaveFileName(self, 'Film Details', 'c://FilmDetails_{0}'.format(self.uiCurrentFilmNumberEdit.text()), '*.pdf')
        if fileName:
            #QMessageBox.warning(None, "Save", fileName)
            #FIXME template from Settings
            template = 'C:/Users/Johannes/.qgis2/python/plugins/APIS/composer/templates/FilmDetails.qpt'
            #if os.path.isfile(template):
            templateDOM = QDomDocument()
            templateDOM.setContent(QFile(template), False)
            mr = QgsMapRenderer()
            comp = QgsComposition(mr)
            m = self.mapper.model()
            r = self.mapper.currentIndex()
            filmDict = {}
            for c in range(m.columnCount()):
                filmDict[m.headerData(c, Qt.Horizontal)] = unicode(m.data(m.createIndex(r, c)))
                #QMessageBox.warning(None, "Save", "{0}:{1}".format(colName, value))

            comp.loadFromTemplate(templateDOM, filmDict)
            comp.exportAsPDF(fileName)

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
                searchListDlg = ApisFilmSelectionListDialog(self.iface, model)
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
            self.addNewFilm(self.newFilmDlg.flightDate(), self.newFilmDlg.useLastEntry(), self.newFilmDlg.producer())

    def openEditWeatherDialog(self):
        self.editWeatherDlg.setWeatherCode(self.uiWeatherCodeEdit.text())
        self.editWeatherDlg.show()

        if self.editWeatherDlg.exec_():
            self.uiWeatherCodeEdit.setText(self.editWeatherDlg.weatherCode())
            self.uiWeatherPTxt.setPlainText(self.editWeatherDlg.weatherDescription())

    def addNewFilm(self, flightDate, useLastEntry, producer):
        self.initalLoad = True
        self.addMode = True
        row = self.model.rowCount()
        self.mapper.submit()
        while (self.model.canFetchMore()):
            self.model.fetchMore()

        self.model.insertRow(row)
        if useLastEntry:
            #copy last row
            #selectionModel = QItemSelectionModel(self.model)
            #QMessageBox.warning(None, "SelectionModel","{0}".format(selectionModel.currentIndex().row()))
            #self.mapper.setCurrentIndex(row)
            for c in range(self.model.columnCount()):
                value = self.model.data(self.model.createIndex(row-1, c))
                #QMessageBox.warning(None, "SelectionModel",u"{0}".format(value))
                self.model.setData(self.model.createIndex(row,c), value)

        self.mapper.setCurrentIndex(row)

        self.uiTotalFilmCountLbl.setText(unicode(self.model.rowCount()))
        self.uiFlightDate.setDate(flightDate)
        self.uiProducerEdit.setText(producer)

        now = QDate.currentDate()
        self.uiInitalEntryDate.setDate(now)
        self.uiLastChangesDate.setDate(now)
        self.uiFilmModeCombo.setEnabled(True)

        #FIXME: Introduce New FilmID
        if flightDate.year() >= 2000:
            hh = "02"
        else:
            hh = "01"

        yy = flightDate.toString("yy")
        mm = flightDate.toString("MM")

        query = QSqlQuery(self.dbm.db)
        qryStr = "select max(filmnummer_nn) from film where filmnummer_hh_jj_mm = '{0}{1}{2}' limit 1".format(hh, yy, mm)
        query.exec_(qryStr)
        query.first()
        fn = query.value(0)

        if isinstance(fn, long):
            nn = str(fn + 1).zfill(2)
        else:
            nn = "01"

        self.uiCurrentFilmNumberEdit.setText("{0}{1}{2}{3}".format(hh, yy, mm, nn))
        self.startEditMode()
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
        #ToDo Check Mandatory fields
        #for mandatoryEditor in self.mandatoryEdtis:

        #saveToModel
        currIdx = self.mapper.currentIndex()
        now = QDate.currentDate()
        self.uiLastChangesDate.setDate(now)
        self.mapper.submit()

        while (self.model.canFetchMore()):
            self.model.fetchMore()

        self.mapper.setCurrentIndex(currIdx)
        self.endEditMode()

    def cancelEdit(self):
        if self.editMode:
            result = QMessageBox.question(None,
                                          self.tr(u"Änderungen wurden vorgenommen!"),
                                          self.tr(u"Möchten Sie die Änerungen speichern?"),
                                          QMessageBox.Yes | QMessageBox.No ,
                                          QMessageBox.Yes)

            #save or not save
            if result == QMessageBox.Yes:
                self.saveEdits()
            elif result == QMessageBox.No:
                if self.addMode:
                    self.removeNewFilm()

                self.mapper.setCurrentIndex(self.mapper.currentIndex())
                self.endEditMode()

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
            if editor.metaObject().className() == "QLineEdit" and editor.isReadOnly():
                editor.setStyleSheet("QLineEdit {background-color: rgb(218, 218, 218);}")
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

        if editor.metaObject().className() == 'QLineEdit':
            editor.setText(unicode(index.model().data(index, Qt.EditRole)))

        elif editor.metaObject().className() == 'QComboBox':
            editor.setEditText(unicode(index.model().data(index, Qt.EditRole)))

        elif editor.metaObject().className() == 'QListWidget':
            #QMessageBox.warning(None, "Test", unicode(index.model().data(index, Qt.EditRole)))
            editor.clear()
            editor.addItems(string.split(unicode(index.model().data(index, Qt.EditRole)), ";"))
        else:
            QSqlRelationalDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        #if editor.metaObject().className() == 'QLineEdit':
            #QMessageBox.warning(None, "Test", unicode(index.data(Qt.DisplayRole)) + ',' + unicode(editor.text()))
            #if unicode(index.data(Qt.DisplayRole)) != unicode(editor.text()):
            #    QMessageBox.warning(None, "Test", unicode(index.data(Qt.DisplayRole)) + ',' + unicode(editor.text()))
            #    model.setData(index, editor.text())

        if index.column() == 2:
            #QMessageBox.warning(None, "Test", unicode(index.column()) + editor.text())
            model.setData(model.createIndex(index.row(), 0), str(editor.text())[:6])
            model.setData(model.createIndex(index.row(), 1), int(str(editor.text())[-2:]))

        if editor.metaObject().className() == 'QListWidget':
            items = []
            for j in xrange(editor.count()):
                items.append(editor.item(j))
            model.setData(index, ";".join([i.text() for i in items]))
        else:
            QSqlRelationalDelegate.setModelData(self, editor, model, index)

class DependDelegate(QSqlRelationalDelegate):
    def __init__(self):
       QSqlRelationalDelegate.__init__(self)

    def createEditor(self, parent, option, index):
        pass

    def setEditorData(self, editor, index):
        editor.setText(unicode(index.model().data(index, Qt.DisplayRole)))

    def setModelData(self, editor, model, index):
        pass


class DropBoxDelegate(QStyledItemDelegate):
    def __init__(self):
        QStyledItemDelegate.__init__(self)

    def createEditor(self, parent, option, index):
        pass

    def setEditorData(self, editor, index):
        QMessageBox.warning(None, "Test", unicode(index.model().data(index, Qt.DisplayRole)))
        pass

    def setModelData(self, editor, model, index):
        QMessageBox.warning(None, "Test", editor.text())
        pass

class InListValidator(QValidator):
        def __init__(self, itemList, editor, parent):
            QValidator.__init__(self, parent)

            self.itemList = itemList
            self.editor = editor

        def validate(self, s, pos):

            if unicode(s) in self.itemList or unicode(s).strip()=='':
                return (QValidator.Acceptable, s, pos)

            return (QValidator.Invalid, "", pos)


        def fixup(self, s):
            #QMessageBox.warning(None, "Test", unicode(s))
            self.editor.setText("")
