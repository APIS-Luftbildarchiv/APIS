
import os

from PyQt4.QtCore import * #QSettings, QTranslator, QString
from PyQt4.QtGui import *
from PyQt4.QtSql import *

from apis_db_manager import *

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

# --------------------------------------------------------
# Film - Eingabe, Pflege
# --------------------------------------------------------
from apis_film_form import *

class ApisFilmDialog(QDialog, Ui_apisFilmDialog):
    def __init__(self, iface, dbm):
        QDialog.__init__(self)
        self.iface = iface
        self.dbm = dbm
        self.setupUi(self)

        # Signals/Slot Connections
        self.rejected.connect(self.onReject)
        self.uiButtonBox.rejected.connect(self.onReject)
        self.uiButtonBox.accepted.connect(self.onAccept)

        # Setup Sub-Dialogs
        # self.

        # Create model
        self.model = QSqlTableModel(self, self.dbm.db)
        self.model.setTable("film")
        self.model.select()

        self.archiveTView = QTableView()
        self.archiveTView.setModel(self.model)

        self.uiDbTestTableView.setModel(self.model)
        self.uiDbTestTableView.resizeColumnsToContents()

        self.uiArchiveCombo.setView(self.archiveTView)

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
        self.close()

    def showEvent(self, evnt):
        pass