# -*- coding: utf-8 -*

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from qgis.core import *
from qgis.gui import *
from apis_db_manager import *
import sys, os

from apis_film_number_selection_dialog import *
from apis_search_film_dialog import *
from apis_film_selection_list_dialog import *

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
        self.dbm = dbm
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self)
        self.hide()
        self.canvas = self.iface.mapCanvas()

        self.setPointMapTool = QgsMapToolEmitPoint(self.canvas) #SetPointMapTool(self.canvas)
        self.setPointMapTool.canvasClicked.connect(self.updatePoint)

        self.uiSetCenterPoint.clicked.connect(self.activateSetCenterPoint)

        self.vertexMarker = QgsVertexMarker(self.canvas)
        self.vertexMarker2 = QgsVertexMarker(self.canvas)
        self.vertexMarker.setIconType(3)
        self.vertexMarker2.setIconType(1)
        self.vertexMarker.setColor(QColor(255,153,0))
        self.vertexMarker2.setColor(QColor(255,153,0))
        self.vertexMarker.setIconSize(12)
        self.vertexMarker2.setIconSize(20)
        self.vertexMarker.hide()
        self.vertexMarker2.hide()

        self.filmSelectionDlg = ApisFilmNumberSelectionDialog(self.iface, self.dbm)
        self.uiFilmSelectionBtn.clicked.connect(self.openFilmSelectionDialog)

        self.searchFilmDlg = ApisSearchFilmDialog(self.iface)
        self.uiSearchFilmBtn.clicked.connect(self.openSearchFilmDialog)

    def openFilmSelectionDialog(self):
        """Run method that performs all the real work"""
        self.filmSelectionDlg.show()
        self.filmSelectionDlg.uiFilmNumberEdit.setFocus()
        if self.filmSelectionDlg.exec_():
            if not self.checkFilmNumber(self.filmSelectionDlg.filmNumber()):
                self.uiCurrentFilmNumberEdit.clear()
                self.openFilmSelectionDialog()
                #TODO: DISABLE OTHER CONTROLS
            else:
                self.currentFilmNumber = self.filmSelectionDlg.filmNumber()
                self.uiCurrentFilmNumberEdit.setText(self.currentFilmNumber)
                #TODO: ENABLE OTHER CONTROLS

    def openSearchFilmDialog(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.searchFilmDlg.show()
        if self.searchFilmDlg.exec_():
            model = QSqlRelationalTableModel(self, self.dbm.db)
            model.setTable("film")
            model.setFilter(self.searchFilmDlg.generateSearchQuery())
            model.select()
            while (model.canFetchMore()):
                model.fetchMore()

            if model.rowCount():
                # open film selection list dialog
                searchListDlg = ApisFilmSelectionListDialog(self.iface, model, self)
                if searchListDlg.exec_():
                    #QMessageBox.warning(None, "FilmNumber", unicode(searchListDlg.filmNumberToLoad))
                    #self.loadRecordByKeyAttribute("filmnummer", searchListDlg.filmNumberToLoad)
                    self.currentFilmNumber = searchListDlg.filmNumberToLoad
                    self.uiCurrentFilmNumberEdit.setText(self.currentFilmNumber)
            else:
                QMessageBox.warning(None, u"Film Suche", u"Keine Ergebnisse mit den angegebenen Suchkriterien.")
                self.openSearchFilmDialog()

    def checkFilmNumber(self, value):
        query = QSqlQuery(self.dbm.db)
        qryStr = "SELECT" \
                 "  (SELECT COUNT(*)" \
                 "       FROM film AS t2" \
                 "       WHERE t2.rowid < t1.rowid" \
                 "      ) + (" \
                 "         SELECT COUNT(*)" \
                 "         FROM film AS t3" \
                 "        WHERE t3.rowid = t1.rowid AND t3.rowid < t1.rowid" \
                 "      ) AS rowNum" \
                 "   FROM film AS t1" \
                 "   WHERE filmnummer = '{0}'" \
                 "   ORDER BY t1.rowid ASC".format(value)
        query.exec_(qryStr)
        query.first()
        if query.value(0) != None:
            # Film exists
            return True
        else:
            # Film does not exist
            QMessageBox.warning(None, "Film Nummer", unicode("Der Film mit der Nummer {0} existiert nicht!".format(value)))
            return False

    def activateSetCenterPoint(self):
        if self.uiSetCenterPoint.isChecked():
            self.canvas.setMapTool(self.setPointMapTool)
        else:
            self.canvas.unsetMapTool(self.setPointMapTool)

    def updatePoint(self, point, button):
        self.vertexMarker.setCenter(point)
        self.vertexMarker2.setCenter(point)
        self.uiXCoordinateLbl.setText("{}".format(point.x()))
        self.uiYCoordinateLbl.setText("{}".format(point.y()))
        if not self.vertexMarker.isVisible():
            self.vertexMarker.show()
            self.vertexMarker2.show()


class SetPointMapTool(QgsMapToolEmitPoint):
  def __init__(self, canvas):
      self.canvas = canvas
      QgsMapToolEmitPoint.__init__(self, self.canvas)
      self.vertexMarker = QgsVertexMarker(self.canvas)
      self.vertexMarker.setColor(Qt.red)
      self.vertexMarker.setCursor(Qt.CrossCursor)
      self.reset()

  def reset(self):
      self.centerPoint = None
      self.vertexMarker.hide()
      #self.isEmittingPoint = False
      #self.rubberBand.reset(QGis.Polygon)

  def canvasPressEvent(self, e):
      self.centerPoint = self.toMapCoordinates(e.pos())
      self.vertexMarker.setCenter(self.centerPoint)
      if not self.vertexMarker.isVisible():
        self.vertexMarker.show()
      #self.endPoint = self.startPoint
      #self.isEmittingPoint = True
      #self.showRect(self.startPoint, self.endPoint)

  def canvasReleaseEvent(self, e):
      return
      #self.isEmittingPoint = False
     # r = self.rectangle()
      #if r is not None:
       # print "Rectangle:", r.xMinimum(), r.yMinimum(), r.xMaximum(), r.yMaximum()

  def canvasMoveEvent(self, e):
      return
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

  def deactivate(self):
      super(SetPointMapTool, self).deactivate()
      self.emit(SIGNAL("deactivated()"))