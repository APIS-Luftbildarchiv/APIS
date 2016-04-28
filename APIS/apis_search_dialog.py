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

        self.setupSearchComboBox(self.uiSearchByCadastralCommunityCombo, "katastralgemeinden", "katastralgemeindenummer, katastralgemeindename", "katastralgemeindenummer, katastralgemeindename", 1)
        self.uiSearchByCadastralCommunityCombo.currentIndexChanged.connect(self.joinRowValues)
        self.uiSearchByCadastralCommunityBtn.clicked.connect(self.spatialSearchByCadastralCommunity)
        self.uiSearchByCadastralCommunityCombo.lineEdit().returnPressed.connect(self.spatialSearchByCadastralCommunity)

        self.setupSearchComboBox(self.uiSearchByCountryCombo, "osm_boundaries", "code, name", "code", 1)
        self.uiSearchByCountryCombo.currentIndexChanged.connect(self.joinRowValues)

        # Attributive Search

        # Fundort

        self.setupSearchComboBox(self.uiSearchSiteNumberCombo, "fundort", "fundortnummer", "land, fundortnummer_nn")
        self.setupSearchComboBox(self.uiSearchFilmNumberCombo, "film", "filmnummer", "filmnummer")
        self.setupSearchComboBox(self.uiSearchProjectNameCombo, "fundort", "filmnummer_projekt", "filmnummer_projekt")

        self.uiSearchSiteNumberBtn.clicked.connect(self.attributeSearchSiteBySiteNumber)
        self.uiSearchSiteNumberCombo.lineEdit().returnPressed.connect(self.attributeSearchSiteBySiteNumber)

        self.uiSearchFilmNumberBtn.clicked.connect(self.attributeSearchSiteByFilmNumber)
        self.uiSearchFilmNumberCombo.lineEdit().returnPressed.connect(self.attributeSearchSiteByFilmNumber)

        self.uiSearchYearBtn.clicked.connect(self.attributeSearchSiteByFilmsOfYear)
        self.uiSearchYearDate.lineEdit().returnPressed.connect(self.attributeSearchSiteByFilmsOfYear)

        self.uiSearchProjectNameBtn.clicked.connect(self.attributeSearchSiteByProjectName)
        self.uiSearchProjectNameCombo.lineEdit().returnPressed.connect(self.attributeSearchSiteByProjectName)

        # Fundstelle

        self.uiSearchFindSpotBtn.setEnabled(True)
        self.uiSearchFindSpotBtn.clicked.connect(self.attributeSearchFindSpot)

        # Datierung

        self.uiPeriodChk.setCheckState(Qt.Unchecked)
        self.uiPeriodDetailsChk.setCheckState(Qt.Unchecked)

        self.uiPeriodDetailsChk.setEnabled(False)

        self.uiPeriodCombo.setEnabled(False)
        self.uiPeriodDetailsCombo.setEnabled(False)

        self.uiPeriodChk.stateChanged.connect(self.onPeriodChkChanged)
        self.uiPeriodDetailsChk.stateChanged.connect(self.onPeriodDetailsChkChanged)

        self.uiTimeCombo.currentIndexChanged.connect(self.loadPeriodContent)
        self.uiPeriodCombo.currentIndexChanged.connect(self.loadPeriodDetailsContent)
        #self.uiPeriodDetailsCombo.currentIndexChanged.connect(False)

        self.setupSearchComboBox(self.uiTimeCombo, "zeit", "zeit", "zeit")

        # Kultur

        self.setupSearchComboBox(self.uiCultureCombo, "kultur", "name", "name")

        # Fundart
        self.setupSearchComboBox(self.uiFindTypeCombo, "fundart", "fundart", "fundart")
        self.uiFindTypeCombo.currentIndexChanged.connect(self.loadFindTypeDtailsContent)

        self.uiFindTypeDetailsChk.setCheckState(Qt.Unchecked)
        self.uiFindTypeDetailsCombo.setEnabled(False)
        self.uiFindTypeDetailsChk.stateChanged.connect(self.onFindTypeDetailsChkChanged)



    def loadPeriodContent(self, idx):
        time = self.uiTimeCombo.currentText()
        self.setupSearchComboBoxByQuery(self.uiPeriodCombo, u"SELECT DISTINCT periode FROM zeit WHERE zeit ='{0}'".format(time))

    def loadPeriodDetailsContent(self, idx):
        time = self.uiTimeCombo.currentText()
        period = self.uiPeriodCombo.currentText()
        self.setupSearchComboBoxByQuery(self.uiPeriodDetailsCombo, u"SELECT DISTINCT periode_detail FROM zeit WHERE zeit = '{0}' AND periode = '{1}'".format(time, period))

    def loadFindTypeDtailsContent(self, idx):
        findType = self.uiFindTypeCombo.currentText()
        self.setupSearchComboBoxByQuery(self.uiFindTypeDetailsCombo, u"SELECT DISTINCT fundart_detail FROM fundart WHERE fundart ='{0}'".format(findType))

    def onPeriodChkChanged(self, state):
        if state:
            self.uiPeriodCombo.setEnabled(True)
            self.uiPeriodDetailsChk.setEnabled(True)
        else:
            self.uiPeriodCombo.setEnabled(False)
            self.uiPeriodDetailsChk.setCheckState(Qt.Unchecked)
            self.uiPeriodDetailsChk.setEnabled(False)

    def onPeriodDetailsChkChanged(self, state):
        if state:
            self.uiPeriodDetailsCombo.setEnabled(True)
        else:
            self.uiPeriodDetailsCombo.setEnabled(False)

    def onFindTypeDetailsChkChanged(self, state):
        if state:
            self.uiFindTypeDetailsCombo.setEnabled(True)
        else:
            self.uiFindTypeDetailsCombo.setEnabled(False)

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
        if self.uiSearchByMapLayerCombo.count() < 1:
            return
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
                query.prepare("SELECT fundortnummer, flurname, katastralgemeinde, fundgewinnung, sicherheit FROM fundort WHERE fundortnummer IN (SELECT DISTINCT fo.fundortnummer FROM fundort fo WHERE NOT IsEmpty(fo.geometry) AND NOT IsEmpty(GeomFromText('{0}',{1})) AND Intersects(GeomFromText('{0}',{1}), fo.geometry) AND fo.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'fundort' AND search_frame = GeomFromText('{0}',{1}) ) ) ORDER BY katastralgemeindenummer, land, fundortnummer_nn".format(searchGeometry.exportToWkt(), epsg))
                #
                #qryStr = "select cp.bildnummer as bildnummer, cp.filmnummer as filmnummer, cp.radius as mst_radius, f.weise as weise, f.art_ausarbeitung as art from film as f, luftbild_schraeg_cp AS cp WHERE f.filmnummer = cp.filmnummer AND cp.bildnummer IN (SELECT fp.bildnummer FROM luftbild_schraeg_fp AS fp WHERE NOT IsEmpty(fp.geometry) AND Intersects(GeomFromText('{0}',{1}), fp.geometry) AND rowid IN (SELECT rowid FROM SpatialIndex WHERE f_table_name = 'luftbild_schraeg_fp' AND search_frame = GeomFromText('{0}',{1}) )) UNION ALL SELECT  cp_s.bildnummer AS bildnummer, cp_S.filmnummer AS filmnummer, cp_s.massstab, f_s.weise, f_s.art_ausarbeitung FROM film AS f_s, luftbild_senk_cp AS cp_s WHERE f_s.filmnummer = cp_s.filmnummer AND cp_s.bildnummer IN (SELECT fp_s.bildnummer FROM luftbild_senk_fp AS fp_s WHERE NOT IsEmpty(fp_s.geometry) AND Intersects(GeomFromText('{0}',{1}), fp_s.geometry) AND rowid IN (SELECT rowid FROM SpatialIndex WHERE f_table_name = 'luftbild_senk_fp' AND search_frame = GeomFromText('{0}',{1}) ) ) ORDER BY filmnummer, bildnummer".format(searchGeometry.exportToWkt(), epsg)
                query.exec_()
                self.siteSelectionListDlg = ApisSiteSelectionListDialog(self.iface, self.dbm)
                info = u"gefunden, die von den selektierten Features aus dem Layer '{0}' abgedeckt/geschnitten werden.".format(vlayer.name())
                res = self.siteSelectionListDlg.loadSiteListBySpatialQuery(query, info)
                if res:
                    self.siteSelectionListDlg.show()
                    if self.siteSelectionListDlg.exec_():
                        pass

            elif self.uiSearchFindspotRBtn.isChecked():
                #Fundstellensuche
                query.prepare("SELECT fs.fundortnummer, fs.fundstellenummer, fo.katastralgemeinde, datierung, fundart, fundart_detail, fs.sicherheit, kultur FROM fundstelle fs, fundort fo WHERE fs.fundortnummer = fo.fundortnummer AND (fs.fundortnummer || '.' || fs.fundstellenummer) IN (SELECT DISTINCT (fst.fundortnummer || '.' || fst.fundstellenummer) AS fsn FROM fundstelle fst WHERE NOT IsEmpty(fst.geometry) AND NOT IsEmpty(GeomFromText('{0}',{1})) AND Intersects(GeomFromText('{0}', {1}), fst.geometry) AND fst.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'fundstelle' AND search_frame = GeomFromText('{0}', {1}))) ORDER BY fo.katastralgemeindenummer, fo.land, fo.fundortnummer_nn, fs.fundstellenummer".format(searchGeometry.exportToWkt(), epsg))
                #query.prepare("SELECT fundortnummer, fundstellenummer, datierung, fundart, fundart_detail, sicherheit, kultur FROM fundstelle WHERE (fundortnummer || '.' || fundstellenummer) as id1 IN (SELECT DISTINCT (fs.fundortnummer || '.' || fs.fundstellenummer) as id2 FROM fundstelle fs WHERE NOT IsEmpty(fs.geometry) AND NOT IsEmpty(GeomFromText('{0}',{1})) AND Intersects(GeomFromText('{0}',{1}), fs.geometry) AND fs.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'fundstelle' AND search_frame = GeomFromText('{0}',{1}) ) )".format(searchGeometry.exportToWkt(), epsg))
                query.exec_()
                self.findSpotSelectionListDlg = ApisFindSpotSelectionListDialog(self.iface, self.dbm)
                res = self.findSpotSelectionListDlg.loadFindSpotListBySpatialQuery(query)
                if res:
                    self.findSpotSelectionListDlg.show()
                    #if self.findSpotSelectionListDlg.exec_():
                    #    pass

            #QMessageBox.warning(None, "Query", "Query finished")

        else:
            self.iface.messageBar().pushMessage(u"Error", u"Bitte selektieren sie zumindest ein Feature im Layer {0} für die Suche!".format(vlayer.name()), level=QgsMessageBar.WARNING, duration=5)


    def spatialSearchByCadastralCommunity(self):
        if self.uiSpatialSearchBtn.isChecked():
            self.uiSpatialSearchBtn.toggle()

        searchValue = self.uiSearchByCadastralCommunityCombo.lineEdit().text()
        searchValues = [sV.strip().replace("'","").replace("\"", "") for sV in searchValue.split(",") if len(sV.strip().replace("'","").replace("\"", "")) > 0]
        if len(searchValues) < 1:
            return
        likeSearch = False
        if len(searchValues) == 1:
            likeSearch = True
        searchValuesStr = u"'"
        searchValuesStr += u"', '".join(searchValues)
        searchValuesStr += u"'"
        #if searchValuesStr
        #QMessageBox.warning(None, self.tr(u"Katastralgemeinde"), u"{0}".format(searchValuesStr))

        epsg = 4312
        query = QSqlQuery(self.dbm.db)

        if likeSearch:
            ccSearchStr = u"SELECT Transform(kg.geometry, {1}) as geometry FROM katastralgemeinden kg WHERE kg.katastralgemeindenummer LIKE '{0}' OR kg.katastralgemeindename LIKE '{0}' AND NOT IsEmpty(kg.geometry)".format(searchValuesStr.replace("'", "%"), epsg)
        else:
            ccSearchStr = u"SELECT Transform(kg.geometry, {1}) as geometry FROM katastralgemeinden kg WHERE kg.katastralgemeindenummer IN ({0}) OR kg.katastralgemeindename IN ({0}) AND NOT IsEmpty(kg.geometry)".format(searchValuesStr, epsg)

        #QMessageBox.warning(None, self.tr(u"Katastralgemeinde"), u"{0}".format(ccSearchStr))

        if self.uiSearchImageRBtn.isChecked():
            # LuftbildSuche
            query.prepare(u"SELECT cp.bildnummer AS bildnummer, cp.filmnummer AS filmnummer, cp.radius AS mst_radius, f.weise AS weise, f.art_ausarbeitung AS art FROM film f, luftbild_schraeg_cp cp WHERE f.filmnummer = cp.filmnummer AND cp.bildnummer IN (SELECT fp.bildnummer FROM luftbild_schraeg_fp fp, ({0}) cc WHERE NOT IsEmpty(fp.geometry) AND Intersects(cc.geometry, fp.geometry) AND fp.rowid IN (SELECT rowid FROM SpatialIndex WHERE f_table_name = 'luftbild_schraeg_fp' AND search_frame = cc.geometry )) UNION ALL SELECT  cp_s.bildnummer AS bildnummer, cp_S.filmnummer AS filmnummer, cp_s.massstab, f_s.weise, f_s.art_ausarbeitung FROM film f_s, luftbild_senk_cp cp_s WHERE f_s.filmnummer = cp_s.filmnummer AND cp_s.bildnummer IN (SELECT fp_s.bildnummer FROM luftbild_senk_fp fp_s, ({0}) cc WHERE NOT IsEmpty(fp_s.geometry) AND Intersects(cc.geometry, fp_s.geometry) AND fp_s.rowid IN (SELECT rowid FROM SpatialIndex WHERE f_table_name = 'luftbild_senk_fp' AND search_frame = cc.geometry ) ) ORDER BY filmnummer, bildnummer".format(ccSearchStr))
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
            # qryStr = "SELECT fundortnummer, flurname, katastralgemeinde, fundgewinnung, sicherheit FROM fundort_pnt WHERE fundort_pnt.fundortnummer IN (SELECT DISTINCT fundort_pol.fundortnummer FROM fundort_pol WHERE NOT IsEmpty(fundort_pol.geometry) AND NOT IsEmpty(GeomFromText('{0}',{1})) AND Intersects(GeomFromText('{0}',{1}), fundort_pol.geometry) AND fundort_pol.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'fundort_pol' AND search_frame = GeomFromText('{0}',{1}) ) ) ORDER BY SUBSTR(fundortnummer, 0, 3), CAST(SUBSTR(fundortnummer, 5) AS INTEGER)".format(searchGeometry.exportToWkt(), epsg)
            query.prepare(u"SELECT fundortnummer, flurname, katastralgemeinde, fundgewinnung, sicherheit FROM fundort WHERE fundortnummer IN (SELECT DISTINCT fo.fundortnummer FROM fundort fo, ({0}) cc WHERE NOT IsEmpty(fo.geometry) AND Intersects(cc.geometry, fo.geometry) AND fo.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'fundort' AND search_frame = cc.geometry ) ) ORDER BY katastralgemeindenummer, land, fundortnummer_nn".format(ccSearchStr))
            query.exec_()
            self.siteSelectionListDlg = ApisSiteSelectionListDialog(self.iface, self.dbm)
            #info = u"gefunden, die von den selektierten Features aus dem Layer '{0}' abgedeckt/geschnitten werden.".format(vlayer.name())
            res = self.siteSelectionListDlg.loadSiteListBySpatialQuery(query)
            if res:
                self.siteSelectionListDlg.show()
                if self.siteSelectionListDlg.exec_():
                    pass

        elif self.uiSearchFindspotRBtn.isChecked():
            #Fundstellen
            query.prepare(u"SELECT fs.fundortnummer, fs.fundstellenummer, fo.katastralgemeinde, datierung, fundart, fundart_detail, fs.sicherheit, kultur FROM fundstelle fs, fundort fo WHERE fs.fundortnummer = fo.fundortnummer AND (fs.fundortnummer || '.' || fs.fundstellenummer) IN (SELECT DISTINCT (fst.fundortnummer || '.' || fst.fundstellenummer) AS fsn FROM fundstelle fst, ({0}) cc WHERE NOT IsEmpty(fst.geometry) AND Intersects(cc.geometry, fst.geometry) AND fst.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'fundstelle' AND search_frame = cc.geometry)) ORDER BY fo.katastralgemeindenummer, fo.land, fo.fundortnummer_nn, fs.fundstellenummer".format(ccSearchStr))
            query.exec_()
            self.findSpotSelectionListDlg = ApisFindSpotSelectionListDialog(self.iface, self.dbm)
            res = self.findSpotSelectionListDlg.loadFindSpotListBySpatialQuery(query)
            if res:
                self.findSpotSelectionListDlg.show()
                #if self.findSpotSelectionListDlg.exec_():
                #    pass


    def attributeSearchSiteBySiteNumber(self):
        # Fundortsuche
        siteNumberSearchValue = self.uiSearchSiteNumberCombo.lineEdit().text()
        query = QSqlQuery(self.dbm.db)
        query.prepare("SELECT fundortnummer, flurname, katastralgemeinde, fundgewinnung, sicherheit FROM fundort WHERE fundortnummer LIKE '%{0}%' ORDER BY katastralgemeindenummer, land, fundortnummer_nn".format(siteNumberSearchValue))
        # qryStr = "select cp.bildnummer as bildnummer, cp.filmnummer as filmnummer, cp.radius as mst_radius, f.weise as weise, f.art_ausarbeitung as art from film as f, luftbild_schraeg_cp AS cp WHERE f.filmnummer = cp.filmnummer AND cp.bildnummer IN (SELECT fp.bildnummer FROM luftbild_schraeg_fp AS fp WHERE NOT IsEmpty(fp.geometry) AND Intersects(GeomFromText('{0}',{1}), fp.geometry) AND rowid IN (SELECT rowid FROM SpatialIndex WHERE f_table_name = 'luftbild_schraeg_fp' AND search_frame = GeomFromText('{0}',{1}) )) UNION ALL SELECT  cp_s.bildnummer AS bildnummer, cp_S.filmnummer AS filmnummer, cp_s.massstab, f_s.weise, f_s.art_ausarbeitung FROM film AS f_s, luftbild_senk_cp AS cp_s WHERE f_s.filmnummer = cp_s.filmnummer AND cp_s.bildnummer IN (SELECT fp_s.bildnummer FROM luftbild_senk_fp AS fp_s WHERE NOT IsEmpty(fp_s.geometry) AND Intersects(GeomFromText('{0}',{1}), fp_s.geometry) AND rowid IN (SELECT rowid FROM SpatialIndex WHERE f_table_name = 'luftbild_senk_fp' AND search_frame = GeomFromText('{0}',{1}) ) ) ORDER BY filmnummer, bildnummer".format(searchGeometry.exportToWkt(), epsg)
        query.exec_()
        self.siteSelectionListDlg = ApisSiteSelectionListDialog(self.iface, self.dbm)
        info = u"gefunden, deren Fundortnummer die Suche '{0}' enthält.".format(siteNumberSearchValue)
        res = self.siteSelectionListDlg.loadSiteListBySpatialQuery(query, info)
        if res:
            self.siteSelectionListDlg.show()
            if self.siteSelectionListDlg.exec_():
                pass

    def attributeSearchSiteByFilmNumber(self):
        #Fundortsuche
        filmNumber = self.uiSearchFilmNumberCombo.lineEdit().text()
        filmType = self.isFilm(filmNumber)

        if filmType == u"senk.":
            fromTable = "luftbild_senk_fp"
        elif filmType == u"schräg":
            fromTable = "luftbild_schraeg_fp"
        else:
            QMessageBox.warning(None, self.tr(u"Film Nummer"), u"Es gibt keinen Film mit der Filmnummer {0}.".format(filmNumber))
            return

        query = QSqlQuery(self.dbm.db)
        query.prepare("SELECT fundortnummer, flurname, katastralgemeinde, fundgewinnung, sicherheit FROM fundort WHERE fundortnummer IN (SELECT DISTINCT fo.fundortnummer FROM fundort fo, {0} WHERE fo.geometry IS NOT NULL AND {0}.geometry IS NOT NULL AND {0}.filmnummer = '{1}' AND Intersects({0}.geometry, fo.geometry) AND fo.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'fundort' AND search_frame = {0}.geometry)) ORDER BY katastralgemeindenummer, land, fundortnummer_nn".format(fromTable, filmNumber))
        query.exec_()
        self.siteSelectionListDlg = ApisSiteSelectionListDialog(self.iface, self.dbm)
        info = u"gefunden, die vom Film {0} abgedeckt/geschnitten werden.".format(filmNumber)
        res = self.siteSelectionListDlg.loadSiteListBySpatialQuery(query, info)
        if res:
            self.siteSelectionListDlg.show()
            if self.siteSelectionListDlg.exec_():
                pass

    def attributeSearchSiteByFilmsOfYear(self):
        year = self.uiSearchYearDate.date().toString('yyyy')

        query = QSqlQuery(self.dbm.db)
        query.prepare("SELECT fundortnummer, flurname, katastralgemeinde, fundgewinnung, sicherheit FROM fundort WHERE fundortnummer IN (SELECT DISTINCT fo.fundortnummer FROM fundort fo, (SELECT filmnummer, geometry FROM luftbild_schraeg_fp WHERE NOT IsEmpty(luftbild_schraeg_fp.geometry) AND substr(luftbild_schraeg_fp.filmnummer, 3, 4) = '{0}' UNION ALL SELECT filmnummer, geometry FROM luftbild_senk_fp WHERE NOT IsEmpty(luftbild_senk_fp.geometry) AND substr(luftbild_senk_fp.filmnummer, 3, 4) = '{0}') luftbild WHERE NOT IsEmpty(fo.geometry) AND Intersects(luftbild.geometry, fo.geometry) AND fo.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'fundort' AND search_frame = luftbild.geometry)) ORDER BY katastralgemeindenummer, land, fundortnummer_nn".format(year))

        query.exec_()
        self.siteSelectionListDlg = ApisSiteSelectionListDialog(self.iface, self.dbm)
        info = u"gefunden, die von Filmen aus dem Jahr {0} abgedeckt/geschnitten werden.".format(year)
        res = self.siteSelectionListDlg.loadSiteListBySpatialQuery(query, info)
        if res:
            self.siteSelectionListDlg.show()
            if self.siteSelectionListDlg.exec_():
                pass

    def attributeSearchSiteByProjectName(self):
        # Fundortsuche
        projectNameSearchValue = self.uiSearchProjectNameCombo.lineEdit().text()
        query = QSqlQuery(self.dbm.db)
        query.prepare("SELECT fundortnummer, flurname, katastralgemeinde, fundgewinnung, sicherheit FROM fundort WHERE filmnummer_projekt LIKE '%{0}%' ORDER BY katastralgemeindenummer, land, fundortnummer_nn".format(projectNameSearchValue))
        query.exec_()
        self.siteSelectionListDlg = ApisSiteSelectionListDialog(self.iface, self.dbm)
        info = u"gefunden, deren Projektbezeichnung die Suche '{0}' enthält.".format(projectNameSearchValue)
        res = self.siteSelectionListDlg.loadSiteListBySpatialQuery(query, info)
        if res:
            self.siteSelectionListDlg.show()
            if self.siteSelectionListDlg.exec_():
                pass

    def attributeSearchFindSpot(self):
        query = QSqlQuery(self.dbm.db)
        #query.prepare("SELECT fs.fundortnummer, fs.fundstellenummer, fo.katastralgemeinde, datierung, fundart, fundart_detail, fs.sicherheit, kultur FROM fundstelle fs, fundort fo WHERE fs.fundortnummer = fo.fundortnummer AND (fs.fundortnummer || '.' || fs.fundstellenummer) IN (SELECT DISTINCT (fst.fundortnummer || '.' || fst.fundstellenummer) AS fsn FROM fundstelle fst WHERE NOT IsEmpty(fst.geometry) AND NOT IsEmpty(GeomFromText('{0}',{1})) AND Intersects(GeomFromText('{0}', {1}), fst.geometry) AND fst.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'fundstelle' AND search_frame = GeomFromText('{0}', {1}))) ORDER BY fo.katastralgemeindenummer, fo.land, fo.fundortnummer_nn, fs.fundstellenummer".format(searchGeometry.exportToWkt(), epsg))
        # query.prepare("SELECT fundortnummer, fundstellenummer, datierung, fundart, fundart_detail, sicherheit, kultur FROM fundstelle WHERE (fundortnummer || '.' || fundstellenummer) as id1 IN (SELECT DISTINCT (fs.fundortnummer || '.' || fs.fundstellenummer) as id2 FROM fundstelle fs WHERE NOT IsEmpty(fs.geometry) AND NOT IsEmpty(GeomFromText('{0}',{1})) AND Intersects(GeomFromText('{0}',{1}), fs.geometry) AND fs.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'fundstelle' AND search_frame = GeomFromText('{0}',{1}) ) )".format(searchGeometry.exportToWkt(), epsg))


        whereClause = []
        if self.uiDatingGrp.isChecked():
            whereClause.append(u"substr(datierung, 1, pos1-1) = '{0}'".format(self.uiTimeCombo.currentText()))  # zeit
            if self.uiPeriodChk.isChecked():
                whereClause.append(u"substr(datierung, pos1+1, pos2-1) = '{0}'".format(self.uiPeriodCombo.currentText()))  # periode
                if self.uiPeriodDetailsChk.isChecked():
                    whereClause.append(u"substr(datierung, pos1+pos2+1, pos3-1) = '{0}'".format(self.uiPeriodDetailsCombo.currentText()))  # periode_detail
        if self.uiCultureGrp.isChecked():
            whereClause.append(u"kultur = '{0}'".format(self.uiCultureCombo.currentText()))  # kultur
        if self.uiFindTypeGrp.isChecked():
            whereClause.append(u"fundart = '{0}'".format(self.uiFindTypeCombo.currentText()))  # fundart
            if self.uiFindTypeDetailsChk.isChecked():
                whereClause.append(u"instr(fundart_detail, '{0}')".format(self.uiFindTypeDetailsCombo.currentText()))  # fundart_detail; je fundart_detail
        #whereClause.append("")  # spatial

        whereStr = u" AND ".join(whereClause)

        qryStr = u"SELECT fundortnummer, fundstellenummer, datierung, fundart, fundart_detail, sicherheit, kultur FROM (SELECT *, instr(datierung,',') AS pos1, instr(substr(datierung, instr(datierung,',')+1), ',') AS pos2, instr(substr(datierung, instr(datierung,',')+instr(substr(datierung, instr(datierung,',')+1), ',')+1),  ',') AS pos3 FROM fundstelle) WHERE {0}".format(whereStr)

        QMessageBox.warning(None, self.tr(u"findspot search"), u"{0}".format(qryStr))


        #return
        query.prepare(qryStr)
        query.exec_()
        self.findSpotSelectionListDlg = ApisFindSpotSelectionListDialog(self.iface, self.dbm)
        res = self.findSpotSelectionListDlg.loadFindSpotListBySpatialQuery(query)
        if res:
            self.findSpotSelectionListDlg.show()
            # if self.findSpotSelectionListDlg.exec_():
            #    pass


    def isFilm(self, filmNumber):
        # check if filmNumber is a filmNumber in film Table
        query = QSqlQuery(self.dbm.db)
        query.prepare("SELECT weise FROM film WHERE filmnummer = '{0}'".format(filmNumber))
        query.exec_()
        query.first()
        return query.value(0)

    def setupSearchComboBox(self, editor, table, column, order, modelcolumn=0):
        model = QSqlQueryModel(self)
        model.setQuery("SELECT DISTINCT {0} FROM {1} ORDER BY {2}".format(column, table, order), self.dbm.db)

        tv = QTableView()
        editor.setView(tv)

        tv.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        tv.setSelectionMode(QAbstractItemView.SingleSelection)
        tv.setSelectionBehavior(QAbstractItemView.SelectRows)
        tv.setAutoScroll(False)

        editor.setModel(model)

        editor.setModelColumn(modelcolumn)
        editor.setInsertPolicy(QComboBox.NoInsert)

        tv.resizeColumnsToContents()
        tv.resizeRowsToContents()
        tv.verticalHeader().setVisible(False)
        tv.horizontalHeader().setVisible(True)
        # tv.setMinimumWidth(tv.horizontalHeader().length())
        tv.horizontalHeader().setResizeMode(QHeaderView.Stretch)

        editor.setAutoCompletion(True)
        editor.setCurrentIndex(-1)

    def setupSearchComboBoxByQuery(self, editor, query, modelcolumn=0):
        model = QSqlQueryModel(self)
        model.setQuery(query, self.dbm.db)

        tv = QTableView()
        editor.setView(tv)

        tv.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        #tv.setSelectionMode(QAbstractItemView.MultiSelection)
        tv.setSelectionMode(QAbstractItemView.SingleSelection)
        tv.setSelectionBehavior(QAbstractItemView.SelectRows)
        tv.setAutoScroll(False)

        editor.setModel(model)

        editor.setModelColumn(modelcolumn)
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


    def joinRowValues(self, row):
        editor = self.sender()
        #QMessageBox.warning(None, self.tr(u"Katastralgemeinde"), u"{0}".format(editor))
        record = editor.model().record(row)
        values = []
        for i in range(record.count()):
            values.append(record.value(i))
        editor.lineEdit().setText(", ".join(values))
