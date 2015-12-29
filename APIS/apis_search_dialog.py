# -*- coding: utf-8 -*

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from qgis.core import *
from qgis.gui import *
from apis_db_manager import *
import sys, os, math, string
import os.path

from apis_search_tools import *
from apis_image_selection_list_dialog import *
from apis_image_registry import *

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

# --------------------------------------------------------
# Bild - Eingabe
# --------------------------------------------------------
from apis_search_form import *
class ApisSearchDialog(QDockWidget, Ui_apisSearchDialog):
    def __init__(self, iface, dbm, imageRegistry):
        QDockWidget.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)
        self.dbm = dbm
        self.imageRegistry = imageRegistry
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self)
        self.hide()

        self.visibilityChanged.connect(self.onVisibilityChanged)

        # Spatial Search
        self.spatialSearchTool = RectangleMapTool(self.iface, self.dbm, self.imageRegistry)
        self.spatialSearchTool.setButton(self.uiSpatialSearchBtn)
        self.uiSpatialSearchBtn.setCheckable(True)
        self.uiSpatialSearchBtn.toggled.connect(self.toggleSpatialSearch)

        self.uiSearchByMapLayerCombo.setFilters(QgsMapLayerProxyModel.HasGeometry)
        self.uiSearchByMapLayerBtn.clicked.connect(self.spatialSearchByMapLayer)


        # Attributive Search

    def toggleSpatialSearch(self, isChecked):
        if isChecked:
             self.iface.mapCanvas().setMapTool(self.spatialSearchTool)
             self.iface.messageBar().pushMessage(u"APIS räumliche Suche", u"Klicken Sie auf die Karte oder ziehen Sie ein Rechteck auf, um in der ausgewählten Kategorie zu suchen!", level=QgsMessageBar.INFO)
        else:
            self.iface.mapCanvas().unsetMapTool(self.spatialSearchTool)
            self.iface.actionTouch().trigger()
            self.iface.messageBar().clearWidgets()

    def spatialSearchByMapLayer(self):
        vlayer = self.uiSearchByMapLayerCombo.currentLayer()
        selection = vlayer.selectedFeatures()
        if len(selection) > 0:

            i = 0
            for feature in selection:
                if i == 0:
                    searchGeometry = QgsGeometry.fromWkt(feature.geometry().exportToWkt())
                    searchGeometry.convertToMultiType()
                else:
                    searchGeometry.addPartGeometry(feature.geometry())
                i += 1
                #searchGeometry = searchGeometry.combine(feature.geometry())

            srcCrs = vlayer.crs()
            destCrs = QgsCoordinateReferenceSystem(4312, QgsCoordinateReferenceSystem.EpsgCrsId)
            ct = QgsCoordinateTransform(srcCrs, destCrs)
            searchGeometry.transform(ct)

            #QMessageBox.warning(None, "WKT", "{0}".format(searchGeometry.geometry().partCount()))

            epsg = 4312
            query = QSqlQuery(self.dbm.db)
            qryStr = "select cp.bildnummer as bildnummer, cp.filmnummer as filmnummer, cp.radius as mst_radius, f.weise as weise, f.art_ausarbeitung as art from film as f, luftbild_schraeg_cp AS cp WHERE f.filmnummer = cp.filmnummer AND cp.bildnummer IN (SELECT fp.bildnummer FROM luftbild_schraeg_fp AS fp WHERE NOT IsEmpty(fp.geometry) AND Intersects(GeomFromText('{0}',{1}), fp.geometry) AND rowid IN (SELECT rowid FROM SpatialIndex WHERE f_table_name = 'luftbild_schraeg_fp' AND search_frame = GeomFromText('{0}',{1}) )) UNION ALL SELECT  cp_s.bildnummer AS bildnummer, cp_S.filmnummer AS filmnummer, cp_s.massstab, f_s.weise, f_s.art_ausarbeitung FROM film AS f_s, luftbild_senk_cp AS cp_s WHERE f_s.filmnummer = cp_s.filmnummer AND cp_s.bildnummer IN (SELECT fp_s.bildnummer FROM luftbild_senk_fp AS fp_s WHERE NOT IsEmpty(fp_s.geometry) AND Intersects(GeomFromText('{0}',{1}), fp_s.geometry) AND rowid IN (SELECT rowid FROM SpatialIndex WHERE f_table_name = 'luftbild_senk_fp' AND search_frame = GeomFromText('{0}',{1}) ) ) ORDER BY filmnummer, bildnummer".format(searchGeometry.exportToWkt(), epsg)
            query.exec_(qryStr)

            QMessageBox.warning(None, "Query", "Query finished")


            self.imageSelectionListDlg = ApisImageSelectionListDialog(self.iface, self.dbm, self.imageRegistry)
            res = self.imageSelectionListDlg.loadImageListBySpatialQuery(query)
            if res:
                self.imageSelectionListDlg.show()
                if self.imageSelectionListDlg.exec_():
                    pass

        else:
            self.iface.messageBar().pushMessage(u"Error", u"Bitte selektieren sie zumindest ein Feature im Layer {0} für die Suche!".format(vlayer.name()), level=QgsMessageBar.WARNING, duration=5)

    def onVisibilityChanged(self, isVisible):
        #QMessageBox.warning(None, self.tr(u"SearchDialog Visibility"), u"Visibility Search Dialog: {0}".format(visibility))
        if not isVisible:
            if self.uiSpatialSearchBtn.isChecked():
                self.uiSpatialSearchBtn.toggle()


