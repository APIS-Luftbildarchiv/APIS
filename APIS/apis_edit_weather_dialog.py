# -*- coding: utf-8 -*

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

from functools import partial

# --------------------------------------------------------
# Film - Eingabe, Pflege
# --------------------------------------------------------
from apis_weather_form import *

class ApisEditWeatherDialog(QDialog, Ui_apisWeatherDialog):

    def __init__(self, iface, dbm):
        QDialog.__init__(self)
        self.iface = iface
        self.dbm = dbm
        self.setupUi(self)

        self.accepted.connect(self.onAccepted)

        self.comboBoxMaps = {
            "lowcloudamount": {
                "editor": self.uiLowCloudAmountCombo,
                "table": "wetter",
                "modelcolumn": 2,
                "category": "Low Cloud Amount",
                "index": 0
            },
            "visibilitykilometres": {
                "editor": self.uiVisibilityCombo,
                "table": "wetter",
                "modelcolumn": 2,
                "category": "Visibility Kilometres",
                "index": 1
            },
            "lowcloudheight": {
                "editor": self.uiLowCloudHeightCombo,
                "table": "wetter",
                "modelcolumn": 2,
                "category": "Low Cloud Height",
                "index": 2
            },
            "weather": {
                "editor": self.uiWeatherCombo,
                "table": "wetter",
                "modelcolumn": 2,
                "category": "Weather",
                "index": 3
            },
            "remarksmission": {
                "editor": self.uiRemarksMissionCombo,
                "table": "wetter",
                "modelcolumn": 2,
                "category": "Remarks Mission",
                "index": 4
            }#,
            # "remarksweather": {
            #     "editor": self.uiRemarksCombo,
            #     "table": "wetter",
            #     "modelcolumn": 2,
            #     "category": "Remarks Weather",
            #     "indexstart": 5
            # }
        }
        for key, item in self.comboBoxMaps.items():
            #self.mapper.addMapping(item["editor"], self.model.fieldIndex(key))
            self.setupComboBox(item["editor"], item["table"], item["modelcolumn"], item["category"])
            if "index" in item:
                item["editor"].currentIndexChanged.connect(partial(self.updateCode, item["index"], item["editor"]))
            if "indexstart" in item:
                pass


        model = QSqlRelationalTableModel(self, self.dbm.db)
        model.setTable("wetter")
        model.setFilter("category = '{0}'".format("Remarks Weather"))
        model.select()
        self.uiRemarksTableV.setModel(model)

        #self.uiRemarksTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.uiRemarksTableV.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.uiRemarksTableV.verticalHeader().setVisible(False)
        self.uiRemarksTableV.hideColumn(0)
        self.uiRemarksTableV.model().insertColumn(0)

        self.uiRemarksTableV.resizeRowsToContents()
        self.uiRemarksTableV.resizeColumnsToContents()

        #self.uiRemoveRemarkBtn.setDisabled(True)
        #self.uiAddRemarkBtn.clicked.connect(self.addRemark)
        #self.uiRemoveRemarkBtn.clicked.connect(self.removeRemark)

    def updateCode(self, idx, editor):
        code = unicode(self.uiCodeEdit.text())

        mIdx = editor.model().createIndex(editor.currentIndex(), editor.model().fieldIndex("code"))
        code = code[:idx] + unicode(editor.model().data(mIdx)) + code[idx+1:]

        self.uiCodeEdit.setText(code)

    def updateCodeRemarks(self):
        pass

    def addRemark(self):
        #QMessageBox.warning(None, "FilmNumber", unicode(self.uiRemarksCombo.count()))
        vH = self.uiRemarksCombo.view().verticalHeader()
        #QMessageBox.warning(None, "FilmNumber", unicode(vH.count()-vH.hiddenSectionCount()))
        if vH.count()-vH.hiddenSectionCount() > 0:
            currentRow = self.uiRemarksCombo.currentIndex()
            #QMessageBox.warning(None, "FilmNumber", unicode(currentRow))
            self.uiRemarksCombo.setCurrentIndex(currentRow + 1)
            self.uiRemarksCombo.view().hideRow(currentRow)

            rowPosition = self.uiRemarksTable.rowCount()

            self.uiRemarksTable.insertRow(rowPosition)
            m = self.uiRemarksCombo.model()
            self.uiRemarksTable.setItem(rowPosition, 0, QTableWidgetItem(m.data(m.createIndex(currentRow,m.fieldIndex("code")))))
            self.uiRemarksTable.setItem(rowPosition, 1, QTableWidgetItem(m.data(m.createIndex(currentRow,m.fieldIndex("description")))))

            self.uiRemarksTable.sortItems(0)

            self.uiRemarksTable.resizeRowsToContents()
            self.uiRemarksTable.resizeColumnsToContents()
            self.updateCodeRemarks()
            self.uiRemoveRemarkBtn.setEnabled(True)
        else:
            self.uiAddRemarkBtn.setDisabled(True)

    def removeRemark(self):
        if self.uiRemarksTable.selectionModel().hasSelection():
            self.uiAddRemarkBtn.setEnabled(True)
            currentRow = self.uiRemarksTable.currentRow()
            self.uiRemarksTable.removeRow(currentRow)
            self.uiRemarksTable.resizeRowsToContents()
            self.uiRemarksTable.resizeColumnsToContents()

            #QMessageBox.warning(None, "FilmNumber", unicode(vH.count()-vH.hiddenSectionCount()))
        #self.uiRemarksTable.selectionModel().clearSelection()

    def setWeatherCode(self, weatherCode):
        self.uiCodeEdit.setText(weatherCode)
        #ToDo: update combo boxes

        if weatherCode:
            for key, item in self.comboBoxMaps.items():
                if "index" in item:
                    code = weatherCode[item["index"]]
                    m = item["editor"].model()
                    rC = m.rowCount()
                    for r in range(rC):
                        mIdx = m.createIndex(r, m.fieldIndex("code"))
                        if m.data(mIdx) == code:
                            idx = r
                    item["editor"].setCurrentIndex(idx)
                if "indexstart" in item:
                    pass

        # for w in weatherCode:
            # QMessageBox.warning(None, "FilmNumber", w)

    def weatherCode(self):
        return unicode(self.uiCodeEdit.text())

    def weatherDescription(self):
        return unicode(self.uiCodeEdit.text())

    def setupComboBox(self, editor, table, modelColumn, category):
        model = QSqlRelationalTableModel(self, self.dbm.db)
        model.setTable(table)
        model.setFilter("category = '{0}'".format(category))
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

        tv.hideColumn(0)

        tv.resizeColumnsToContents()
        tv.resizeRowsToContents()
        tv.verticalHeader().setVisible(False)
        tv.horizontalHeader().setVisible(True)
        tv.setMinimumWidth(tv.horizontalHeader().length())

        editor.setAutoCompletion(True)
        #editor.lineEdit().setValidator(InListValidator([editor.itemText(i) for i in range(editor.count())], editor.lineEdit(), self))
        #self.uiProducerCombo.lineEdit().editingFinished.connect(self.cbValidate)

    def onAccepted(self):
        self.accept()