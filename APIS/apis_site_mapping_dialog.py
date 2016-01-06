# -*- coding: utf-8 -*

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from qgis.core import *
from qgis.gui import *
from apis_db_manager import *
import sys, os, math, string
import os.path

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

# --------------------------------------------------------
# Bild - Eingabe
# --------------------------------------------------------
from apis_site_mapping_form import *
class ApisSiteMappingDialog(QDockWidget, Ui_apisSiteMappingDialog):
    def __init__(self, iface, dbm):
        QDockWidget.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)
        self.dbm = dbm
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self)
        self.hide()

        self.uiSiteMappingModesGrp.setEnabled(False)

        self.uiAddToSiteManuallyGrp.setVisible(False)
        self.uiAddToSiteByIntersectionGrp.setVisible(False)

        self.visibilityChanged.connect(self.onVisibilityChanged)

        self.uiNewSiteYesRBtn.toggled.connect(self.onNewSiteChanged)
        self.uiNewSiteNoRBtn.toggled.connect(self.onNewSiteChanged)

    def onNewSiteChanged(self):
        if self.uiNewSiteYesRBtn.isChecked():
            # Add New Site
            self.uiNewSiteInterpretationGrp.setEnabled(True)
            self.uiSiteMappingModesGrp.setEnabled(False)
        else:
            self.uiNewSiteInterpretationGrp.setEnabled(False)
            self.uiSiteMappingModesGrp.setEnabled(True)
            #Add To Existing Site


    def onVisibilityChanged(self, isVisible):
        #QMessageBox.warning(None, self.tr(u"SearchDialog Visibility"), u"Visibility Search Dialog: {0}".format(visibility))
        if not isVisible:
            pass
            #if self.uiSpatialSearchBtn.isChecked():
            #    self.uiSpatialSearchBtn.toggle()


class PointSquareMapTool(QgsMapToolEmitPoint):
    finished = pyqtSignal(object, object)

    def __init__(self, canvas):
        QgsMapToolEmitPoint.__init__(self, canvas)
        self.canvas = canvas
        self.rb = None
        self.vm = None
        self.cp = None
        self.isEmittingPoint = False
        self.cursor = Qt.CrossCursor

    def reset(self):
        pass
        #self.centerPoint = None
        #self.vertexMarker.hide()
        #self.isEmittingPoint = False
        #self.rubberBand.reset(QGis.Polygon)

    def canvasPressEvent(self, e):
        return
        #self.cp = self.toMapCoordinates(e.pos())

        #self.vm = QgsVertexMarker(self.canvas)
        #self.vm.setCenter(self.cp)



        #self.showRect(self.startPoint, self.endPoint)

    def canvasReleaseEvent(self, e):
        self.centerPoint = self.toMapCoordinates(e.pos())
        point = None
        polygon = None
        self.finished.emit(point, polygon)
        return

        # r = self.rectangle()
        # if r is not None:
        # print "Rectangle:", r.xMinimum(), r.yMinimum(), r.xMaximum(), r.yMaximum()

    def canvasMoveEvent(self, e):
        return
        #self.showRect(self.startPoint, self.endPoint)
        #if not self.isEmittingPoint:
            #return

        #self.endPoint = self.toMapCoordinates(e.pos())
        #self.showRect(self.startPoint, self.endPoint)

    def rectangle(self):
        if self.startPoint is None or self.endPoint is None:
            return None
        elif self.startPoint.x() == self.endPoint.x() or self.startPoint.y() == self.endPoint.y():
            return None

        return QgsRectangle(self.startPoint, self.endPoint)

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        super(PointSquareMapTool, self).deactivate()
        self.emit(SIGNAL("deactivated()"))

#class PolygonPointMapTool(QgsMapToolEmitPoint):
