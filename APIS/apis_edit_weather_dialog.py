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

        self.setMode = False

        self.accepted.connect(self.onAccepted)

        self.comboBoxMaps = {
            "lowcloudamount": {
                "editor": self.uiLowCloudAmountCombo,
                "codelbl": self.uiLowCloudAmountValueLbl,
                "table": "wetter",
                "modelcolumn": 2,
                "category": "Low Cloud Amount",
                "index": 0
            },
            "visibilitykilometres": {
                "editor": self.uiVisibilityCombo,
                "codelbl": self.uiVisibilityValueLbl,
                "table": "wetter",
                "modelcolumn": 2,
                "category": "Visibility Kilometres",
                "index": 1
            },
            "lowcloudheight": {
                "editor": self.uiLowCloudHeightCombo,
                "codelbl": self.uiLowCloudHeightValueLbl,
                "table": "wetter",
                "modelcolumn": 2,
                "category": "Low Cloud Height",
                "index": 2
            },
            "weather": {
                "editor": self.uiWeatherCombo,
                "codelbl": self.uiWeatherValueLbl,
                "table": "wetter",
                "modelcolumn": 2,
                "category": "Weather",
                "index": 3
            },
            "remarksmission": {
                "editor": self.uiRemarksMissionCombo,
                "codelbl": self.uiRemarksMissionValueLbl,
                "table": "wetter",
                "modelcolumn": 2,
                "category": "Remarks Mission",
                "index": 4
            },
            "remarksweather": {
                "editor": self.uiRemarksTableV,
                "codelbl": self.uiRemarksValueLbl,
                "table": "wetter",
                "modelcolumn": 2,
                "category": "Remarks Weather",
                "indexstart": 5
            }
        }
        for key, item in self.comboBoxMaps.items():
            if "index" in item:
                self.setupComboBox(item["editor"], item["table"], item["modelcolumn"], item["category"])
                item["editor"].currentIndexChanged.connect(self.generateWeatherCode)
            if "indexstart" in item:
                pass

        model = QSqlRelationalTableModel(self, self.dbm.db)
        model.setTable("wetter")
        model.setFilter("category = '{0}'".format("Remarks Weather"))
        model.select()
        self.uiRemarksTableV.setModel(model)

        #self.uiRemarksTableV.setSelectionMode(QAbstractItemView.SingleSelection)
        self.uiRemarksTableV.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.uiRemarksTableV.verticalHeader().setVisible(False)
        self.uiRemarksTableV.hideColumn(0)
        #self.uiRemarksTableV.model().insertColumn(0)

        self.uiRemarksTableV.resizeRowsToContents()
        self.uiRemarksTableV.resizeColumnsToContents()
        self.uiRemarksTableV.horizontalHeader().setStretchLastSection(True)

        self.uiRemarksTableV.selectionModel().selectionChanged.connect(self.generateWeatherCode)

        #self.uiRemoveRemarkBtn.setDisabled(True)
        #self.uiAddRemarkBtn.clicked.connect(self.addRemark)
        #self.uiRemoveRemarkBtn.clicked.connect(self.removeRemark)

    def generateWeatherCode(self):
        if not self.setMode:
            code = [None]*5
            for key, item in self.comboBoxMaps.items():
                if "index" in item:
                    mIdx = item["editor"].model().createIndex(item["editor"].currentIndex(), item["editor"].model().fieldIndex("code"))
                    c = unicode(item["editor"].model().data(mIdx))
                    code[item["index"]] = c
                    item["codelbl"].setText(c)
                if "indexstart" in item:
                    remarks = []
                    if item["editor"].selectionModel().hasSelection():
                        selIdcs = item["editor"].selectionModel().selectedRows(item["editor"].model().fieldIndex("code"))
                        for i in selIdcs:
                            remarks.append(item["editor"].model().data(i))
                        remarks.sort()
                        item["codelbl"].setText("".join(remarks))
                    else:
                        item["codelbl"].setText("-")

            #code = unicode(self.uiCodeEdit.text())
            #mIdx = editor.model().createIndex(editor.currentIndex(), editor.model().fieldIndex("code"))
            #code = code[:idx] + unicode(editor.model().data(mIdx)) + code[idx+1:]

            self.uiCodeEdit.setText("".join(code) + "".join(remarks))

    def setWeatherCode(self, weatherCode):
        self.setMode = True

        if not weatherCode:
            weatherCode = "9990X"

        self.uiCodeEdit.setText(weatherCode)

        for key, item in self.comboBoxMaps.items():
            if "index" in item:
                code = weatherCode[item["index"]]
                item["codelbl"].setText(code)
                m = item["editor"].model()
                rC = m.rowCount()
                for r in range(rC):
                    mIdx = m.createIndex(r, m.fieldIndex("code"))
                    if m.data(mIdx) == code:
                        idx = r
                item["editor"].setCurrentIndex(idx)
            if "indexstart" in item:
                item["editor"].selectionModel().clearSelection()
                if len(weatherCode) >= item["indexstart"]:
                    item["codelbl"].setText(weatherCode[item["indexstart"]:])
                    m = item["editor"].model()
                    rC = m.rowCount()
                    selection = QItemSelection()
                    for i in range(item["indexstart"], len(weatherCode)):
                        #QMessageBox.warning(None, "FilmNumber", weatherCode[i])
                        for r in range(rC):
                            mIdx = m.createIndex(r, m.fieldIndex("code"))
                            #QMessageBox.warning(None, "WeatherCode", "{0}={1}".format(m.data(mIdx), weatherCode[i]))
                            if m.data(mIdx) == weatherCode[i]:
                                lIdx = m.createIndex(r, 0)
                                rIdx = m.createIndex(r, item["editor"].model().columnCount()-1)
                                rowSelection = QItemSelection(lIdx, rIdx)
                                selection.merge(rowSelection, QItemSelectionModel.Select)
                                break
                    item["editor"].selectionModel().select(selection,  QItemSelectionModel.Select)
                else:
                    item["codelbl"].setText("-")

        self.setMode = False
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