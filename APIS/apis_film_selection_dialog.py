# -*- coding: utf-8 -*

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

from apis_db_manager import *

from functools import partial

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

# --------------------------------------------------------
# Film - Eingabe, Pflege
# --------------------------------------------------------
from apis_film_number_selection_form import *

class ApisFilmSelectionDialog(QDialog, Ui_apisFilmNumberSelectionDialog):

    def __init__(self, iface, dbm):
        QDialog.__init__(self)
        self.iface = iface
        self.dbm = dbm
        self.setupUi(self)

        self.accepted.connect(self.onAccepted)

    def filmNumber(self):
        return self.uiFilmNumberEdit.text()

    def onAccepted(self):
        self.accept()