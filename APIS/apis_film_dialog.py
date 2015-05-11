# -*- coding: utf-8 -*

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

from apis_db_manager import *
from apis_film_selection_dialog import *
from apis_new_film_dialog import *

from functools import partial

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

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
        self.initalLoad = True
        # Signals/Slot Connections
        self.rejected.connect(self.onReject)
        #self.uiButtonBox.rejected.connect(self.onReject)
        self.uiOkBtn.clicked.connect(self.onAccept)
        self.uiCancelBtn.clicked.connect(self.cancelEdit)
        self.uiSaveBtn.clicked.connect(self.saveEdits)

        self.uiFilmSelectionBtn.clicked.connect(self.openFilmSelectionDialog)
        self.uiNewFilmBtn.clicked.connect(self.openNewFilmDialog)
        #self.uiButtonBox.button(QDialogButtonBox.Ok).setDefault(False)
        #self.uiButtonBox.button(QDialogButtonBox.Ok).setAutoDefault(False)
        #self.uiButtonBox.button(QDialogButtonBox.Cancel).setDefault(False)
        #self.uiButtonBox.button(QDialogButtonBox.Cancel).setAutoDefault(False)

        # Setup Sub-Dialogs
        self.filmSelectionDlg = ApisFilmSelectionDialog(self.iface, self.dbm)
        self.newFilmDlg = ApisNewFilmDialog(self.iface)

        # Setup film model
        self.model = QSqlRelationalTableModel(self, self.dbm.db)
        self.model.setTable("film")
        self.model.select()

        while (self.model.canFetchMore()):
            self.model.fetchMore()

        self.setupMapper()

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

        # LineEdits
        self.lineEditMaps = {
            "filmnummer": {
                "editor": self.uiCurrentFilmNumberEdit
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
            }
        }
        for key, item in self.lineEditMaps.items():
            self.mapper.addMapping(item["editor"], self.model.fieldIndex(key))
            item["editor"].textChanged.connect(partial(self.onLineEditChanged, item["editor"]))

        #Text
        self.mapper.addMapping(self.uiCommentsPTxt, self.model.fieldIndex("kommentar"))

        # Date and Times
        self.mapper.addMapping(self.uiFlightDate, self.model.fieldIndex("flugdatum"))
        self.mapper.addMapping(self.uiInitalEntryDate, self.model.fieldIndex("datum_ersteintrag"))
        self.mapper.addMapping(self.uiLastChangesDate, self.model.fieldIndex("datum_aenderung"))
        self.mapper.addMapping(self.uiDepartureTime, self.model.fieldIndex("abflug_zeit"))
        self.mapper.addMapping(self.uiArrivalTime, self.model.fieldIndex("ankunft_zeit"))


        # ComboBox
        self.comboBoxMaps = {
            "aufbewahrungsort": {
                "editor": self.uiArchiveCombo,
                "table": "aufbewahrungsort",
                "modelcolumn": 1
            },
            "kamera": {
                "editor": self.uiCameraCombo,
                "table": "kamera",
                "modelcolumn": 0
            },
            "filmfabrikat": {
                "editor": self.uiFilmMakeCombo,
                "table": "film_fabrikat",
                "modelcolumn": 0
            }
        }
        for key, item in self.comboBoxMaps.items():
            self.mapper.addMapping(item["editor"], self.model.fieldIndex(key))
            self.setupComboBox(item["editor"], item["table"], item["modelcolumn"])

    def setupComboBox(self, editor, table, modelColumn):
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
        #elf.uiArchiveCombo.lineEdit().editingFinished.connect(self.cbValidate)

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
        self.model.setFilter(attribute + " = " + value)
        self.model.select()
        self.mapper.toFirst()

        #QMessageBox.warning(None, "FilnNumber", unicode(res))


    def submitChanges(self):
        self.mapper.submit()


    def onCurrentIndexChanged(self):
        self.uiCurrentFilmCountEdit.setText(str(self.mapper.currentIndex() + 1))

    def onLineEditChanged(self, editor):
        if not self.editMode and not self.initalLoad:
            self.startEditMode()
        if not self.initalLoad:
            editor.setStyleSheet("QLineEdit {background-color: rgb(153, 204, 255);}")
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

    def openFilmSelectionDialog(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.filmSelectionDlg.show()
        # Run the dialog event loop
        result = self.filmSelectionDlg.exec_()
        # See if OK was pressed
        if result:
            # QMessageBox.warning(None, "FilmNumber", self.filmSelectionDlg.filmNumber())
            # self.loadRecordByKeyAttribute("filmnummer", self.filmSelectionDlg.filmNumber())
            # Do something useful here - delete the line containing pass and
            #
            pass

    def openNewFilmDialog(self):
        self.newFilmDlg.show()
        # Run the dialog event loop
        result = self.newFilmDlg.exec_()
        # See if OK was pressed
        if result:

            # TODO AddNewFilm .-..

            # QMessageBox.warning(None, "FilmNumber", self.filmSelectionDlg.filmNumber())
            # self.loadRecordByKeyAttribute("filmnummer", self.filmSelectionDlg.filmNumber())
            # Do something useful here - delete the line containing pass and
            #
            pass

    def addNewFilm(self):
        self.initalLoad = True
        row = self.model.rowCount()
        self.mapper.submit()
        while (self.model.canFetchMore()):
            self.model.fetchMore()

        self.model.insertRow(row)
        self.mapper.setCurrentIndex(row)

        self.initLoad = False

    def saveEdits(self):
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
                                          self.tr("Änderungen wurden vorgenommen!"),
                                          self.tr("Möchten Sie die Änerungen speichern?"),
                                          QMessageBox.Yes | QMessageBox.No ,
                                          QMessageBox.Yes)

            #save or not save
            if result == QMessageBox.Yes:
                self.saveEdits()
            elif result == QMessageBox.No:
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
        self.enableItemsInLayout(self.uiTopHorizontalLayout, True)
        self.enableItemsInLayout(self.uiBottomHorizontalLayout, True)
        self.uiOkBtn.setEnabled(True)
        self.uiSaveBtn.setEnabled(False)
        self.uiCancelBtn.setEnabled(False)
        for editor in self.editorsEdited:
            editor.setStyleSheet("")
        self.editorsEdited = []

    def showEvent(self, evnt):
        pass

class FilmDelegate(QSqlRelationalDelegate):
    def __init__(self):
       QSqlRelationalDelegate.__init__(self)

    def createEditor(self, parent, option, index):
        pass

    def setEditorData(self, editor, index):
        #QMessageBox.warning(None, "Test", str(editor.metaObject().className(index))()) + str

        if editor.metaObject().className() == 'QLineEdit':
            editor.setText(unicode(index.model().data(index, Qt.EditRole)))

        if editor.metaObject().className() == 'QComboBox':
            editor.setEditText(unicode(index.model().data(index, Qt.EditRole)))
        else:
            QSqlRelationalDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        #if editor.metaObject().className() == 'QLineEdit':
            #QMessageBox.warning(None, "Test", unicode(index.data(Qt.DisplayRole)) + ',' + unicode(editor.text()))
            #if unicode(index.data(Qt.DisplayRole)) != unicode(editor.text()):
            #    QMessageBox.warning(None, "Test", unicode(index.data(Qt.DisplayRole)) + ',' + unicode(editor.text()))
            #    model.setData(index, editor.text())
        QSqlRelationalDelegate.setModelData(self, editor, model, index)

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
