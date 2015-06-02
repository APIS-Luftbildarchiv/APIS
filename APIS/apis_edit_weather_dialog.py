# -*- coding: utf-8 -*

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

# --------------------------------------------------------
# Film - Eingabe, Pflege
# --------------------------------------------------------
from apis_weather_form import *

class ApisEditWeatherDialog(QDialog, Ui_apisWeatherDialog):

    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        self.accepted.connect(self.onAccepted)


    #def flightDate(self):
        #return self.uiFlightDate.date()

    #def useLastEntry(self):
        #return self.uiUseLastEntryChk.isChecked()

    #def showEvent(self, evnt):
        #self.uiFlightDate.setDate(QDate.currentDate())
        #self.uiCodeEdit.setText(self.iface.uiWeatherCodeEdit)

    def onAccepted(self):
        self.accept()