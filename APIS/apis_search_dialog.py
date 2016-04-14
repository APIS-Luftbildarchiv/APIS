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
from apis_site_selection_list_dialog import *
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

        self.uiSearchImageRBtn.toggled.connect(self.setSearchTopic)
        self.uiSearchSiteRBtn.toggled.connect(self.setSearchTopic)
        self.uiSearchFindspotRBtn.toggled.connect(self.setSearchTopic)


        # Attributive Search

        self.setupSearchComboBox(self.uiSearchSiteNumberCombo, "fundort_pnt", "fundortnummer")
        self.setupSearchComboBox(self.uiSearchFilmNumberCombo, "film", "filmnummer")
        self.setupSearchComboBox(self.uiSearchProjectNameCombo, "fundort_pnt", "filmnummer_projekt")
        self.uiSearchSiteNumberBtn.clicked.connect(self.attributeSearchSiteBySiteNumber)
        self.uiSearchSiteNumberCombo.lineEdit().returnPressed.connect(self.attributeSearchSiteBySiteNumber)

    def setSearchTopic(self):
        if self.uiSearchImageRBtn.isChecked():
            self.spatialSearchTool.setTopic('image')
        elif self.uiSearchSiteRBtn.isChecked():
            self.spatialSearchTool.setTopic('site')
        elif self.uiSearchFindspotRBtn.isChecked():
            self.spatialSearchTool.setTopic('findspot')

    def toggleSpatialSearch(self, isChecked):
        if isChecked:
             self.iface.mapCanvas().setMapTool(self.spatialSearchTool)
             self.iface.messageBar().pushMessage(u"APIS räumliche Suche", u"Klicken Sie auf die Karte oder ziehen Sie ein Rechteck auf, um in der ausgewählten Kategorie zu suchen!", level=QgsMessageBar.INFO)
        else:
            self.iface.mapCanvas().unsetMapTool(self.spatialSearchTool)
            self.iface.actionTouch().trigger()
            self.iface.messageBar().clearWidgets()

    def spatialSearchByMapLayer(self):
        if self.uiSpatialSearchBtn.isChecked():
            self.uiSpatialSearchBtn.toggle()
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

            if self.uiSearchImageRBtn.isChecked():
                # LuftbildSuche
                query.prepare("select cp.bildnummer as bildnummer, cp.filmnummer as filmnummer, cp.radius as mst_radius, f.weise as weise, f.art_ausarbeitung as art from film as f, luftbild_schraeg_cp AS cp WHERE f.filmnummer = cp.filmnummer AND cp.bildnummer IN (SELECT fp.bildnummer FROM luftbild_schraeg_fp AS fp WHERE NOT IsEmpty(fp.geometry) AND Intersects(GeomFromText('{0}',{1}), fp.geometry) AND rowid IN (SELECT rowid FROM SpatialIndex WHERE f_table_name = 'luftbild_schraeg_fp' AND search_frame = GeomFromText('{0}',{1}) )) UNION ALL SELECT  cp_s.bildnummer AS bildnummer, cp_S.filmnummer AS filmnummer, cp_s.massstab, f_s.weise, f_s.art_ausarbeitung FROM film AS f_s, luftbild_senk_cp AS cp_s WHERE f_s.filmnummer = cp_s.filmnummer AND cp_s.bildnummer IN (SELECT fp_s.bildnummer FROM luftbild_senk_fp AS fp_s WHERE NOT IsEmpty(fp_s.geometry) AND Intersects(GeomFromText('{0}',{1}), fp_s.geometry) AND rowid IN (SELECT rowid FROM SpatialIndex WHERE f_table_name = 'luftbild_senk_fp' AND search_frame = GeomFromText('{0}',{1}) ) ) ORDER BY filmnummer, bildnummer".format(searchGeometry.exportToWkt(), epsg))
                query.exec_()
                self.imageSelectionListDlg = ApisImageSelectionListDialog(self.iface, self.dbm, self.imageRegistry)
                res = self.imageSelectionListDlg.loadImageListBySpatialQuery(query)
                if res:
                    self.imageSelectionListDlg.show()
                    if self.imageSelectionListDlg.exec_():
                        pass
            elif self.uiSearchSiteRBtn.isChecked():
                # Fundortsuche
                # old query (pnt/pol)
                #qryStr = "SELECT fundortnummer, flurname, katastralgemeinde, fundgewinnung, sicherheit FROM fundort_pnt WHERE fundort_pnt.fundortnummer IN (SELECT DISTINCT fundort_pol.fundortnummer FROM fundort_pol WHERE NOT IsEmpty(fundort_pol.geometry) AND NOT IsEmpty(GeomFromText('{0}',{1})) AND Intersects(GeomFromText('{0}',{1}), fundort_pol.geometry) AND fundort_pol.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'fundort_pol' AND search_frame = GeomFromText('{0}',{1}) ) ) ORDER BY SUBSTR(fundortnummer, 0, 3), CAST(SUBSTR(fundortnummer, 5) AS INTEGER)".format(searchGeometry.exportToWkt(), epsg)
                query.prepare("SELECT fundortnummer, flurname, katastralgemeinde, fundgewinnung, sicherheit FROM fundort WHERE fundortnummer IN (SELECT DISTINCT fo.fundortnummer FROM fundort fo WHERE NOT IsEmpty(fo.geometry) AND NOT IsEmpty(GeomFromText('{0}',{1})) AND Intersects(GeomFromText('{0}',{1}), fo.geometry) AND fo.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'fundort' AND search_frame = GeomFromText('{0}',{1}) ) ) ORDER BY SUBSTR(fundortnummer, 0, 3), CAST(SUBSTR(fundortnummer, 5) AS INTEGER)".format(searchGeometry.exportToWkt(), epsg))
                #
                #qryStr = "select cp.bildnummer as bildnummer, cp.filmnummer as filmnummer, cp.radius as mst_radius, f.weise as weise, f.art_ausarbeitung as art from film as f, luftbild_schraeg_cp AS cp WHERE f.filmnummer = cp.filmnummer AND cp.bildnummer IN (SELECT fp.bildnummer FROM luftbild_schraeg_fp AS fp WHERE NOT IsEmpty(fp.geometry) AND Intersects(GeomFromText('{0}',{1}), fp.geometry) AND rowid IN (SELECT rowid FROM SpatialIndex WHERE f_table_name = 'luftbild_schraeg_fp' AND search_frame = GeomFromText('{0}',{1}) )) UNION ALL SELECT  cp_s.bildnummer AS bildnummer, cp_S.filmnummer AS filmnummer, cp_s.massstab, f_s.weise, f_s.art_ausarbeitung FROM film AS f_s, luftbild_senk_cp AS cp_s WHERE f_s.filmnummer = cp_s.filmnummer AND cp_s.bildnummer IN (SELECT fp_s.bildnummer FROM luftbild_senk_fp AS fp_s WHERE NOT IsEmpty(fp_s.geometry) AND Intersects(GeomFromText('{0}',{1}), fp_s.geometry) AND rowid IN (SELECT rowid FROM SpatialIndex WHERE f_table_name = 'luftbild_senk_fp' AND search_frame = GeomFromText('{0}',{1}) ) ) ORDER BY filmnummer, bildnummer".format(searchGeometry.exportToWkt(), epsg)
                query.exec_()
                self.siteSelectionListDlg = ApisSiteSelectionListDialog(self.iface, self.dbm)
                res = self.siteSelectionListDlg.loadSiteListBySpatialQuery(query)
                if res:
                    self.siteSelectionListDlg.show()
                    if self.siteSelectionListDlg.exec_():
                        pass
            elif self.uiSearchFindspotRBtn.isChecked():
                #Fundstellensuche
                pass
                query.prepare("SELECT fundrotnummer, fundstellenummer, datierung, fundart, fundart_detail, sicherheit, kultur FROM fundstelle WHERE fundortnummer || '.' || fundstellenummer as id1 IN (SELECT DISTINCT fs.fundortnummer || '.' || fs.fundstellenummer as id2 FROM fundstelle fs WHERE NOT IsEmpty(fs.geometry) AND NOT IsEmpty(GeomFromText('{0}',{1})) AND Intersects(GeomFromText('{0}',{1}), fs.geometry) AND fs.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'fundstelle' AND search_frame = GeomFromText('{0}',{1}) ) )".format(searchGeometry.exportToWkt(), epsg))
                query.exec_()
                #self.findSpotSelectionListDlg = ApisFindSpotSelectionListDialog(self.iface, self.dbm)
                #res = self.findSpotSelectionListDlg.loadFindSpotListBySpatialQuery(query)
                #if res:
                #    self.findSpotSelectionListDlg.show()
                #    if self.findSpotSelectionListDlg.exec_():
                #        pass

            #QMessageBox.warning(None, "Query", "Query finished")




        else:
            self.iface.messageBar().pushMessage(u"Error", u"Bitte selektieren sie zumindest ein Feature im Layer {0} für die Suche!".format(vlayer.name()), level=QgsMessageBar.WARNING, duration=5)


    def attributeSearchSiteBySiteNumber(self):
        # Fundortsuche
        siteNumberSearchValue = self.uiSearchSiteNumberCombo.lineEdit().text()
        query = QSqlQuery(self.dbm.db)
        query.prepare("SELECT fundortnummer, flurname, katastralgemeinde, fundgewinnung, sicherheit FROM fundort WHERE fundortnummer LIKE '%{0}%' ORDER BY land, fundortnummer_nn".format(siteNumberSearchValue))
        # qryStr = "select cp.bildnummer as bildnummer, cp.filmnummer as filmnummer, cp.radius as mst_radius, f.weise as weise, f.art_ausarbeitung as art from film as f, luftbild_schraeg_cp AS cp WHERE f.filmnummer = cp.filmnummer AND cp.bildnummer IN (SELECT fp.bildnummer FROM luftbild_schraeg_fp AS fp WHERE NOT IsEmpty(fp.geometry) AND Intersects(GeomFromText('{0}',{1}), fp.geometry) AND rowid IN (SELECT rowid FROM SpatialIndex WHERE f_table_name = 'luftbild_schraeg_fp' AND search_frame = GeomFromText('{0}',{1}) )) UNION ALL SELECT  cp_s.bildnummer AS bildnummer, cp_S.filmnummer AS filmnummer, cp_s.massstab, f_s.weise, f_s.art_ausarbeitung FROM film AS f_s, luftbild_senk_cp AS cp_s WHERE f_s.filmnummer = cp_s.filmnummer AND cp_s.bildnummer IN (SELECT fp_s.bildnummer FROM luftbild_senk_fp AS fp_s WHERE NOT IsEmpty(fp_s.geometry) AND Intersects(GeomFromText('{0}',{1}), fp_s.geometry) AND rowid IN (SELECT rowid FROM SpatialIndex WHERE f_table_name = 'luftbild_senk_fp' AND search_frame = GeomFromText('{0}',{1}) ) ) ORDER BY filmnummer, bildnummer".format(searchGeometry.exportToWkt(), epsg)
        query.exec_()
        self.siteSelectionListDlg = ApisSiteSelectionListDialog(self.iface, self.dbm)
        res = self.siteSelectionListDlg.loadSiteListBySpatialQuery(query)
        if res:
            self.siteSelectionListDlg.show()
            if self.siteSelectionListDlg.exec_():
                pass

    def attributeSearchSiteByFilmNumber(self):

        #check if filmNumber isFilm
        #get weise of film
        filmType = "senk."

        if filmType == u"senk.":
            fromTable = "luftbild_senk_fp"
        elif filmType == u"schräg":
            fromTable = "luftbild_schraeg_fp"
        else:
            # FIXME Introduce Error System
            sys.exit()
        query = QSqlQuery(self.dbm.db)
        query.prepare(
            "SELECT fundortnummer, flurname, katastralgemeinde, fundgewinnung, sicherheit FROM fundort WHERE fundortnummer IN (SELECT DISTINCT fo.fundortnummer FROM fundort fo, {0} WHERE fo.geometry IS NOT NULL AND {0}.geometry IS NOT NULL AND {0}.filmnummer = '{1}' AND Intersects({0}.geometry, fo.geometry) AND fo.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'fundort' AND search_frame = {0}.geometry))".format(
                fromTable, self.uiCurrentFilmNumberEdit.text()))
        query.exec_()

        res = self.siteSelectionListDlg.loadSiteListBySpatialQuery(query)
        if res:
            self.siteSelectionListDlg.show()
            if self.siteSelectionListDlg.exec_():
                pass

    def setupSearchComboBox(self, editor, table, column):
        model = QSqlQueryModel(self)
        model.setQuery("SELECT DISTINCT {0} FROM {1}".format(column, table), self.dbm.db)

        tv = QTableView()
        editor.setView(tv)

        tv.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        tv.setSelectionMode(QAbstractItemView.SingleSelection)
        tv.setSelectionBehavior(QAbstractItemView.SelectRows)
        tv.setAutoScroll(False)

        editor.setModel(model)

        editor.setModelColumn(0)
        editor.setInsertPolicy(QComboBox.NoInsert)

        tv.resizeColumnsToContents()
        tv.resizeRowsToContents()
        tv.verticalHeader().setVisible(False)
        tv.horizontalHeader().setVisible(True)
        # tv.setMinimumWidth(tv.horizontalHeader().length())
        tv.horizontalHeader().setResizeMode(QHeaderView.Stretch)

        editor.setAutoCompletion(True)
        editor.setCurrentIndex(-1)

    def onVisibilityChanged(self, isVisible):
        #QMessageBox.warning(None, self.tr(u"SearchDialog Visibility"), u"Visibility Search Dialog: {0}".format(visibility))
        if not isVisible:
            if self.uiSpatialSearchBtn.isChecked():
                self.uiSpatialSearchBtn.toggle()


