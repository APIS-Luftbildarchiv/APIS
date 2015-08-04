# -*- coding: utf-8 -*

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from qgis.core import *
from apis_db_manager import *
import sys, os


sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

# --------------------------------------------------------
# Bild - Eingabe
# --------------------------------------------------------
from apis_image_mapping_form import *
class ApisImageMappingDialog(QDockWidget, Ui_apisImageMappingDialog):
    def __init__(self, iface, dbm):
        QDockWidget.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self)
        #self.hide()