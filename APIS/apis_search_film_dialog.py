# -*- coding: utf-8 -*

import os

from PyQt4.QtCore import QDate, Qt
from PyQt4.QtGui import *
# from PyQt4.QtSql import *

# from apis_db_manager import *

# from functools import partial

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

# --------------------------------------------------------
# Film - Suche
# --------------------------------------------------------
from apis_search_film_form import *

class ApisSearchFilmDialog(QDialog, Ui_apisSearchFilmDialog):

    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        #self.dbm = dbm
        self.setupUi(self)

        self.accepted.connect(self.onAccepted)

        now = QDate.currentDate()
        self.uiSearchDate.setDate(now)
        self.uiSearchDate.setMaximumDate(now)
        self.uiToDate.setDate(now)
        self.uiToDate.setMaximumDate(now)
        # FIXME next two lines into def => update on change of one of the two Date edits
        self.uiFromDate.setMaximumDate(self.uiToDate.date())
        self.uiToDate.setMinimumDate(self.uiFromDate.date())

        # Signals
        self.uiVerticalChk.stateChanged.connect(self.onFilmModeChange)
        self.uiObliqueChk.stateChanged.connect(self.onFilmModeChange)

        self.uiSearchDate.dateChanged.connect()

        self.uiFromDate.dateChanged.connect()
        self.uiToDate.dateChanged.connect()


    def onFilmModeChange(self):
        verticalState = self.uiVerticalChk.checkState()
        obliqueState = self.uiObliqueChk.checkState()

        if verticalState == Qt.Checked or obliqueState == Qt.Checked:
            self.uiSearchModeTBox.setEnabled(False)
        else:
           self.uiSearchModeTBox.setEnabled(True)

    def onAccepted(self):
        self.accept()