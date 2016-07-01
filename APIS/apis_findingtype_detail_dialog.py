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
from apis_findingtype_detail_form import *

class ApisFindingTypeDetailDialog(QDialog, Ui_apisFindingTypeDetailDialog):

    def __init__(self, iface, dbm):
        QDialog.__init__(self)
        self.iface = iface
        self.dbm = dbm
        self.setupUi(self)

        self.setMode = False

        self.accepted.connect(self.onAccepted)


    def loadList(self, findingType, findingTypeDetail):

        self.uiFindingTypeEdit.setText(findingType)
        self.uiFindingTypeDetailEdit.setText(findingTypeDetail)
        res = self.loadListForFindingType(findingType.strip())

        if res:
            self.setSelectionForFindingTypeDetail(findingTypeDetail.strip())
            return True
        else:
            return False

    def loadListForFindingType(self, findingType):
        model = QSqlRelationalTableModel(self, self.dbm.db)
        model.setTable(u"fundart")
        model.setFilter(u"fundart = '{0}' AND fundart_detail IS NOT NULL".format(findingType))
        model.select()

        if model.rowCount() < 1:
            QMessageBox.warning(None, "Result", u"Für die Fundart '{0}' wurden keine Detail Einträge gefunden.".format(findingType))
            return False

        self.uiFindingTypeDetailTableV.setModel(model)

        #self.uiRemarksTableV.setSelectionMode(QAbstractItemView.SingleSelection)
        self.uiFindingTypeDetailTableV.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.uiFindingTypeDetailTableV.verticalHeader().setVisible(False)
        self.uiFindingTypeDetailTableV.hideColumn(0)
        if findingType != "Siedlung":
            self.uiFindingTypeDetailTableV.hideColumn(2)
        #self.uiRemarksTableV.model().insertColumn(0)

        self.uiFindingTypeDetailTableV.resizeRowsToContents()
        self.uiFindingTypeDetailTableV.resizeColumnsToContents()
        self.uiFindingTypeDetailTableV.horizontalHeader().setStretchLastSection(True)

        self.uiFindingTypeDetailTableV.selectionModel().selectionChanged.connect(self.generateFindingTypeDetail)

        return True

    def setSelectionForFindingTypeDetail(self, findingTypeDetail):
        self.setMode = True
        if len(findingTypeDetail) > 0:
            findingTypeDetailList = findingTypeDetail.split(',')
            #QMessageBox.warning(None, "not found", u"{0}, '{1}'".format(len(findingTypeDetailList),u",".join(findingTypeDetailList)))
            e = self.uiFindingTypeDetailTableV
            sm = e.selectionModel()
            sm.clearSelection()

            m = self.uiFindingTypeDetailTableV.model()
            rC = m.rowCount()
            selection = QItemSelection()

            notFound = []
            for detail in findingTypeDetailList:
                found = False
                for r in range(rC):
                    mIdx = m.createIndex(r, m.fieldIndex("fundart_detail"))
                    # QMessageBox.warning(None, "WeatherCode", "{0}={1}".format(m.data(mIdx), weatherCode[i]))
                    if m.data(mIdx).lower() == detail.lower():
                        lIdx = m.createIndex(r, 0)
                        rIdx = m.createIndex(r, m.columnCount() - 1)
                        rowSelection = QItemSelection(lIdx, rIdx)
                        selection.merge(rowSelection, QItemSelectionModel.Select)
                        found = True
                        break
                if not found:
                    notFound.append(detail)
                sm.select(selection, QItemSelectionModel.Select)
            #QMessageBox.warning(None, "not found", u"{0}".format(len(notFound)))
            if len(notFound) > 0:
                QMessageBox.warning(None, u"Fundart Details", u"Die folgenden Einträge wurden nicht gefunden. Bitte wählen Sie von den verfügbaren Einträgen aus oder fügen Sie diese manuell zur Tabelle 'fundart' hinzu. [{0}]".format(u", ".join(notFound)))

        self.setMode = False


    def generateFindingTypeDetail(self):
        e = self.uiFindingTypeDetailTableV
        sm = e.selectionModel()
        details = []
        if sm.hasSelection():
            selIdcs = sm.selectedRows(e.model().fieldIndex("fundart_detail"))
            for i in selIdcs:
                details.append(e.model().data(i))
            details.sort()
            self.uiFindingTypeDetailNewEdit.setText(u",".join(details))
        else:
            self.uiFindingTypeDetailNewEdit.setText("")

    def getFindingTypeDetailText(self):
        return self.uiFindingTypeDetailNewEdit.text()

        # self.setMode = False
        #
        #
        #
        # self.comboBoxMaps = {
        #     "lowcloudamount": {
        #         "editor": self.uiLowCloudAmountCombo,
        #         "codelbl": self.uiLowCloudAmountValueLbl,
        #         "table": "wetter",
        #         "modelcolumn": 2,
        #         "category": "Low Cloud Amount",
        #         "index": 0
        #     },
        #     "visibilitykilometres": {
        #         "editor": self.uiVisibilityCombo,
        #         "codelbl": self.uiVisibilityValueLbl,
        #         "table": "wetter",
        #         "modelcolumn": 2,
        #         "category": "Visibility Kilometres",
        #         "index": 1
        #     },
        #     "lowcloudheight": {
        #         "editor": self.uiLowCloudHeightCombo,
        #         "codelbl": self.uiLowCloudHeightValueLbl,
        #         "table": "wetter",
        #         "modelcolumn": 2,
        #         "category": "Low Cloud Height",
        #         "index": 2
        #     },
        #     "weather": {
        #         "editor": self.uiWeatherCombo,
        #         "codelbl": self.uiWeatherValueLbl,
        #         "table": "wetter",
        #         "modelcolumn": 2,
        #         "category": "Weather",
        #         "index": 3
        #     },
        #     "remarksmission": {
        #         "editor": self.uiRemarksMissionCombo,
        #         "codelbl": self.uiRemarksMissionValueLbl,
        #         "table": "wetter",
        #         "modelcolumn": 2,
        #         "category": "Remarks Mission",
        #         "index": 4
        #     },
        #     "remarksweather": {
        #         "editor": self.uiRemarksTableV,
        #         "codelbl": self.uiRemarksValueLbl,
        #         "table": "wetter",
        #         "modelcolumn": 2,
        #         "category": "Remarks Weather",
        #         "indexstart": 5
        #     }
        # }
        # for key, item in self.comboBoxMaps.items():
        #     if "index" in item:
        #         self.setupComboBox(item["editor"], item["table"], item["modelcolumn"], item["category"])
        #         item["editor"].currentIndexChanged.connect(self.generateWeatherCode)
        #     if "indexstart" in item:
        #         pass
        #
        # model = QSqlRelationalTableModel(self, self.dbm.db)
        # model.setTable("wetter")
        # model.setFilter("category = '{0}'".format("Remarks Weather"))
        # model.select()
        # self.uiRemarksTableV.setModel(model)
        #
        # #self.uiRemarksTableV.setSelectionMode(QAbstractItemView.SingleSelection)
        # self.uiRemarksTableV.setSelectionBehavior(QAbstractItemView.SelectRows)
        # self.uiRemarksTableV.verticalHeader().setVisible(False)
        # self.uiRemarksTableV.hideColumn(0)
        # #self.uiRemarksTableV.model().insertColumn(0)
        #
        # self.uiRemarksTableV.resizeRowsToContents()
        # self.uiRemarksTableV.resizeColumnsToContents()
        # self.uiRemarksTableV.horizontalHeader().setStretchLastSection(True)
        #
        # self.uiRemarksTableV.selectionModel().selectionChanged.connect(self.generateWeatherCode)

        #self.uiRemoveRemarkBtn.setDisabled(True)
        #self.uiAddRemarkBtn.clicked.connect(self.addRemark)
        #self.uiRemoveRemarkBtn.clicked.connect(self.removeRemark)

    # def generateWeatherCode(self):
    #     if not self.setMode:
    #         code = [None]*5
    #         for key, item in self.comboBoxMaps.items():
    #             if "index" in item:
    #                 mIdx = item["editor"].model().createIndex(item["editor"].currentIndex(), item["editor"].model().fieldIndex("code"))
    #                 c = unicode(item["editor"].model().data(mIdx))
    #                 code[item["index"]] = c
    #                 item["codelbl"].setText(c)
    #             if "indexstart" in item:
    #                 remarks = []
    #                 if item["editor"].selectionModel().hasSelection():
    #                     selIdcs = item["editor"].selectionModel().selectedRows(item["editor"].model().fieldIndex("code"))
    #                     for i in selIdcs:
    #                         remarks.append(item["editor"].model().data(i))
    #                     remarks.sort()
    #                     item["codelbl"].setText("".join(remarks))
    #                 else:
    #                     item["codelbl"].setText("-")
    #
    #         #code = unicode(self.uiCodeEdit.text())
    #         #mIdx = editor.model().createIndex(editor.currentIndex(), editor.model().fieldIndex("code"))
    #         #code = code[:idx] + unicode(editor.model().data(mIdx)) + code[idx+1:]
    #
    #         self.uiCodeEdit.setText("".join(code) + "".join(remarks))
    #         self.generateWeatherDescription()
    #
    # def setWeatherCode(self, weatherCode):
    #     self.setMode = True
    #
    #     if not weatherCode:
    #         weatherCode = "9990X"
    #
    #     self.uiCodeEdit.setText(weatherCode)
    #
    #     for key, item in self.comboBoxMaps.items():
    #         if "index" in item:
    #             code = weatherCode[item["index"]]
    #             item["codelbl"].setText(code)
    #             m = item["editor"].model()
    #             rC = m.rowCount()
    #             for r in range(rC):
    #                 mIdx = m.createIndex(r, m.fieldIndex("code"))
    #                 if m.data(mIdx) == code:
    #                     idx = r
    #             item["editor"].setCurrentIndex(idx)
    #         if "indexstart" in item:
    #             item["editor"].selectionModel().clearSelection()
    #             if len(weatherCode) >= item["indexstart"]:
    #                 item["codelbl"].setText(weatherCode[item["indexstart"]:])
    #                 m = item["editor"].model()
    #                 rC = m.rowCount()
    #                 selection = QItemSelection()
    #                 for i in range(item["indexstart"], len(weatherCode)):
    #                     #QMessageBox.warning(None, "FilmNumber", weatherCode[i])
    #                     for r in range(rC):
    #                         mIdx = m.createIndex(r, m.fieldIndex("code"))
    #                         #QMessageBox.warning(None, "WeatherCode", "{0}={1}".format(m.data(mIdx), weatherCode[i]))
    #                         if m.data(mIdx) == weatherCode[i]:
    #                             lIdx = m.createIndex(r, 0)
    #                             rIdx = m.createIndex(r, item["editor"].model().columnCount()-1)
    #                             rowSelection = QItemSelection(lIdx, rIdx)
    #                             selection.merge(rowSelection, QItemSelectionModel.Select)
    #                             break
    #                 item["editor"].selectionModel().select(selection,  QItemSelectionModel.Select)
    #             else:
    #                 item["codelbl"].setText("-")
    #
    #     self.setMode = False
    #     self.generateWeatherDescription()
    #
    # def generateWeatherDescription(self):
    #     weatherCode = self.uiCodeEdit.text()
    #     code = []
    #     idx = 0
    #     query = QSqlQuery(self.dbm.db)
    #     for c in weatherCode:
    #         for key, item in self.comboBoxMaps.items():
    #             if "index" in item:
    #                 if idx == item["index"]:
    #                     code.append({'code': c, 'category': item["category"]})
    #                     break
    #             elif "indexstart" in item:
    #                 if idx >= item["indexstart"]:
    #                     code.append({'code': c, 'category': item["category"]})
    #                     break
    #         idx += 1
    #     self.uiDescriptionPTxt.clear()
    #     pos = 0
    #     for c in code:
    #         pos += 1
    #         qryStr = "select description from wetter where category = '{0}' and code = '{1}' limit 1".format(c['category'], c['code'])
    #         query.exec_(qryStr)
    #         query.first()
    #         fn = query.value(0)
    #         if pos <= 6:
    #             self.uiDescriptionPTxt.appendPlainText(c['category'] + ': ' + fn)
    #         else:
    #             self.uiDescriptionPTxt.insertPlainText('; ' + fn)
    #
    # def weatherCode(self):
    #     return unicode(self.uiCodeEdit.text())
    #
    # def weatherDescription(self):
    #     return unicode(self.uiDescriptionPTxt.toPlainText())
    #
    # def setupComboBox(self, editor, table, modelColumn, category):
    #     model = QSqlRelationalTableModel(self, self.dbm.db)
    #     model.setTable(table)
    #     model.setFilter("category = '{0}'".format(category))
    #     model.select()
    #
    #     tv = QTableView()
    #     editor.setView(tv)
    #
    #     tv.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    #     tv.setSelectionMode(QAbstractItemView.SingleSelection)
    #     tv.setSelectionBehavior(QAbstractItemView.SelectRows)
    #     tv.setAutoScroll(False)
    #
    #     editor.setModel(model)
    #
    #     editor.setModelColumn(modelColumn)
    #     editor.setInsertPolicy(QComboBox.NoInsert)
    #
    #     tv.hideColumn(0)
    #
    #     tv.resizeColumnsToContents()
    #     tv.resizeRowsToContents()
    #     tv.verticalHeader().setVisible(False)
    #     tv.horizontalHeader().setVisible(True)
    #     tv.setMinimumWidth(tv.horizontalHeader().length())
    #
    #     editor.setAutoCompletion(True)
    #     #editor.lineEdit().setValidator(InListValidator([editor.itemText(i) for i in range(editor.count())], editor.lineEdit(), self))
    #     #self.uiProducerCombo.lineEdit().editingFinished.connect(self.cbValidate)

    def onAccepted(self):
        self.accept()