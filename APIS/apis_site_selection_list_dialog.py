# -*- coding: utf-8 -*

import os, glob

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from PyQt4.QtXml import *

from qgis.core import *

from apis_db_manager import *
from apis_site_dialog import *
from functools import partial

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

# --------------------------------------------------------
# Film - Eingabe, Pflege
# --------------------------------------------------------
from apis_site_selection_list_form import *
from functools import partial
import subprocess

class ApisSiteSelectionListDialog(QDialog, Ui_apisSiteSelectionListDialog):
    def __init__(self, iface, dbm):
        QDialog.__init__(self)
        self.iface = iface
        self.dbm = dbm
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)
        self.setupUi(self)

        self.query = None

        self.uiSiteListTableV.doubleClicked.connect(self.openSiteDialog)

        self.siteDlg = None

    def loadSiteListBySpatialQuery(self, query=None):
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
                newCol = QStandardItem(value)
                newRow.append(newCol)

            self.model.appendRow(newRow)

        if self.model.rowCount() < 1:
            QMessageBox.warning(None, "Fundort Auswahl", u"Es wurden keine Fundorte gefunden!")
            return False

        for col in range(rec.count()):
            self.model.setHeaderData(col, Qt.Horizontal, rec.fieldName(col))

        self.setupTable()

        self.uiImageCountLbl.setText(unicode(self.model.rowCount()))

        return True

    def setupTable(self):
        #proxy = SiteNumberSortModel()
        #proxy.setSourceModel(self.model)
        #self.model.sort(0, Qt.AscendingOrder)
        self.uiSiteListTableV.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.uiSiteListTableV.setModel(self.model)
        self.uiSiteListTableV.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.uiSiteListTableV.resizeColumnsToContents()
        self.uiSiteListTableV.resizeRowsToContents()
        self.uiSiteListTableV.horizontalHeader().setResizeMode(QHeaderView.Stretch)


    def openSiteDialog(self, idx):
        siteNumber = self.model.item(idx.row(), 0).text()
        if self.siteDlg == None:
            self.siteDlg = ApisSiteDialog(self.iface, self.dbm)
            self.siteDlg.siteEditsSaved.connect(self.reloadTable)
        self.siteDlg.openInViewMode(siteNumber)
        self.siteDlg.show()
        # Run the dialog event loop

        if self.siteDlg.exec_():
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
        #QMessageBox.warning(None, self.tr(u"Load Site"), self.tr(u"For Site: {0}".format(siteNumber)))

    def reloadTable(self, editsSaved):
        self.query.exec_()
        self.loadSiteListBySpatialQuery(self.query)
        #QMessageBox.warning(None, self.tr(u"Load Site"), self.tr(u"Reload Table Now"))

class SiteNumberSortModel(QSortFilterProxyModel):

    def lessThan(self, left, right):

        lvalue = int(left.data()[4:])
        rvalue = int(right.data()[4:])
        return lvalue < rvalue