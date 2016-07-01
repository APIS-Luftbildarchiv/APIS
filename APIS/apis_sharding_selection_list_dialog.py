7# -*- coding: utf-8 -*

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from PyQt4.QtXml import *

from qgis.core import *

from apis_db_manager import *
from apis_image_registry import *
from apis_sharding_dialog import *

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

# --------------------------------------------------------
# Begehung - Eingabe, Pflege
# --------------------------------------------------------
from apis_sharding_selection_list_form import *

class ApisShardingSelectionListDialog(QDialog, Ui_apisShardingSelectionListDialog):
    def __init__(self, iface, dbm):
        QDialog.__init__(self)
        self.iface = iface
        self.dbm = dbm
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)
        self.setupUi(self)

        self.siteNumber = None

        self.uiShardingListTableV.doubleClicked.connect(self.openShardingDialog)
        self.uiNewShardingBtn.clicked.connect(self.addNewSharding)

    def loadShardingListBySiteNumber(self, siteNumber):
        self.siteNumber = siteNumber
        self.uiSiteNumberLbl.setText(self.siteNumber)
        if self.siteNumber:
            query = QSqlQuery(self.dbm.db)
            query.prepare("SELECT begehung, datum, name, begehtyp, parzelle, funde FROM begehung WHERE fundortnummer = '{0}' ORDER BY date(datum)".format(self.siteNumber))
            query.exec_()

            self.model = QStandardItemModel()
            while query.next():
                newRow = []
                rec = query.record()
                for col in range(rec.count()):
                    if rec.value(col) == None:
                        value = ''
                    else:
                        value = unicode(rec.value(col))
                    #QMessageBox.warning(None, "test", u"{0}".format(value))
                    newCol = QStandardItem(value)
                    newRow.append(newCol)

                self.model.appendRow(newRow)

            if self.model.rowCount() < 1:
                self.uiShardingCountLbl.setText("0")
                return

            self.uiShardingCountLbl.setText(u"{0}".format(self.model.rowCount()))
            for col in range(rec.count()):
                self.model.setHeaderData(col, Qt.Horizontal, rec.fieldName(col))

            self.setupTable()


    def setupTable(self):
        self.uiShardingListTableV.setModel(self.model)
        self.uiShardingListTableV.setColumnHidden(0, True)
        self.uiShardingListTableV.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.uiShardingListTableV.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.uiShardingListTableV.resizeColumnsToContents()
        self.uiShardingListTableV.resizeRowsToContents()

        self.uiShardingListTableV.horizontalHeader().setResizeMode(QHeaderView.Stretch)

    def openShardingDialog(self, idx):
        shardingNumber = self.model.item(idx.row(), 0).text()
        shardingDlg = ApisShardingDialog(self.iface, self.dbm)
        shardingDlg.shardingEditsSaved.connect(self.reloadShardingList)
        shardingDlg.openSharding(self.siteNumber, shardingNumber)
        # Run the dialog event loop
        res = shardingDlg.exec_()
        #if res:
            # reload the table after closing
            #self.loadShardingListBySiteNumber(self.siteNumber)
        #MessageBox.warning(None, "test", u"{0}".format(res))

    def addNewSharding(self):
        shardingDlg = ApisShardingDialog(self.iface, self.dbm)
        shardingDlg.shardingEditsSaved.connect(self.reloadShardingList)
        # Run the dialog event loop
        shardingDlg.addNewSharding(self.siteNumber)

        res = shardingDlg.exec_()
        #if res:
            # reload the table after closing
            #self.loadShardingListBySiteNumber(self.siteNumber)
        #QMessageBox.warning(None, "test", u"{0}".format(res))

    def reloadShardingList(self):
        self.loadShardingListBySiteNumber(self.siteNumber)