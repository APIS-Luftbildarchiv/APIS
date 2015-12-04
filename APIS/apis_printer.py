from PyQt4.QtCore import *
from PyQt4.QtGui import *
#from PyQt4.QtSql import *
from PyQt4.QtXml import *

import os, sys, subprocess

from qgis.core import *


class ApisPrinter():
    def __init__(self, parent, openfile=False, w=210.0, h=297.0, r=300):
        self.parent = parent
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)

        self.comp = QgsComposition(QgsMapSettings())
        self.comp.setPlotStyle(QgsComposition.Print)
        self.comp.setPrintResolution(r)
        #self.comp.setPaperSize(w, h)
        self.openFile = openfile

    def _export(self):
        self.comp.exportAsPDF(self.fileName)

    def _openFile(self):
         if sys.platform == 'linux2':
            subprocess.call(["xdg-open", self.fileName])
         else:
            os.startfile(self.fileName)

    def _setFileName(self, filename, task='Speichern', date=True):
        if date:
            dt = "_" + QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")
        else:
            dt = ""
        saveTask = task
        saveDir = self.settings.value("APIS/working_dir", QDir.home().dirName())
        self.fileName = QFileDialog.getSaveFileName(self.parent, saveTask, saveDir + "\\" + '{0}{1}'.format(filename,dt), '*.pdf')


class ApisListPrinter(ApisPrinter):
    '''
    Input:
    '''
    def setContent(self):
        pass
        #self._setFileName("Filmlist", "Filmliste speichern")
        #self._setFileName("Bildliste", "Bildliste speichern")



class ApisFilmDetailsPrinter(ApisPrinter):
    '''
    Input: List of FilmIDs
    '''
    def printToPdf(self, filmIdList):
        self.filmIdList = filmIdList
        self._save()
        if self.fileName:
            self._prepair()
            #self._export()
            #self._cleanup()
            #if self.openFile:
                #self._openFile()

    def _save(self):
        if len(self.filmIdList) <= 1:
            self._setFileName(u"Filmdetails_{0}".format(self.filmIdList[0]), u"Filmdetails speichern")
        else:
            self._setFileName(u"Filmdetails_Sammlung", u"Filmdetails speichern")

    def _prepair(self):
        try:

            #FIXME template from Settings ':/plugins/APIS/icons/settings.png'
            template = 'C:/Users/Johannes/.qgis2/python/plugins/APIS/composer/templates/test.qpt'
            #if os.path.isfile(template):
            templateDOM = QDomDocument()
            templateDOM.setContent(QFile(template), False)

            #for filmId in self.filmIdList:

            #FIXME load correct Flightpath; from Settings
            #printLayers = []
            #flightpathDir = self.settings.value("APIS/flightpath_dir")
            #uri = flightpathDir + "\\" + self.uiFlightDate.date().toString("yyyy") + "\\" + filmId + "_lin.shp"
            #printLayer = QgsVectorLayer(uri, "FlightPath", "ogr")
            #QgsMapLayerRegistry.instance().addMapLayer(printLayer, False) #False = don't add to Layers (TOC)
            #extent = printLayer.extent()

            #layerset.append(printLayer.id())
            #printLayers.append(printLayer.id())

            #urlWithParams = ' '
            #urlWithParams = 'url=http://wms.jpl.nasa.gov/wms.cgi&layers=global_mosaic&styles=pseudo&format=image/jpeg&crs=EPSG:4326'
            #rlayer = QgsRasterLayer(urlWithParams, 'basemap', 'wms')
            #QgsMapLayerRegistry.instance().addMapLayer(rlayer)
            #printLayers.append(rlayer.id())

            #ms = QgsMapSettings()
            #ms.setExtent(extent)
            #mr.setLayerSet(layerset)

            #mapRectangle = QgsRectangle(140,-28,155,-15)
            #mr.setExtent(extent)

            #comp = QgsComposition(ms)
            #comp.setPlotStyle(QgsComposition.Print)
            #comp.setPrintResolution(300)

            #m = self.mapper.model()
            #r = self.mapper.currentIndex()

            filmDict = {'filmnummer': 'abc'}
            #for c in range(m.columnCount()):
                #filmDict[m.headerData(c, Qt.Horizontal)] = unicode(m.data(m.createIndex(r, c)))
                #QMessageBox.warning(None, "Save", "{0}:{1}".format(colName, value))

            #self.comp.setNumPages(13)
            self.comp.loadFromTemplate(templateDOM, filmDict)
            QMessageBox.warning(None, "Save",self.fileName)
            self.comp.exportAsPDF(self.fileName)
            #self._export()

        except:
            raise IOError



        #composerMap = comp.getComposerMapById(0)
        #composerMap.setKeepLayerSet(True)
        #composerMap.setLayerSet(printLayers)
        #composerMap.renderModeUpdateCachedImage()
        #ms.setLayers(printLayers)

        #if composerMap:
            #QMessageBox.warning(None, "Save", composerMap)
        #composerMap.setKeepLayerSet(True)
        #composerMap.setLayerSet(layerset)






    def _cleanup():
         #FIXME: Delete all alyers (array) not just one layer
         #QgsMapLayerRegistry.instance().removeMapLayer(printLayer.id())
        pass