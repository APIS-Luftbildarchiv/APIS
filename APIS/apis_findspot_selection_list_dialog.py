# -*- coding: utf-8 -*

import os, glob

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from PyQt4.QtXml import *

from qgis.core import *

from apis_db_manager import *
from apis_findspot_dialog import *
from functools import partial

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

# --------------------------------------------------------
# Film - Eingabe, Pflege
# --------------------------------------------------------
from apis_findspot_selection_list_form import *
from functools import partial
import subprocess

class ApisFindSpotSelectionListDialog(QDialog, Ui_apisFindSpotSelectionListDialog):
    def __init__(self, iface, dbm):
        QDialog.__init__(self)
        self.iface = iface
        self.dbm = dbm
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)
        self.setupUi(self)

        self.query = None

        self.uiFindSpotListTableV.doubleClicked.connect(self.openFindSpotDialog)

        self.findSpotDlg = None

    def loadFindSpotListBySpatialQuery(self, query=None, info=None):
        if self.query == None:
            self.query = query
        self.model = QStandardItemModel()
        while query.next():
            newRow = []
            rec = query.record()
            for col in range(rec.count()):
                if rec.value(col) == None:
                    value = ''
                else:
                    value = rec.value(col)
                newCol = QStandardItem(unicode(value))
                newRow.append(newCol)

            self.model.appendRow(newRow)

        if self.model.rowCount() < 1:
            QMessageBox.warning(None, "Fundstellen Auswahl", u"Es wurden keine Fundstellen gefunden!")
            return False

        for col in range(rec.count()):
            self.model.setHeaderData(col, Qt.Horizontal, rec.fieldName(col))

        self.setupTable()

        self.uiFindSpotCountLbl.setText(unicode(self.model.rowCount()))
        if info != None:
            self.uiInfoLbl.setText(info)

        return True

    def setupTable(self):
        self.uiFindSpotListTableV.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.uiFindSpotListTableV.setModel(self.model)
        self.uiFindSpotListTableV.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.uiFindSpotListTableV.resizeColumnsToContents()
        self.uiFindSpotListTableV.resizeRowsToContents()
        self.uiFindSpotListTableV.horizontalHeader().setResizeMode(QHeaderView.Stretch)


    def openFindSpotDialog(self, idx):
        findSpotNumber = self.model.item(idx.row(), 1).text()
        siteNumber = self.model.item(idx.row(), 0).text()
        if self.findSpotDlg == None:
            self.findSpotDlg = ApisFindSpotDialog(self.iface, self.dbm)
            self.findSpotDlg.findSpotEditsSaved.connect(self.reloadTable)
        self.findSpotDlg.openInViewMode(siteNumber, findSpotNumber)
        self.findSpotDlg.show()
        # Run the dialog event loop

        if self.findSpotDlg.exec_():
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
        #QMessageBox.warning(None, self.tr(u"Load Site"), self.tr(u"For Site: {0}".format(siteNumber)))

    def reloadTable(self, editsSaved):
        self.query.exec_()
        self.loadFindSpotListBySpatialQuery(self.query)
        #QMessageBox.warning(None, self.tr(u"Load Site"), self.tr(u"Reload Table Now"))
