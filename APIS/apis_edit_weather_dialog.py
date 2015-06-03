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
                "category": "Weather"
                ,
                "index": 3
            },
            "remarksmission": {
                "editor": self.uiRemarksMissionCombo,
                "table": "wetter",
                "modelcolumn": 2,
                "category": "Remarks Mission",
                "index": 4
            },
            "remarksweather": {
                "editor": self.uiRemarksCombo,
                "table": "wetter",
                "modelcolumn": 2,
                "category": "Remarks Weather"
            }
        }
        for key, item in self.comboBoxMaps.items():
            #self.mapper.addMapping(item["editor"], self.model.fieldIndex(key))
            self.setupComboBox(item["editor"], item["table"], item["modelcolumn"], item["category"])
            if "index" in item:
                item["editor"].currentIndexChanged.connect(partial(self.updateCode, item["index"], item["editor"]))

    def updateCode(self, idx, editor):
        code = unicode(self.uiCodeEdit.text())

        mIdx = editor.model().createIndex(editor.currentIndex(), editor.model().fieldIndex("code"))
        code = code[:idx] + unicode(editor.model().data(mIdx)) + code[idx+1:]

        self.uiCodeEdit.setText(code)

    def setWeatherCode(self, weatherCode):
        self.uiCodeEdit.setText(weatherCode)

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