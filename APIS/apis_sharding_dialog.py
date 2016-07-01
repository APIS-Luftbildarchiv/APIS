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
from apis_thumb_viewer import *

from functools import partial
import subprocess
import string

from apis_exif2points import Exif2Points


import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/composer")

# --------------------------------------------------------
# Begehung - Eingabe, Pflege
# --------------------------------------------------------
from apis_sharding_form import *

class ApisShardingDialog(QDialog, Ui_apisShardingDialog):

    shardingEditsSaved = pyqtSignal(bool)

    def __init__(self, iface, dbm):
        QDialog.__init__(self)
        self.iface = iface
        self.dbm = dbm
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

        self.uiViewPicturesBtn.clicked.connect(self.viewPictures)
        self.uiViewSketchesBtn.clicked.connect(self.viewSketches)

        self.initalLoad = False

    def openSharding(self, siteNumber, shardingNumber):
        self.initalLoad = True
        self.siteNumber = siteNumber
        self.shardingNumber = shardingNumber

        #QMessageBox.warning(None, self.tr(u"Neu"), self.tr(u"{0}, {1}".format(siteNumber, shardingNumber)))

        # Setup sharding model
        self.model = QSqlRelationalTableModel(self, self.dbm.db)
        self.model.setTable("begehung")
        self.model.setFilter("fundortnummer='{0}' AND begehung='{1}'".format(self.siteNumber, self.shardingNumber))
        res = self.model.select()
        self.setupMapper()
        self.mapper.toFirst()
        self.setKgNameAndCode()

        self.initalLoad = False

    def setKgNameAndCode(self):
        query = QSqlQuery(self.dbm.db)
        qryStr = u"select CASE WHEN katastralgemeinde IS NULL AND katastralgemeindenummer IS NULL THEN '--' ELSE katastralgemeindenummer || ' - ' || katastralgemeinde END AS kg FROM fundort WHERE fundortnummer = '{0}'".format(self.siteNumber)
        query.exec_(qryStr)
        query.first()
        self.uiCadastralCommunityEdit.setText(query.value(0))


    def setupMapper(self):
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
        self.mapper.setItemDelegate(ShardingDelegate())

        self.mapper.setModel(self.model)

        self.mandatoryEditors = [self.uiShardingDate]

        # LineEdits & PlainTextEdits
        self.intValidator = QIntValidator()
        self.doubleValidator = QDoubleValidator()

        self.lineEditMaps = {
            "fundortnummer": {
                "editor": self.uiSiteNumberEdit
            },
            "begehung": {
                "editor": self.uiShardingNumberEdit
            },
            "name":{
                "editor": self.uiNameEdit
            },
            "parzelle":{
                "editor": self.uiPlotPTxt
            },
            "sichtbarkeit":{
                "editor": self.uiVisibilityEdit
            },
            "verbleib":{
                "editor": self.uiWhereaboutsEdit
            },
            "funde":{
                "editor": self.uiFindsPTxt
            },
            "morphologie":{
                "editor": self.uiMorphologyPTxt
            },
            "sonstiges":{
                "editor": self.uiMiscellaneousPTxt
            }
        }
        for key, item in self.lineEditMaps.items():
            self.mapper.addMapping(item["editor"], self.model.fieldIndex(key))
            if "validator" in item:
                item["editor"].setValidator(item["validator"])
            #item["editor"].textChanged.connect(partial(self.onLineEditChanged, item["editor"]))
            item["editor"].textChanged.connect(self.onLineEditChanged)

        # Date and Times
        self.mapper.addMapping(self.uiShardingDate, self.model.fieldIndex("datum"))

        # ComboBox without Model
        self.mapper.addMapping(self.uiShardingTypeCombo, self.model.fieldIndex("begehtyp"))
        self.uiShardingTypeCombo.editTextChanged.connect(self.onLineEditChanged)
        self.uiShardingTypeCombo.setAutoCompletion(True)
        self.uiShardingTypeCombo.lineEdit().setValidator(InListValidator([self.uiShardingTypeCombo.itemText(i) for i in range(self.uiShardingTypeCombo.count())], self.uiShardingTypeCombo.lineEdit(), None, self))

        # ComboBox without Model
        self.mapper.addMapping(self.uiConditionPlantCoverCombo, self.model.fieldIndex("zustand_bewuchs"))
        self.uiConditionPlantCoverCombo.editTextChanged.connect(self.onLineEditChanged)
        self.uiConditionPlantCoverCombo.setAutoCompletion(True)
        self.uiConditionPlantCoverCombo.lineEdit().setValidator(InListValidator([self.uiConditionPlantCoverCombo.itemText(i) for i in range(self.uiConditionPlantCoverCombo.count())], self.uiConditionPlantCoverCombo.lineEdit(), None, self))

        # ComboBox without Model
        self.mapper.addMapping(self.uiConditionLightCombo, self.model.fieldIndex("zustand_licht"))
        self.uiConditionLightCombo.editTextChanged.connect(self.onLineEditChanged)
        self.uiConditionLightCombo.setAutoCompletion(True)
        self.uiConditionLightCombo.lineEdit().setValidator(InListValidator([self.uiConditionLightCombo.itemText(i) for i in range(self.uiConditionLightCombo.count())], self.uiConditionLightCombo.lineEdit(), None, self))

        # ComboBox without Model
        self.mapper.addMapping(self.uiConditionSoilCombo, self.model.fieldIndex("zustand_boden"))
        self.uiConditionSoilCombo.editTextChanged.connect(self.onLineEditChanged)
        self.uiConditionSoilCombo.setAutoCompletion(True)
        self.uiConditionSoilCombo.lineEdit().setValidator(InListValidator([self.uiConditionSoilCombo.itemText(i) for i in range(self.uiConditionSoilCombo.count())], self.uiConditionSoilCombo.lineEdit(), None, self))

        # ComboBox without Model
        self.mapper.addMapping(self.uiConditionMoistureCombo, self.model.fieldIndex("zustand_feuchtigkeit"))
        self.uiConditionMoistureCombo.editTextChanged.connect(self.onLineEditChanged)
        self.uiConditionMoistureCombo.setAutoCompletion(True)
        self.uiConditionMoistureCombo.lineEdit().setValidator(InListValidator([self.uiConditionMoistureCombo.itemText(i) for i in range(self.uiConditionMoistureCombo.count())], self.uiConditionMoistureCombo.lineEdit(), None, self))

        # ComboBox without Model
        self.mapper.addMapping(self.uiConditionRainCombo, self.model.fieldIndex("zustand_abgeregnet"))
        self.uiConditionRainCombo.editTextChanged.connect(self.onLineEditChanged)
        self.uiConditionRainCombo.setAutoCompletion(True)
        self.uiConditionRainCombo.lineEdit().setValidator(InListValidator([self.uiConditionRainCombo.itemText(i) for i in range(self.uiConditionRainCombo.count())], self.uiConditionRainCombo.lineEdit(), None, self))

    def onLineEditChanged(self):
        sender = self.sender()
        if not self.editMode and not self.initalLoad:
            self.startEditMode()
        if not self.initalLoad:
            sender.setStyleSheet("{0} {{background-color: rgb(153, 204, 255);}}".format(sender.metaObject().className()))
            self.editorsEdited.append(sender)

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

    def addNewSharding(self, siteNumber):
        self.initalLoad = True
        self.siteNumber = siteNumber

        # get new sharding number
        query = QSqlQuery(self.dbm.db)
        qryStr = "SELECT CASE WHEN max(begehung) IS NULL THEN 1 ELSE max(begehung)+1 END begehungNeu FROM begehung WHERE fundortnummer='{0}'".format(self.siteNumber)
        query.exec_(qryStr)
        query.first()
        self.shardingNumber = query.value(0)

        self.model = QSqlRelationalTableModel(self, self.dbm.db)
        self.model.setTable("begehung")
        self.model.setFilter("fundortnummer='{0}'".format(self.siteNumber))
        res = self.model.select()
        #self.model.submitAll()
        while (self.model.canFetchMore()):
            self.model.fetchMore()

        row = self.model.rowCount()
        #QMessageBox.information(None, "begehung", "{0}".format(row))
        self.model.insertRow(row)

        #QMessageBox.information(None, "begehung", "{0}".format(self.model.rowCount()))

        self.setupMapper()
        self.mapper.toLast()

        self.addMode = True
        self.startEditMode()


        #self.mapper.submit()


        #self.model.insertRow(row)
        #self.mapper.setCurrentIndex(row)


        self.uiSiteNumberEdit.setText(self.siteNumber)
        self.uiShardingNumberEdit.setText(unicode(self.shardingNumber))
        now = QDate.currentDate()
        self.uiShardingDate.setDate(now)

        self.setKgNameAndCode()

        #QMessageBox.warning(None, self.tr(u"Neu"), self.tr(u"{0}, {1}".format(siteNumber,nn)))

        self.initalLoad = False

    def removeNewSharding(self):
        self.initalLoad = True
        row = self.mapper.currentIndex()
        self.model.removeRow(row+1)
        self.model.submitAll()
        while (self.model.canFetchMore()):
            self.model.fetchMore()
        self.mapper.toLast()
        self.initalLoad = False

    def saveEdits(self):
        #Check Mandatory fields
        flag = False
        for mEditor in self.mandatoryEditors:
            cName = mEditor.metaObject().className()
            if cName == 'QDateEdit':
                value = mEditor.date().toString("yyyy-MM-dd")
            elif cName == 'QLineEdit':
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
        #QMessageBox.information(None, "begehung", "{0}".format(currIdx))
        #now = QDate.currentDate()
        #self.uiLastChangesDate.setDate(now)
        self.mapper.submit()

        self.mapper.setCurrentIndex(currIdx)

        # emit signal
        self.shardingEditsSaved.emit(True)

        self.endEditMode()
        return True

    def cancelEdit(self):
        currIdx = self.mapper.currentIndex()
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
                    #self.close()
                    self.done(1)
                    self.removeNewSharding()
                    self.endEditMode()

                    return True
                else:
                    self.mapper.setCurrentIndex(currIdx)
                    self.endEditMode()
                    return True

    def startEditMode(self):
        self.editMode = True
        self.uiOkBtn.setEnabled(False)
        self.uiSaveBtn.setEnabled(True)
        self.uiCancelBtn.setEnabled(True)
        self.editorsEdited = []
        self.uiShardingDate.setReadOnly(not self.addMode)
        if self.uiShardingDate.isReadOnly():
            self.uiShardingDate.setStyleSheet("background-color: rgb(218, 218, 218);")
        else:
            self.uiShardingDate.setStyleSheet("")


    def endEditMode(self):
        self.editMode = False
        self.addMode = False
        self.uiOkBtn.setEnabled(True)
        self.uiSaveBtn.setEnabled(False)
        self.uiCancelBtn.setEnabled(False)
        self.uiShardingDate.setReadOnly(not self.addMode)
        self.uiShardingDate.setStyleSheet("background-color: rgb(218, 218, 218);")
        for editor in self.editorsEdited:
            cName = editor.metaObject().className()
            if (cName == "QLineEdit" or cName == "QDateEdit") and editor.isReadOnly():
                editor.setStyleSheet("{0} {{background-color: rgb(218, 218, 218);}}".format(cName))
            else:
                editor.setStyleSheet("")
        self.editorsEdited = []

    def viewPictures(self):
        dirName = self.settings.value("APIS/insp_image_dir")
        folderNameType = self.settings.value("APIS/insp_image_foto_dir")
        folderNameSite = self.getFolderNameSite(self.siteNumber)
        path = dirName + u'\\' + folderNameSite + u'\\' + folderNameType

        self.loadInImageViewer(path)

    def viewSketches(self):
        dirName = self.settings.value("APIS/insp_image_dir")
        folderNameType = self.settings.value("APIS/insp_image_sketch_dir")
        folderNameSite = self.getFolderNameSite(self.siteNumber)
        path = dirName + u'\\' + folderNameSite + u'\\' + folderNameType

        self.loadInImageViewer(path)

    def getFolderNameSite(self, siteNumber):
        query = QSqlQuery(self.dbm.db)
        qryStr = u"SELECT trim(katastralgemeinde) || ' ' || trim(katastralgemeindenummer) || '.' || substr('000' || fundortnummer_nn_legacy, -3, 3) AS folderName FROM fundort f WHERE f.fundortnummer='{0}'".format(siteNumber)
        query.exec_(qryStr)
        query.first()
        return query.value(0)

    def loadInImageViewer(self, path):
        dir = QDir(path)
        if dir.exists():
            entryList = dir.entryList(['*.jpg'], QDir.Files)
            if len(entryList) > 0:
                # load in thumb viewer
                # QMessageBox.information(None, u"Begehung", u",".join(entryList))
                imagePathList = []
                for image in entryList:
                    imagePathList.append(path + u'\\' + image)

                widget = QdContactSheet()
                widget.load(imagePathList)
                widget.setWindowTitle("Apis Thumb Viewer")
                widget.setModal(True)
                widget.resize(1000, 600)
                widget.show()
                if widget.exec_():
                    pass
                    # app.exec_()
            else:
                QMessageBox.information(None, u"Begehung", u"Es wurden keine Dateien [*.jpg] für diesen Fundort gefunden.")
        else:
            QMessageBox.information(None, u"Begehung", u"Das Verzeichnis '{0}' wurde nicht gefunden.".format(path))

class ShardingDelegate(QSqlRelationalDelegate):
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
            if index.column() == 23: #sicherheit
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

        #     model.setData(model.createIndex(index.row(), 2), filmnummer[:8]) # filmnummer_hh_jjjj_mm
        #     model.setData(model.createIndex(index.row(), 1), int(index.row())) # filmnummer_nn
        #     model.setData(model.createIndex(index.row(), 0), str(editor.text())) #filmnummer
        #     mil = ""
        #     if filmnummer[2:4] == "19":
        #         mil = "01"
        #     elif filmnummer[2:4] == "20":
        #         mil = "02"
        #     model.setData(model.createIndex(index.row(), 1), mil + filmnummer[4:]) # filmnummer_legacy

        if editor.metaObject().className() == 'QDateEdit':
        #if editor.metaObject().className() == 'QDateEdit':
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
        # elif editor.metaObject().className() == 'QComboBox':
        #     if index.column() == 23: #sicherheit
        #         model.setData(index, editor.currentIndex()+1)
        #     else:
        #         model.setData(index, editor.currentText())
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
