# -*- coding: utf-8 -*

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

# --------------------------------------------------------
# Film - Eingabe, Pflege
# --------------------------------------------------------
from apis_new_film_form import *

class ApisNewFilmDialog(QDialog, Ui_apisNewFilmDialog):

    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        self.accepted.connect(self.onAccepted)

    def flightDate(self):
        return self.uiFlightDate.date()

    def useLastEntry(self):
        return self.uiUseLastEntryChk.isChecked()

    def producer(self):
        return self.uiProducerCombo.currentText()

    def producerCode(self):
        editor = self.uiProducerCombo
        idx = editor.model().createIndex(editor.currentIndex(), editor.model().fieldIndex("id"))
        return unicode(editor.model().data(idx))


    def showEvent(self, evnt):
        self.uiFlightDate.setDate(QDate.currentDate())

    def onAccepted(self):
        self.accept()