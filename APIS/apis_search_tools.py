# -*- coding: utf-8 -*

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from qgis.core import *
from qgis.gui import *
from apis_image_selection_list_dialog import *
from apis_image_registry import *

import traceback
import time



class RectangleMapTool(QgsMapToolEmitPoint):
  def __init__(self, iface, dbm, imageRegistry):
      self.iface = iface
      self.canvas = self.iface.mapCanvas()
      self.dbm = dbm
      self.imageRegistry = imageRegistry

      QgsMapToolEmitPoint.__init__(self, self.canvas)
      self.rubberBand = QgsRubberBand(self.canvas, QGis.Polygon)
      self.rubberBand.setColor(QColor(255,128,0, 255))
      self.rubberBand.setFillColor(QColor(255, 128, 0, 128))
      self.rubberBand.setWidth(1)

      #self.vertexMarker = QgsVertexMarker(self.canvas)

      self.reset()

      self.imageSelectionListDlg = ApisImageSelectionListDialog(self.iface, self.dbm, self.imageRegistry)

      self.worker = None

  def reset(self):
      self.startPoint = self.endPoint = None
      self.isEmittingPoint = False
      self.rubberBand.reset(QGis.Polygon)

  def canvasPressEvent(self, e):
      self.startPoint = self.toMapCoordinates(e.pos())
      self.endPoint = self.startPoint
      self.isEmittingPoint = True
      self.showRect(self.startPoint, self.endPoint)

  def canvasReleaseEvent(self, e):
      self.isEmittingPoint = False
      r = self.rectangle()

      #QMessageBox.warning(None, "Bild", u"Punkt: {0}".format(epsg))

      srcCrs = self.canvas.mapSettings().destinationCrs()
      destCrs = QgsCoordinateReferenceSystem(4312, QgsCoordinateReferenceSystem.EpsgCrsId)
      ct = QgsCoordinateTransform(srcCrs, destCrs)
      if r is None:
          #QMessageBox.warning(None, "Bild", u"Punkt: {0}".format(self.endPoint.wellKnownText()))

          p = QgsGeometry.fromPoint(self.endPoint)
          p.transform(ct)
          #QMessageBox.warning(None, "Bild", u"Punkt: {0}".format(self.endPoint.x()))
          #self.openImageSelectionListDialogByLocation(p.exportToWkt(8))
          self.startWorker(p.exportToWkt(8))

      else:
          #.warning(None, "Bild", u"Rechteck: {0}, {1}, {2}, {3}".format(r.xMinimum(), r.yMinimum(), r.xMaximum(), r.yMaximum()))

          r2 = QgsGeometry.fromRect(r)
          r2.transform(ct)
          #QMessageBox.warning(None, "Bild", u"Polygon: {0}".format(r2.exportToWkt(8)))
          #self.openImageSelectionListDialogByLocation(r2.exportToWkt(8))
          self.startWorker(r2.exportToWkt(8))
        #print "Rectangle:", r.xMinimum(), r.yMinimum(), r.xMaximum(), r.yMaximum()

  def openImageSelectionListDialogByLocation(self, query):
      # progressMessageBar = self.iface.messageBar().createMessage("Luftbilder werden gesucht")
      # progress = QProgressBar()
      # progress.setMinimum(0)
      # progress.setMaximum(0)
      # progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
      # progressMessageBar.layout().addWidget(progress)
      # self.iface.messageBar().pushWidget(progressMessageBar, self.iface.messageBar().INFO)
      res = self.imageSelectionListDlg.loadImageListBySpatialQuery(query)
      if res:
          self.imageSelectionListDlg.show()
          if self.imageSelectionListDlg.exec_():
              pass

      self.rubberBand.hide()

  def canvasMoveEvent(self, e):
      if not self.isEmittingPoint:
        return

      self.endPoint = self.toMapCoordinates(e.pos())
      self.showRect(self.startPoint, self.endPoint)

  def showRect(self, startPoint, endPoint):
      self.rubberBand.reset(QGis.Polygon)
      if startPoint.x() == endPoint.x() or startPoint.y() == endPoint.y():
        return

      point1 = QgsPoint(startPoint.x(), startPoint.y())
      point2 = QgsPoint(startPoint.x(), endPoint.y())
      point3 = QgsPoint(endPoint.x(), endPoint.y())
      point4 = QgsPoint(endPoint.x(), startPoint.y())

      self.rubberBand.addPoint(point1, False)
      self.rubberBand.addPoint(point2, False)
      self.rubberBand.addPoint(point3, False)
      self.rubberBand.addPoint(point4, True)    # true to update canvas
      self.rubberBand.show()

  def rectangle(self):
      if self.startPoint is None or self.endPoint is None:
        return None
      elif self.startPoint.x() == self.endPoint.x() or self.startPoint.y() == self.endPoint.y():
        return None

      return QgsRectangle(self.startPoint, self.endPoint)

  #def deactivate(self):
      #super(RectangleMapTool, self).deactivate()
      #self.emit(SIGNAL("deactivated()"))


  def startWorker(self, geometry):
    # create a new worker instance

    if self.worker is None:

        worker = Worker(self.dbm, geometry)

        # configure the QgsMessageBar
        messageBar = self.iface.messageBar().createMessage('Luftbilder werden gesucht ...', )
        progressBar = QtGui.QProgressBar()
        progressBar.setMinimum(0)
        progressBar.setMaximum(0)
        progressBar.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        cancelButton = QtGui.QPushButton()
        cancelButton.setText('Cancel')
        cancelButton.clicked.connect(self.killWorker)
        messageBar.layout().addWidget(progressBar)
        self.progressBar = progressBar
        messageBar.layout().addWidget(cancelButton)
        self.iface.messageBar().pushWidget(messageBar, self.iface.messageBar().INFO)
        self.messageBar = messageBar

        # start the worker in a new thread
        thread = QtCore.QThread(self)
        worker.moveToThread(thread)
        worker.finished.connect(self.workerFinished)
        worker.error.connect(self.workerError)
        #worker.progress.connect(progressBar.setValue)
        thread.started.connect(worker.run)
        thread.start()
        self.thread = thread
        self.worker = worker

  def killWorker(self):
      self.worker.kill()
      self.progressBar.setMaximum(100)
      self.progressBar.setValue(100)

  def workerFinished(self, ret):
    # clean up the worker and thread
    self.worker.deleteLater()
    self.thread.quit()
    self.thread.wait()
    self.thread.deleteLater()
    # remove widget from message bar
    self.iface.messageBar().popWidget(self.messageBar)
    if ret is not None:
        # report the result
        #query = ret
        if not self.worker.killed:
            self.openImageSelectionListDialogByLocation(ret)
        else:
            self.rubberBand.hide()
        #self.iface.messageBar().pushMessage('Result')
    else:
        # notify the user that something went wrong
        self.iface.messageBar().pushMessage('Something went wrong! See the message log for more information.', level=QgsMessageBar.CRITICAL, duration=3)
    self.worker = None

  def workerError(self, e, exception_string):
     QgsMessageLog.logMessage('Worker thread raised an exception:\n'.format(exception_string), level=QgsMessageLog.CRITICAL)


class Worker(QtCore.QObject):
    '''Example worker for calculating the total area of all features in a layer'''
    def __init__(self, dbm, geometry):
        QtCore.QObject.__init__(self)
        self.dbm = dbm
        self.killed = False
        self.geometryWkt = geometry

    def run(self):
        query = None
        try:
            epsg = 4312
            query = QSqlQuery(self.dbm.db)
            qryStr = "select cp.bildnummer as bildnummer, cp.filmnummer as filmnummer, cp.radius as mst_radius, f.weise as weise, f.art_ausarbeitung as art from film as f, luftbild_schraeg_cp AS cp WHERE f.filmnummer = cp.filmnummer AND cp.bildnummer IN (SELECT fp.bildnummer FROM luftbild_schraeg_fp AS fp WHERE NOT IsEmpty(fp.geometry) AND Intersects(GeomFromText('{0}',{1}), fp.geometry) AND rowid IN (SELECT rowid FROM SpatialIndex WHERE f_table_name = 'luftbild_schraeg_fp' AND search_frame = GeomFromText('{0}',{1}) )) UNION ALL SELECT  cp_s.bildnummer AS bildnummer, cp_S.filmnummer AS filmnummer, cp_s.massstab, f_s.weise, f_s.art_ausarbeitung FROM film AS f_s, luftbild_senk_cp AS cp_s WHERE f_s.filmnummer = cp_s.filmnummer AND cp_s.bildnummer IN (SELECT fp_s.bildnummer FROM luftbild_senk_fp AS fp_s WHERE NOT IsEmpty(fp_s.geometry) AND Intersects(GeomFromText('{0}',{1}), fp_s.geometry) AND rowid IN (SELECT rowid FROM SpatialIndex WHERE f_table_name = 'luftbild_senk_fp' AND search_frame = GeomFromText('{0}',{1}) ) ) ORDER BY filmnummer, bildnummer".format(self.geometryWkt, epsg)
            query.exec_(qryStr)
        except Exception, e:
            # forward the exception upstream
            self.error.emit(e, traceback.format_exc())
        self.finished.emit(query)

    def kill(self):
        self.killed = True

    finished = QtCore.pyqtSignal(object)
    error = QtCore.pyqtSignal(Exception, basestring)
