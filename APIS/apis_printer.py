#from PyQt4.QtCore import *
#from PyQt4.QtGui import *
#from PyQt4.QtSql import *
#from PyQt4.QtXml import *

from qgis.core import *

class ApisPrinter():
    def __init__(self):
        pass

    def setupPage(self, w=210.0, h=297.0, r=300):
        self.comp = QgsComposition(QgsMapSettings())
        self.comp.setPlotStyle(QgsComposition.Print)
        self.comp.setPrintResolution(r)
        self.comp.setPaperSize(w, h)

class ApisListPrinter(ApisPrinter):

    def __init__(self):
        pass

class ApisFilmDetailsPrinter(ApisPrinter):
    def __init__(self):
        pass

class ApisMultipleFilmsDetailsPrinter(ApisPrinter):
     def __init__(self):
        pass