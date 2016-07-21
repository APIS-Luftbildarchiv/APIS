# -*- coding: utf-8 -*

"""
/***************************************************************************
 *   APIS                                                                  *
 *   A QGIS plugin for APIS - Luftbildarchiv Uni Wien                      *
 *                                                                         *
 *   begin     : 2016-06-01                                                *
 *   copyright : (C) 2016 by Johannes Liem und Luftbildarchiv Uni Wien     *
 *   email     : johannes.liem@digitalcartography.org                      *
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

/***************************************************************************
 *   apis_site_mapping_dialog.py                                           *
 *   Fundorte Kartieren Dock Widget                                        *
 *                                                                         *
 *                                                                         *
 *                                                                         *
 *                                                                         *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from qgis.core import *
from qgis.gui import *
from apis_db_manager import *
from apis_map_tools import *
import sys, os, math, string
import os.path
from apis_site_edit_findspot_handling_dialog import *
from apis_utils import *

from apis_site_dialog import *

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")
from apis_site_mapping_form import *

class ApisSiteMappingDialog(QDockWidget, Ui_apisSiteMappingDialog):
    def __init__(self, iface, dbm, imageRegistry, apisLayer):
        QDockWidget.__init__(self)
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.setupUi(self)
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)
        self.dbm = dbm
        self.imageRegistry = imageRegistry
        self.apisLayer = apisLayer
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self)
        self.hide()

        self.point = None
        self.polygon = None
        self.crs = None


        self.siteLayerId = None
        self.siteLayer = None

        self.findSpotLayerId = None
        self.findSpotLayer = None

        #self.changedGeometries = {}
        #self.changedAttributeValues = {}
        self.lastGeometryChange = None
        self.lastFindSpotGeometryChange = None

        self.uiSiteMappingModesGrp.setEnabled(False)

        self.uiAddToSiteManuallyGrp.setVisible(False)
        self.uiAddToSiteByIntersectionGrp.setVisible(False)
        self.uiEditGeometryGrp.setVisible(False)
        self.uiEditFindSpotGeometryGrp.setVisible(False)

        self.visibilityChanged.connect(self.onVisibilityChanged)

        self.uiNewSiteYesRBtn.toggled.connect(self.onNewSiteChanged)
        self.uiNewSiteNoRBtn.toggled.connect(self.onNewSiteChanged)
        self.uiEditGeometryRBtn.toggled.connect(self.onNewSiteChanged)

        self.siteMapToolByPoint = ApisMapToolEmitPointAndSquare(self.canvas)
        self.siteMapToolByPoint.setButton(self.uiMapPointAndSquareBtn)
        self.uiMapPointAndSquareBtn.setCheckable(True)
        self.uiMapPointAndSquareBtn.toggled.connect(self.onToggleMapping)
        self.siteMapToolByPoint.mappingFinished.connect(self.onMappingFinished)
        self.uiDiagonalSpn.valueChanged.connect(self.onDiagonalValueChanged)

        self.siteMapToolByPolygon = ApisMapToolEmitPolygonAndPoint(self.canvas)
        self.siteMapToolByPolygon.setButton(self.uiMapPolygonAndPointBtn)
        self.uiMapPolygonAndPointBtn.setCheckable(True)
        self.uiMapPolygonAndPointBtn.toggled.connect(self.onTogglePolygonMapping)
        self.siteMapToolByPolygon.mappingFinished.connect(self.onMappingFinished)

        self.uiCheckIfFilmBtn.clicked.connect(self.onCheckIfFilm)

        self.uiFilmOrProjectEdit.textChanged.connect(self.onFilmOrProjectChanged)

        self.uiIntersectingSitesCombo.activated.connect(self.selectEditCandidateSite)

        self.uiCancelSelectedEditingBtn.clicked.connect(self.onCancelAnyEdits)
        self.uiProvideSiteManuallyBtn.clicked.connect(self.provideSiteManually)
        self.uiAddToSelectedSiteBtn.clicked.connect(self.addToSelectedSite)
        self.uiReplaceSelectedSiteBtn.clicked.connect(self.replaceSelectedSite)

        self.uiCancelManuallyEditingBtn.clicked.connect(self.onCancelAnyEdits)
        self.uiReplaceProvidedSiteBtn.clicked.connect(self.replaceProvidedSite)

        self.uiEditGeometryStartBtn.clicked.connect(self.startEditingSiteLayer)
        self.uiEditGeometryCancelBtn.clicked.connect(self.cancelEditingSiteLayer)

        self.uiEditFindSpotGeometryStartBtn.clicked.connect(self.startEditingFindSpotLayer)
        self.uiEditFindSpotGeometryCancelBtn.clicked.connect(self.cancelEditingFindSpotLayer)

# ---------------------------------------------------------------------------
# Slots
# ---------------------------------------------------------------------------

    def onCancelAnyEdits(self):
        # CleanUp Map Canvas
        self.cleanUpMapCanvas()
        # Reset UI
        self.onNewSiteChanged()


    def onDiagonalValueChanged(self, value):
        self.siteMapToolByPoint.updateDiagonal(value)


    def onMappingFinished(self, point, polygon, crs):
        self.point = point
        self.polygon = polygon
        self.crs = crs

        #QMessageBox.warning(None, self.tr(u"Site Mapping"), u"Site Geom: {0}, {1}".format(point, polygon))
        if self.uiNewSiteYesRBtn.isChecked():
            self.addNewSite()
        else:
            self.checkEditSite()

    def onNewSiteChanged(self):
        self.uiMapPointAndSquareBtn.setChecked(False)
        self.uiMapPolygonAndPointBtn.setChecked(False)

        self.uiAddToSiteManuallyGrp.setVisible(False)
        self.uiAddToSiteByIntersectionGrp.setVisible(False)

        if self.siteLayerId not in QgsMapLayerRegistry.instance().mapLayers():
            self.siteLayer = None
            self.siteLayerId = None
            self.reloadSiteLayer()

        if self.siteLayer and self.siteLayer.isEditable() and not self.uiEditGeometryRBtn.isChecked():
            self.siteLayer.rollBack()
            self.uiEditGeometryStartBtn.setEnabled(True)
            self.uiEditGeometryCancelBtn.setEnabled(False)

        if self.findSpotLayerId not in QgsMapLayerRegistry.instance().mapLayers():
            self.findSpotLayer = None
            self.findSpotLayerId = None

        if self.findSpotLayer and self.findSpotLayer.isEditable() and not self.uiEditGeometryRBtn.isChecked():
            self.findSpotLayer.rollBack()
            self.uiEditFindSpotGeometryStartBtn.setEnabled(True)
            self.uiEditFindSpotGeometryCancelBtn.setEnabled(False)


        if self.uiNewSiteYesRBtn.isChecked():
            # Add New Site
            self.uiNewSiteInterpretationGrp.setEnabled(True)
            self.uiSiteMappingModesGrp.setVisible(True)
            self.uiSiteMappingModesGrp.setEnabled(False)
            self.uiNewSiteInterpretationGrp.setEnabled(True)
            self.uiNewSiteInterpretationGrp.setVisible(True)
            self.uiEditGeometryGrp.setVisible(False)
            self.uiEditFindSpotGeometryGrp.setVisible(False)

        elif self.uiNewSiteNoRBtn.isChecked():
            # Add To Existing Site
            self.uiNewSiteInterpretationGrp.setEnabled(False)
            self.uiSiteMappingModesGrp.setVisible(True)
            self.uiSiteMappingModesGrp.setEnabled(True)
            self.uiNewSiteInterpretationGrp.setVisible(False)
            self.uiEditGeometryGrp.setVisible(False)
            self.uiEditFindSpotGeometryGrp.setVisible(False)


        elif self.uiEditGeometryRBtn.isChecked():
            # siteStart Layer in Edit Mode!
            self.uiSiteMappingModesGrp.setVisible(False)
            self.uiNewSiteInterpretationGrp.setVisible(False)
            self.uiEditGeometryGrp.setVisible(True)
            self.uiEditFindSpotGeometryGrp.setVisible(True)


            #self.startEditingSiteLayer()
        else:
            return

    # def onPolygonMappingFinished(self, point, polygon, crs):
    #     #QMessageBox.warning(None, self.tr(u"Site Mapping"), u"Site Geom: {0}, {1}".format(point, polygon))
    #     if self.uiNewSiteYesRBtn.isChecked():
    #         self.addNewSite(point, polygon, crs)
    #     else:
    #         self.checkEditSite(point, polygon, crs)

    def onToggleMapping(self, isChecked):
        if isChecked:
            self.uiNewSiteInterpretationGrp.setEnabled(False)
            self.siteMapToolByPoint.updateDiagonal(self.uiDiagonalSpn.value())
            self.canvas.setMapTool(self.siteMapToolByPoint)
            #self.iface.messageBar().pushMessage(u"APIS Bild Kartierung", u"Positionieren Sie den Bildmittelpunkt mit der linken Maustaste und klicken Sie auf das Plus Symbol (oder verwenden Sie die reche Maustaste)", level=QgsMessageBar.INFO)
        else:
            self.siteMapToolByPoint.stopCapturing()
            self.canvas.unsetMapTool(self.siteMapToolByPoint)
            #self.iface.actionTouch().trigger()
            if not self.uiMapPolygonAndPointBtn.isChecked() and not self.uiMapPointAndSquareBtn.isChecked():
                self.iface.actionTouch().trigger()
                self.uiNewSiteInterpretationGrp.setEnabled(True)

            #self.iface.messageBar().clearWidgets()


    def onTogglePolygonMapping(self, isChecked):
        if isChecked:
            self.uiNewSiteInterpretationGrp.setEnabled(False)
            self.canvas.setMapTool(self.siteMapToolByPolygon)
            # self.iface.messageBar().pushMessage(u"APIS Bild Kartierung", u"Positionieren Sie den Bildmittelpunkt mit der linken Maustaste und klicken Sie auf das Plus Symbol (oder verwenden Sie die reche Maustaste)", level=QgsMessageBar.INFO)
        else:
            self.siteMapToolByPolygon.stopCapturing()
            self.canvas.unsetMapTool(self.siteMapToolByPolygon)
            if not self.uiMapPolygonAndPointBtn.isChecked() and not self.uiMapPointAndSquareBtn.isChecked():
                self.iface.actionTouch().trigger()
                self.uiNewSiteInterpretationGrp.setEnabled(True)

    def onVisibilityChanged(self, isVisible):
        #QMessageBox.warning(None, self.tr(u"SearchDialog Visibility"), u"Visibility Search Dialog: {0}".format(visibility))
        if not isVisible:
            # datctivate mapping tools
            self.uiMapPointAndSquareBtn.setChecked(False)
            self.uiMapPolygonAndPointBtn.setChecked(False)

            #unload layers
            #self.removeSiteLayer()
        else:
            #load layers
            #self.removeSiteLayer()
            #self.loadSiteLayer()
            self.reloadSiteLayer()


    def cleanUpMapCanvas(self):
        # deselect
        self.siteLayer.removeSelection()
        # remove map tool rRubberBands/VertexMarker
        self.siteMapToolByPoint.clearScene()
        self.siteMapToolByPolygon.clearScene()


    def startEditingSiteLayer(self):
        self.reloadSiteLayer()
        self.siteLayer.startEditing()
        self.uiEditGeometryStartBtn.setEnabled(False)
        self.uiEditGeometryCancelBtn.setEnabled(True)

    def cancelEditingSiteLayer(self):
        if self.siteLayer and self.siteLayer.isEditable():
            self.siteLayer.rollBack()
        self.uiEditGeometryStartBtn.setEnabled(True)
        self.uiEditGeometryCancelBtn.setEnabled(False)

    def startEditingFindSpotLayer(self):
        self.reloadFindSpotLayer()
        self.findSpotLayer.startEditing()
        self.uiEditFindSpotGeometryStartBtn.setEnabled(False)
        self.uiEditFindSpotGeometryCancelBtn.setEnabled(True)

    def cancelEditingFindSpotLayer(self):
        if self.findSpotLayer and self.findSpotLayer.isEditable():
            self.findSpotLayer.rollBack()
        self.uiEditFindSpotGeometryStartBtn.setEnabled(True)
        self.uiEditFindSpotGeometryCancelBtn.setEnabled(False)

    def removeSiteLayer(self):
        if self.siteLayerId in QgsMapLayerRegistry.instance().mapLayers():
            #TODO: disconnect all slots
            QgsMapLayerRegistry.instance().removeMapLayer(self.siteLayer.id())

    def reloadSiteLayer(self):
        if self.siteLayerId not in QgsMapLayerRegistry.instance().mapLayers():
            self.loadSiteLayer()

    def reloadFindSpotLayer(self):
        if self.findSpotLayerId not in QgsMapLayerRegistry.instance().mapLayers():
            self.loadFindSpotLayer()

    def loadSiteLayer(self):
        #uri = QgsDataSourceURI()
        #uri.setDatabase(self.dbm.db.databaseName())
        #uri.setDataSource('', 'fundort', 'geometry')
        #self.siteLayer = QgsVectorLayer(uri.uri(), u'Fundorte', 'spatialite')
        self.siteLayer = self.apisLayer.requestSiteLayer()
        if self.siteLayer:
            self.siteLayerId = self.siteLayer.id()
            self.siteLayer.geometryChanged.connect(self.onSiteGeometryEditing)
            self.siteLayer.editCommandEnded.connect(self.onEditCommandEnded)
            self.siteLayer.beforeCommitChanges.connect(self.onBeforeCommitChanges)
        #self.siteLayer.committedGeometriesChanges.connect(self.onSiteGeometryChangesCommitted)
        #self.siteLayer.committedAttributeValuesChanges.connect(self.onSiteAttributeValuesChangesCommitted)

        # self.siteLayer.editingStopped.connect(self.editingStopped)
        # self.siteLayer.editCommandStarted.connect(self.onEditCommandStarted)

        #symbol_layer = QgsSimpleLineSymbolLayerV2()
        #symbol_layer.setWidth(0.6)
        #symbol_layer.setColor(QColor(100, 50, 140, 255))
        #self.siteLayer.rendererV2().symbols()[0].changeSymbolLayer(0, symbol_layer)

        #QgsMapLayerRegistry.instance().addMapLayer(self.siteLayer)


    def loadFindSpotLayer(self):
        self.findSpotLayer = self.apisLayer.requestFindSpotLayer()
        if self.findSpotLayer:
            self.findSpotLayerId = self.findSpotLayer.id()
            self.findSpotLayer.geometryChanged.connect(self.onFindSpotGeometryEditing)
            self.findSpotLayer.editCommandEnded.connect(self.onFindSpotEditCommandEnded)
            self.findSpotLayer.beforeCommitChanges.connect(self.onBeforeCommitChangesFindSpotEditing)

    def onSiteAttributeValuesChangesCommitted(self, layerId, changedAttributesValues ):
        QMessageBox.warning(None, self.tr(u"Site Mapping"), u"AttributeChanges Comitted")
        # Log Because of Attribute Changes
        #TODO: LOGGING

    def onSiteGeometryChangesCommitted(self, layerId, changedGeometries):
        QMessageBox.warning(None, self.tr(u"Site Mapping"), u"GeometryChanges Comitted")
        # Log Because of Geometry Changes



        #layer = QgsMapLayerRegistry.instance().mapLayer(layerId)

        #
        # fids = [fid for fid, geom in changedGeometries.items()]
        #
        # request = QgsFeatureRequest()
        # request.setSubsetOfAttributes(['fundortnummer'], layer.pendingFields())
        # request.setFilterFids(fids)
        #
        # features = layer.getFeatures(request)
        #
        # if not layer.isEditable():
        #     layer.startEditing()
        # for feature in features:
        #
        #     layer.updateFeature(feature)
        # layer.commitChanges()


        # for fid, geom in changedGeometries.items():
        #     request = QgsFeatureRequest().setFilterFids([fid])
        #     fList = [feat for feat in self.siteLayer.getFeatures(request)]
        #     if len(fList) > 1:
        #         pass
        #         #error
        #     else:
        #         f = fList[0]
        #         siteNumber = f.attribute("fundortnummer")
        #
        #         siteArea = self.siteAreaHa(geom)
        #         country = f.attribute("land")
        #
        #         if country == 'AUT':
        #             kgCode, kgName = self.getKgNameAndCode(geom)
        #         else:
        #             kgCode = None
        #             kgName = None

                #self.siteLayer.startEditing()
                #feature.setGeometry(polygon)
                # f.setAttribute('flaeche', siteArea)
                # f.setAttribute('katastralgemeindenummer', kgCode)
                # f.setAttribute('katastralgemeinde', kgName)
                #
                # cpGeom = geom.centroid()
                # nearestCp = geom.nearestPoint(cpGeom)
                # cp = nearestCp.asPoint()
                # f.setAttribute('longitude', cp.x())
                # f.setAttribute('latitude', cp.y())
                #
                # # Aktions
                # import getpass
                # now = QDate.currentDate()
                # f.setAttribute('aktion', 'edited')
                # f.setAttribute('aktionsdatum', now.toString("yyyy-MM-dd"))
                # f.setAttribute('aktionsuser', getpass.getuser())
                #
                # if country == 'AUT':
                #     # get meridian and epsg Code
                #     lon = cp.x()
                #     if lon < 11.8333333333:
                #         meridian = 28
                #         epsgGK = 31254
                #     elif lon > 14.8333333333:
                #         meridian = 34
                #         epsgGK = 31256
                #     else:
                #         meridian = 31
                #         epsgGK = 31255
                #     f.setAttribute('meridian', meridian)
                #     gk = QgsGeometry(nearestCp)
                #     destGK = QgsCoordinateReferenceSystem()
                #     destGK.createFromId(epsgGK, QgsCoordinateReferenceSystem.EpsgCrsId)
                #     ctGK = QgsCoordinateTransform(self.siteLayer.crs(), destGK)
                #     gk.transform(ctGK)
                #     f.setAttribute('gkx', gk.asPoint().y())  # Hochwert
                #     f.setAttribute('gky', gk.asPoint().x())  # Rechtswert
                #
                # self.siteLayer.updateFeature(f)
                #
                # uri = QgsDataSourceURI()
                # uri.setDatabase(self.dbm.db.databaseName())
                # uri.setDataSource('', 'fundstelle', 'geometry')
                # findSpotLayer = QgsVectorLayer(uri.uri(), u'Fundstelle', 'spatialite')
                # findSpotLayer.setSubsetString(u'"fundortnummer" = "{0}"'.format(siteNumber))
                #
                # if findSpotLayer.featureCount() > 0:
                #     # QMessageBox.warning(None, u"Fundort Update", u"{0}.".format(oldPolygon))
                #     #if self.allGeometriesEquals(findSpotLayer, oldPolygon):
                #     findSpotLayer.startEditing()
                #     fSIter = findSpotLayer.getFeatures()
                #     for fSFeature in fSIter:
                #         fSFeature.setGeometry(geom)
                #         # geom = fSFeature.geometry()
                #         findSpotLayer.updateFeature(fSFeature)
                #     findSpotLayer.commitChanges()
                #     #else:
                #     #    findSpotLayer.startEditing()
                #     #    fSIter = findSpotLayer.getFeatures()
                #     #    for fSFeature in fSIter:
                #     #        geom = fSFeature.geometry()
                #     #        fSFeature.setGeometry(geom.intersection(polygon))
                #     #       findSpotLayer.updateFeature(fSFeature)
                #     findSpotLayer.commitChanges()

                #self.siteLayer.commitChanges()
                #g = f.geometry()
                #QMessageBox.warning(None, self.tr(u"Site Mapping"), u"{0}, {1}, {2}".format(siteNumber, geom.area(), g.area()))

    def editingStopped(self):
        QMessageBox.warning(None, self.tr(u"Site Mapping"), u"Edit stopped!")
        #Do changes on FindSpots!!!

    def onBeforeCommitChanges(self):
        #for fid, geom in self.changedGeometries.items():
        #    QMessageBox.warning(None, self.tr(u"Site Mapping"), u"{0}, {1}".format(fid, geom))
        #QMessageBox.warning(None, self.tr(u"Site Mapping"), u"Before Commit Changes")

        if not self.siteLayer.isEditable():
            self.siteLayer.startEditing()

        editBuffer = self.siteLayer.editBuffer()
        changedGeometriesMap = editBuffer.changedGeometries()
        fids = [fid for fid, geom in changedGeometriesMap.items()]
        request = QgsFeatureRequest()
        request.setFilterFids(fids)
        polygonDict = {}
        features = self.siteLayer.getFeatures(request)
        for feature in features:
            fid = feature.id()
            newGeometry = changedGeometriesMap[fid]
            oldGeometry = feature.geometry()
            siteNumber = feature.attribute('fundortnummer')
            polygonDict[siteNumber] = [newGeometry, QgsGeometry(oldGeometry), newGeometry.buffer(0.0001, 12)]
            country = feature.attribute('land')
            # edit and update attributes, affected by geometry change
            feature.setAttribute('flaeche', self.siteAreaHa(newGeometry))

            cpGeom = newGeometry.centroid()
            if not newGeometry.contains(cpGeom):
                cpGeom = newGeometry.pointOnSurface()
            cp = cpGeom.asPoint()
            feature.setAttribute('longitude', cp.x())
            feature.setAttribute('latitude', cp.y())

            if country == 'AUT':
                # get meridian and epsg Code
                meridian, epsgGK = GetMeridianAndEpsgGK(cp.x())

                # get KG Coordinates
                gk = TransformGeometry(cpGeom, self.siteLayer.crs(), QgsCoordinateReferenceSystem(epsgGK, QgsCoordinateReferenceSystem.EpsgCrsId))
                gkx = gk.asPoint().y()  # Hochwert
                gky = gk.asPoint().x()  # Rechtswert

                #kgCode, kgName = self.getKgNameAndCode(newGeometry)
            else:
                #kgCode = None
                #kgName = None
                meridian = None
                gkx = None
                gky = None

            feature.setAttribute('meridian', meridian)
            feature.setAttribute('gkx', gkx)  # Hochwert
            feature.setAttribute('gky', gky)  # Rechtswert
            # Do not overwrite kg (InitalKG)
            #feature.setAttribute('katastralgemeindenummer', kgCode)
            #feature.setAttribute('katastralgemeinde', kgName)

            now = QDate.currentDate()
            feature.setAttribute('datum_aenderung', now.toString("yyyy-MM-dd"))
            # Aktions
            import getpass
            user = getpass.getuser()
            feature.setAttribute('aktion', 'editG')
            feature.setAttribute('aktionsdatum', now.toString("yyyy-MM-dd"))
            feature.setAttribute('aktionsuser', user)

            self.siteLayer.updateFeature(feature)

        if SitesHaveFindSpots(self.dbm.db, [siteNumber for siteNumber in polygonDict]):
            findSpotHandlingDlg = ApisSiteEditFindSpotHandlingDialog(self.iface, self.dbm, polygonDict)
            findSpotHandlingDlg.closeAble = False
            findSpotHandlingDlg.uiCancelEditBtn.setEnabled(False)
            res = findSpotHandlingDlg.exec_()
            fSEditActions = findSpotHandlingDlg.getActions()
            # Edit FindSpots
            sites = u", ".join(u"'{0}'".format(siteNumber) for siteNumber in polygonDict)

            # Fundstellen des Fundortes Editieren
            uri = QgsDataSourceURI()
            uri.setDatabase(self.dbm.db.databaseName())
            uri.setDataSource('', 'fundstelle', 'geometry')
            findSpotLayer = QgsVectorLayer(uri.uri(), u'Fundstelle', 'spatialite')
            findSpotLayer.setSubsetString(u'"fundortnummer" IN ({0})'.format(sites))

            if findSpotLayer.featureCount() > 0:
                logs = []
                findSpotLayer.startEditing()
                fSIter = findSpotLayer.getFeatures()
                for fSFeature in fSIter:
                    fSGeom = fSFeature.geometry()
                    sN = fSFeature.attribute("fundortnummer")
                    fSN = fSFeature.attribute("fundstellenummer")
                    fSNumber = u"{0}.{1}".format(sN, fSN)

                    if fSEditActions[fSNumber] == 1:
                        # findSpot Polygon gets same geometry, attributes as sitePolygon
                        pol = polygonDict[sN][0]
                        fSFeature.setGeometry(pol)
                        fSFeature.setAttribute('aktion', 'editG1')
                        logs.append([u"editG1", sN, fSN])
                    elif fSEditActions[fSNumber] == 2:
                        # findSpot Polygon is different from sitePolygon
                        pol = fSGeom.intersection(polygonDict[sN][0])
                        fSFeature.setGeometry(pol)
                        fSFeature.setAttribute('aktion', 'editG2')
                        logs.append([u"editG2", sN, fSN])

                    if fSEditActions[fSNumber] == 1 or fSEditActions[fSNumber] == 2:
                        fSFeature.setAttribute('flaeche', self.siteAreaHa(pol))
                        # if center point is not on polygon get the nearest Point
                        cpPol = pol.centroid()
                        if not pol.contains(cpPol):
                            cpPol = pol.pointOnSurface()
                        cpP = cpPol.asPoint()
                        fSFeature.setAttribute('longitude', cpP.x())
                        fSFeature.setAttribute('latitude', cpP.y())
                        if country == 'AUT':
                            # since find spot is always within site, use meridian of site
                            fSFeature.setAttribute('meridian', meridian)
                            gkFS = TransformGeometry(cpPol, findSpotLayer.crs(), QgsCoordinateReferenceSystem(epsgGK, QgsCoordinateReferenceSystem.EpsgCrsId))
                            fSFeature.setAttribute('gkx', gkFS.asPoint().y())  # Hochwert
                            fSFeature.setAttribute('gky', gkFS.asPoint().x())  # Rechtswert

                        fSFeature.setAttribute('datum_aenderung', now.toString("yyyy-MM-dd"))
                        fSFeature.setAttribute('aktionsdatum', now.toString("yyyy-MM-dd"))
                        fSFeature.setAttribute('aktionsuser', user)

                    findSpotLayer.updateFeature(fSFeature)

                commitRes = findSpotLayer.commitChanges()
                # log
                if commitRes:
                    for log in logs:
                        self.apisLogger(log[0], u"fundstelle", u"fundortnummer = '{0}' AND fundstellenummer = {1}".format(log[1], log[2]))

    def onBeforeCommitChangesFindSpotEditing(self):
        if not self.findSpotLayer.isEditable():
            self.findSpotLayer.startEditing()

        editBuffer = self.findSpotLayer.editBuffer()
        changedGeometriesMap = editBuffer.changedGeometries()
        fids = [fid for fid, geom in changedGeometriesMap.items()]
        request = QgsFeatureRequest()
        request.setFilterFids(fids)
        polygonList = []
        features = self.findSpotLayer.getFeatures(request)

        for feature in features:
            fid = feature.id()
            newGeometry = changedGeometriesMap[fid]
            oldGeometry = feature.geometry()
            siteNumber = feature.attribute('fundortnummer')

            # get corresponding site feature
            expression = QgsExpression("\"fundortnummer\"='{0}'".format(siteNumber))
            siteFeature = self.siteLayer.getFeatures(QgsFeatureRequest(expression)).next()
            country = siteFeature.attribute('land')


            polygonList.append([siteNumber, QgsGeometry(newGeometry)])
            #country = feature.attribute('land')
            # edit and update attributes, affected by geometry change
            feature.setAttribute('flaeche', self.siteAreaHa(newGeometry))

            cpGeom = newGeometry.centroid()
            if not newGeometry.contains(cpGeom):
                cpGeom = newGeometry.pointOnSurface()
            cp = cpGeom.asPoint()
            feature.setAttribute('longitude', cp.x())
            feature.setAttribute('latitude', cp.y())

            if country == 'AUT':
                # get meridian and epsg Code
                meridian, epsgGK = GetMeridianAndEpsgGK(cp.x())

                # get KG Coordinates
                gk = TransformGeometry(cpGeom, self.findSpotLayer.crs(),
                                       QgsCoordinateReferenceSystem(epsgGK, QgsCoordinateReferenceSystem.EpsgCrsId))
                gkx = gk.asPoint().y()  # Hochwert
                gky = gk.asPoint().x()  # Rechtswert
            else:
                meridian = None
                gkx = None
                gky = None

            feature.setAttribute('meridian', meridian)
            feature.setAttribute('gkx', gkx)  # Hochwert
            feature.setAttribute('gky', gky)  # Rechtswert


            now = QDate.currentDate()
            feature.setAttribute('datum_aenderung', now.toString("yyyy-MM-dd"))
            # Aktions
            import getpass
            user = getpass.getuser()
            feature.setAttribute('aktion', 'editG')
            feature.setAttribute('aktionsdatum', now.toString("yyyy-MM-dd"))
            feature.setAttribute('aktionsuser', user)

            self.findSpotLayer.updateFeature(feature)

        self.siteLayer.geometryChanged.disconnect(self.onSiteGeometryEditing)
        self.siteLayer.editCommandEnded.disconnect(self.onEditCommandEnded)
        self.siteLayer.beforeCommitChanges.disconnect(self.onBeforeCommitChanges)
        for findSpot in polygonList:
            siteNumber = findSpot[0]
            newFindSpotGeometry = QgsGeometry(findSpot[1])
            expression = QgsExpression("\"fundortnummer\"='{0}'".format(siteNumber))
            siteFeature = self.siteLayer.getFeatures(QgsFeatureRequest(expression)).next()

            siteGeometry = QgsGeometry(siteFeature.geometry())
            #QMessageBox.information(None, "FindSpot", u"{0},{1}".format(siteNumber, newFindSpotGeometry))


            if siteGeometry.intersects(newFindSpotGeometry) and not siteGeometry.contains(newFindSpotGeometry):
                newSiteGeometry = siteGeometry.combine(newFindSpotGeometry)

                if not self.siteLayer.isEditable():
                    self.siteLayer.startEditing()

                siteFeature.setGeometry(newSiteGeometry)
                country = siteFeature.attribute('land')
                # edit and update attributes, affected by geometry change
                siteFeature.setAttribute('flaeche', self.siteAreaHa(newSiteGeometry))

                cpGeom = newSiteGeometry.centroid()
                if not newSiteGeometry.contains(cpGeom):
                    cpGeom = newSiteGeometry.pointOnSurface()
                cp = cpGeom.asPoint()
                siteFeature.setAttribute('longitude', cp.x())
                siteFeature.setAttribute('latitude', cp.y())

                if country == 'AUT':
                    # get meridian and epsg Code
                    meridian, epsgGK = GetMeridianAndEpsgGK(cp.x())

                    # get KG Coordinates
                    gk = TransformGeometry(cpGeom, self.siteLayer.crs(),
                                           QgsCoordinateReferenceSystem(epsgGK, QgsCoordinateReferenceSystem.EpsgCrsId))
                    gkx = gk.asPoint().y()  # Hochwert
                    gky = gk.asPoint().x()  # Rechtswert
                else:
                    meridian = None
                    gkx = None
                    gky = None

                siteFeature.setAttribute('meridian', meridian)
                siteFeature.setAttribute('gkx', gkx)  # Hochwert
                siteFeature.setAttribute('gky', gky)  # Rechtswert


                now = QDate.currentDate()
                siteFeature.setAttribute('datum_aenderung', now.toString("yyyy-MM-dd"))
                # Aktions
                import getpass
                user = getpass.getuser()
                siteFeature.setAttribute('aktion', 'editG')
                siteFeature.setAttribute('aktionsdatum', now.toString("yyyy-MM-dd"))
                siteFeature.setAttribute('aktionsuser', user)

                self.siteLayer.updateFeature(siteFeature)


                resCommit = self.siteLayer.commitChanges()

        self.siteLayer.geometryChanged.connect(self.onSiteGeometryEditing)
        self.siteLayer.editCommandEnded.connect(self.onEditCommandEnded)
        self.siteLayer.beforeCommitChanges.connect(self.onBeforeCommitChanges)



    def onSiteGeometryEditing(self, fid, geom):
        self.lastGeometryChange = [fid, geom]
        #self.changedGeometries[fid] = [geom]
        #QMessageBox.warning(None, self.tr(u"Site Mapping"), u"Geom Edited, {0}, {1}".format(fid, geom))

    def onFindSpotGeometryEditing(self, fid, geom):
        self.lastFindSpotGeometryChange = [fid, geom]

    def onEditCommandEnded(self):
        #QMessageBox.warning(None, self.tr(u"Site Mapping"), u"Edit Command ended!")
        #check if geometries are simple
        fid = self.lastGeometryChange[0]
        newGeometry = self.lastGeometryChange[1]
        request = QgsFeatureRequest()
        request.setSubsetOfAttributes(['land'], self.siteLayer.pendingFields()) #deletes other attributes on update! Only use when do OnlyReading! - like here now!
        request.setFilterFid(fid)

        features = self.siteLayer.getFeatures(request)
        for feature in features:
            oldCountry = feature.attribute('land')

        if not self.passGeometryCheck(newGeometry):
            QMessageBox.warning(None, self.tr(u"Site Mapping"), u"Die vorgenommenen Veränderungen sind nicht zulässig!")
            self.siteLayer.destroyEditCommand()
            return

        if not self.passCountryCheck(oldCountry, newGeometry):
            QMessageBox.warning(None, u"IntersectingCountries", u"Das neue Fundortpolygon befindet sich nicht mehr im bisherigen Land ({0}). Bitte erstellen Sie dazu einen neuen Fundort.".format(oldCountry))
            self.siteLayer.destroyEditCommand()
            return

    def onFindSpotEditCommandEnded(self):
        fid = self.lastFindSpotGeometryChange[0]
        newFindSpotGeometry = self.lastFindSpotGeometryChange[1]

        if not self.passGeometryCheck(newFindSpotGeometry):
            QMessageBox.warning(None, self.tr(u"Site Mapping"), u"Die vorgenommenen Veränderungen sind nicht zulässig!")
            self.findSpotLayer.destroyEditCommand()
            return

        request = QgsFeatureRequest()
        request.setSubsetOfAttributes(['fundortnummer'], self.findSpotLayer.pendingFields())  # deletes other attributes on update! Only use when do OnlyReading! - like here now!
        request.setFilterFid(fid)
        findSpotFeature = self.findSpotLayer.getFeatures(request).next()
        siteNumber = findSpotFeature.attribute('fundortnummer')

        # get corresponding site feature
        expression = QgsExpression("\"fundortnummer\"='{0}'".format(siteNumber))
        siteFeature = self.siteLayer.getFeatures(QgsFeatureRequest(expression)).next()

        siteGeometry = QgsGeometry(siteFeature.geometry())
        oldCountry = siteFeature.attribute('land')

        if siteGeometry.disjoint(newFindSpotGeometry):
            QMessageBox.warning(None, self.tr(u"Site Mapping"), u"Die Fundstelle darf nicht zur Gänze auserhalb des Fundortes liegen! Ändern Sie zuerst den Fundort!")
            self.findSpotLayer.destroyEditCommand()
            return
        elif siteGeometry.contains(newFindSpotGeometry):
            # alles OK, kein Site edit nötig
            pass
        elif siteGeometry.intersects(newFindSpotGeometry):
            #if new geometry intersects > do expand siteGeometry > geometry Check > Country Check
            newSiteGeometry = siteGeometry.combine(newFindSpotGeometry)
            if not self.passGeometryCheck(newSiteGeometry):
                QMessageBox.warning(None, self.tr(u"Site Mapping"), u"Die vorgenommenen Veränderungen sind nicht zulässig!")
                self.findSpotLayer.destroyEditCommand()
                return

            if not self.passCountryCheck(oldCountry, newSiteGeometry):
                QMessageBox.warning(None, u"IntersectingCountries",
                                    u"Das neue Fundortpolygon befindet sich nicht mehr im bisherigen Land ({0}). Bitte erstellen Sie dazu einen neuen Fundort.".format(
                                        oldCountry))
                self.findSpotLayer.destroyEditCommand()
                return



    def onEditCommandStarted(self, text):
        QMessageBox.warning(None, self.tr(u"Site Mapping"), u"Edit Command started: {0}".format(text))

    def onFilmOrProjectChanged(self, text):
        self.uiImageNumberEdit.setEnabled(False)
        self.uiImageNumberEdit.setText('-1')
        if len(text.strip()) == 0:
            self.uiSiteMappingModesGrp.setEnabled(False)
        else:
            self.uiSiteMappingModesGrp.setEnabled(True)

    def onCheckIfFilm(self):
        if IsFilm(self.dbm.db, self.uiFilmOrProjectEdit.text()):
            QMessageBox.warning(None, self.tr(u"Site Mapping"), u"{0} ist ein bestehender Film".format(self.uiFilmOrProjectEdit.text()))
            # Bildnummer Freischalten
            self.uiImageNumberEdit.setEnabled(True)
        else:
            QMessageBox.warning(None, self.tr(u"Site Mapping"), u"{0} ist kein Film".format(self.uiFilmOrProjectEdit.text()))
            self.uiImageNumberEdit.setEnabled(False)
            self.uiImageNumberEdit.setText('-1')


    def addNewSite(self):
        # QMessageBox.warning(None, u"Film Nummer", u"0},{1},{2}".format(self.imageCenterPoint.x(), self.imageCenterPoint.y(), type(self.imageCenterPoint)))
        # return

        self.reloadSiteLayer()

        #transform pointGeom and polyGeom from sourceCrs to siteLayerCrs
        ctFwd = QgsCoordinateTransform(self.crs, self.siteLayer.crs())
        self.point.transform(ctFwd)
        self.polygon.transform(ctFwd)

        countryCode = self.getCountryCode(self.polygon)
        siteNumberNN = self.getNextSiteNumberForCountry(countryCode)
        siteNumber = u"{0}.{1}".format(countryCode, siteNumberNN)
        siteArea = self.siteAreaHa(self.polygon)

        #QMessageBox.warning(None, u"CoutnryCode", u"{0}.{1}, Fläche: {2}".format(countryCode, siteNumber, siteArea))


        caps = self.siteLayer.dataProvider().capabilities()
        if caps & QgsVectorDataProvider.AddFeatures:
            features = []

            feat = QgsFeature(self.siteLayer.pendingFields())
            feat.setGeometry(self.polygon)

            #Get Country Code

            feat.setAttribute('land', countryCode)
            feat.setAttribute('flaeche', siteArea)

            #Get Fundortnummer NN based on Country

            feat.setAttribute('fundortnummer', siteNumber)
            feat.setAttribute('fundortnummer_nn', siteNumberNN)

            filmNumber = self.uiFilmOrProjectEdit.text().strip()
            imgNumber = self.uiImageNumberEdit.text().strip() if len(self.uiImageNumberEdit.text().strip()) > 0 else '-1'
            feat.setAttribute('filmnummer_projekt', filmNumber)
            feat.setAttribute('bildnummer', imgNumber)

            isFilmBased = False
            if IsFilm(self.dbm.db, filmNumber):
                feat.setAttribute('befund', "{0}/{1}: ".format(filmNumber, imgNumber))
                isFilmBased = True

            # Date TODAY
            now = QDate.currentDate()
            feat.setAttribute('datum_ersteintrag', now.toString("yyyy-MM-dd"))
            feat.setAttribute('datum_aenderung', now.toString("yyyy-MM-dd"))
            feat.setAttribute('erstmeldung_jahr', now.toString("yyyy"))

            # Aktions
            import getpass
            feat.setAttribute('aktion', 'new')
            feat.setAttribute('aktionsdatum', now.toString("yyyy-MM-dd"))
            feat.setAttribute('aktionsuser', getpass.getuser())

            # Calculated/Derived
            p = self.point.asPoint()
            feat.setAttribute('longitude', p.x())
            feat.setAttribute('latitude', p.y())

            if countryCode == 'AUT':
                # get meridian and epsg Code
                meridian, epsgGK = GetMeridianAndEpsgGK(p.x())
                feat.setAttribute('meridian', meridian)

                gk = TransformGeometry(QgsGeometry(self.point), self.siteLayer.crs(), QgsCoordinateReferenceSystem(epsgGK, QgsCoordinateReferenceSystem.EpsgCrsId))
                feat.setAttribute('gkx', gk.asPoint().y())  # Hochwert
                feat.setAttribute('gky', gk.asPoint().x())  # Rechtswert

                # KG Name und Nummer
                kgCode, kgName = self.getKgNameAndCode(self.polygon)
                feat.setAttribute('katastralgemeindenummer', kgCode)
                feat.setAttribute('katastralgemeinde', kgName)
                #QMessageBox.warning(None, u"CoutnryCode", u"{0} - {1}".format(kgCode, kgName))

                siteNumberLegacy, siteNumberNNLegacy = self.getSiteNumberLegacy(kgCode)

                feat.setAttribute('fundortnummer_legacy', siteNumberLegacy)
                feat.setAttribute('fundortnummer_nn_legacy', siteNumberNNLegacy)

            features.append(feat)

            (res, outFeats) = self.siteLayer.dataProvider().addFeatures(features)
            self.siteLayer.updateExtents()

            self.openSiteDialogInAddMode(siteNumber, isFilmBased)
        else:
            QMessageBox.warning(None, u"Layer Capabilities!")

        if self.canvas.isCachingEnabled():
            self.siteLayer.setCacheImage(None)
        else:
            self.canvas.refresh()


    def siteAreaHa(self, polygon):
        a = QgsDistanceArea()
        a.setEllipsoidalMode(True)
        a.setEllipsoid("bessel")
        a.setSourceCrs(self.siteLayer.crs())
        return a.convertAreaMeasurement(a.measureArea(polygon), QgsUnitTypes.Hectares)


    def checkEditSite(self):

        self.reloadSiteLayer()

        # datctivate mapping tools
        self.uiMapPointAndSquareBtn.setChecked(False)
        self.uiMapPolygonAndPointBtn.setChecked(False)

        # transform pointGeom and polyGeom from sourceCrs to siteLayerCrs
        ctFwd = QgsCoordinateTransform(self.crs, self.siteLayer.crs())
        self.point.transform(ctFwd)
        self.polygon.transform(ctFwd)

        # get final geometry
        # check if intersection with other sites
        intersectingSites = self.doesIntersectSites(self.polygon)
        if not intersectingSites:
            QMessageBox.warning(None, u"IntersectingSites", u"Keine bestehenden Fundorte im Kartierten Bereich. Sie können eine Fundortnummer manuell angeben.")
            self.provideSiteManually()
        else:
            self.uiAddToSiteByIntersectionGrp.setVisible(True)
            self.uiSiteMappingModesGrp.setEnabled(False)
            self.uiIntersectingSitesCombo.clear()
            self.uiIntersectingSitesCombo.addItems(intersectingSites)
            self.selectEditCandidateSite(0)


    def addToSelectedSite(self): #editSelectedSite
        siteNumber, feature = self.prepareSelectedSiteEditing()

        oldGeometry = feature.geometry()
        oldCountry = feature.attribute("land")

        # combine both geometries
        newGeometry = oldGeometry.combine(self.polygon)

        # alternative to combine: make multipart
        #newGeometry = QgsGeometry(oldGeometry)
        #newGeometry.convertToMultiType()
        #newGeometry.addPartGeometry(self.polygon)
        #newGeometry.convertToSingleType()

        if not self.passGeometryCheck(newGeometry):
            QMessageBox.warning(None, u"Fundort Update", u"Die Geometrie des neue Fundortpolygons ist nicht gültig.")
            self.onCancelAnyEdits()
            return

        #QMessageBox.warning(None, u"IntersectingCountries", u"{0}".format(newGeometry.exportToWkt()))

        if not self.passCountryCheck(oldCountry, newGeometry):
            QMessageBox.warning(None, u"IntersectingCountries", u"Das neue Fundortpolygon befindet sich nicht mehr im bisherigen Land ({0}). Bitte erstellen Sie dazu einen neuen Fundort.".format(oldCountry))
            self.onCancelAnyEdits()
            return

        #QMessageBox.warning(None, u"IntersectingCountries", u"{0}".format(", ".join(intersectingCountries)))
        #QMessageBox.warning(None, u"IntersectingCountries", u"{0} U {1} = {2}".format(oa, self.siteAreaHa(self.polygon), self.siteAreaHa(newGeometry)))
        #QMessageBox.warning(None, u"IntersectingCountries", u"{0}, {1}".format(oldCountry, self.getCountryCode(newGeometry)))


        self.doSiteEditing(siteNumber, newGeometry, QgsGeometry(oldGeometry), oldCountry)



    def replaceSelectedSite(self):
        siteNumber, feature = self.prepareSelectedSiteEditing()

        oldGeometry = feature.geometry()
        oldCountry = feature.attribute("land")

        if not self.passGeometryCheck(self.polygon):
            QMessageBox.warning(None, u"Fundort Update", u"Die Geometrie des neue Fundortpolygons ist nicht gültig.")
            self.onCancelAnyEdits()
            return

        if not self.passCountryCheck(oldCountry, self.polygon):
            QMessageBox.warning(None, u"IntersectingCountries", u"Das neue Fundortpolygon befindet sich nicht mehr im bisherigen Land ({0}). Bitte erstellen Sie dazu einen neuen Fundort.".format(oldCountry))
            self.onCancelAnyEdits()
            return

        self.doSiteEditing(siteNumber, self.polygon, QgsGeometry(oldGeometry), oldCountry)


    def prepareSelectedSiteEditing(self):
        self.reloadSiteLayer()
        # get feature of selected site
        siteNumber = self.uiIntersectingSitesCombo.currentText()
        # select Site by Attribute Where fundortnummer = siteNumber
        expression = QgsExpression("\"fundortnummer\"='{0}'".format(siteNumber))
        feature = self.siteLayer.getFeatures(QgsFeatureRequest(expression)).next()
        return siteNumber, feature

    def passGeometryCheck(self, polygon):
        #QMessageBox.warning(None, u"IntersectingCountries", u"{0}, {1}, {2}".format(polygon.isMultipart(), not polygon.isGeosValid(), polygon.isGeosEmpty()))
        return not polygon.isMultipart() or polygon.isGeosValid() or not polygon.isGeosEmpty()

    def passCountryCheck(self, country, polygon):
        return country in self.doesIntersectCountries(polygon)

    def doSiteEditing(self, siteNumber, polygon, oldPolygon, country):

        siteArea = self.siteAreaHa(polygon)
        if country == 'AUT':
            kgCode, kgName = self.getKgNameAndCode(polygon)
        else:
            kgCode = None
            kgName = None

        editsSaved = self.openSiteDialogInEditMode(siteNumber, polygon, oldPolygon, country, kgCode, kgName, siteArea)

        # open Dialog in editMode if cancel do not commit Changes but cancel Editing some rollback!

    def saveSiteEdits(self, dialog, siteNumber, polygon, oldPolygon, country, fSEditActions):

        if True: #editsSaved:
            self.siteLayer.reload()
            #reload feature > since changed in Dialog!!!!
            expression = QgsExpression("\"fundortnummer\"='{0}'".format(siteNumber))
            feature = self.siteLayer.getFeatures(QgsFeatureRequest(expression)).next()
            self.siteLayer.startEditing()
            feature.setGeometry(polygon)

            # if center point is not on polygon get the nearest Point
            cpGeom = polygon.centroid()
            if not polygon.contains(cpGeom):
                cpGeom = polygon.pointOnSurface()
            cp = cpGeom.asPoint()
            feature.setAttribute('longitude', cp.x())
            feature.setAttribute('latitude', cp.y())

            # Aktions
            import getpass
            user = getpass.getuser()
            now = QDate.currentDate()
            feature.setAttribute('aktion', 'editAG')
            feature.setAttribute('aktionsdatum', now.toString("yyyy-MM-dd"))
            feature.setAttribute('aktionsuser', user)
            gk = None
            meridian = None
            epsgGK = None
            if country == 'AUT':
                # get meridian and epsg Code
                meridian, epsgGK = GetMeridianAndEpsgGK(cp.x())
                feature.setAttribute('meridian', meridian)
                # get KG Coordinates
                gk = TransformGeometry(cpGeom, self.siteLayer.crs(), QgsCoordinateReferenceSystem(epsgGK, QgsCoordinateReferenceSystem.EpsgCrsId))
                feature.setAttribute('gkx', gk.asPoint().y())  # Hochwert
                feature.setAttribute('gky', gk.asPoint().x())  # Rechtswert

            # Fundstellen des Fundortes Editieren
            uri = QgsDataSourceURI()
            uri.setDatabase(self.dbm.db.databaseName())
            uri.setDataSource('', 'fundstelle', 'geometry')
            findSpotLayer = QgsVectorLayer(uri.uri(), u'Fundstelle', 'spatialite')
            findSpotLayer.setSubsetString(u'"fundortnummer" = "{0}"'.format(siteNumber))

            if findSpotLayer.featureCount() > 0:
                logs = []
                findSpotLayer.startEditing()
                fSIter = findSpotLayer.getFeatures()
                for fSFeature in fSIter:
                    fSGeom = fSFeature.geometry()
                    sN = fSFeature.attribute("fundortnummer")
                    fSN = fSFeature.attribute("fundstellenummer")
                    fSNumber = u"{0}.{1}".format(sN, fSN)

                    if fSEditActions[fSNumber] == 1:
                        # findSpot Polygon gets same geometry, attributes as sitePolygon
                        fSFeature.setGeometry(polygon)
                        #area allready commited in siteLayer
                        fSFeature.setAttribute('flaeche', feature.attribute('flaeche'))
                        #other values (above) not yet commited, so use values/variables from above
                        fSFeature.setAttribute('longitude', cp.x())
                        fSFeature.setAttribute('latitude', cp.y())
                        if country == 'AUT':
                            fSFeature.setAttribute('meridian', meridian)
                            fSFeature.setAttribute('gkx', gk.asPoint().y())  # Hochwert
                            fSFeature.setAttribute('gky', gk.asPoint().x())  # Rechtswert

                        fSFeature.setAttribute('aktion', 'editG1')
                        logs.append([u"editG1", sN, fSN])
                    elif fSEditActions[fSNumber] == 2:
                        # findSpot Polygon is different from sitePolygon
                        pol = fSGeom.intersection(polygon)
                        fSFeature.setGeometry(pol)
                        fSFeature.setAttribute('flaeche', self.siteAreaHa(pol))

                        # if center point is not on polygon get the nearest Point
                        cpPol = pol.centroid()
                        if not pol.contains(cpPol):
                            cpPol = pol.pointOnSurface()
                        cpP = cpPol.asPoint()
                        fSFeature.setAttribute('longitude', cpP.x())
                        fSFeature.setAttribute('latitude', cpP.y())
                        if country == 'AUT':
                            #since find spot is always within site, use meridian of site
                            fSFeature.setAttribute('meridian', meridian)
                            gkFS = TransformGeometry(cpPol, findSpotLayer.crs(),QgsCoordinateReferenceSystem(epsgGK, QgsCoordinateReferenceSystem.EpsgCrsId))
                            fSFeature.setAttribute('gkx', gkFS.asPoint().y())  # Hochwert
                            fSFeature.setAttribute('gky', gkFS.asPoint().x())  # Rechtswert

                        fSFeature.setAttribute('aktion', 'editG2')
                        logs.append([u"editG2", sN, fSN])

                    if fSEditActions[fSNumber] == 1 or fSEditActions[fSNumber] == 2:
                        fSFeature.setAttribute('datum_aenderung', now.toString("yyyy-MM-dd"))
                        fSFeature.setAttribute('aktionsdatum', now.toString("yyyy-MM-dd"))
                        fSFeature.setAttribute('aktionsuser', user)

                    findSpotLayer.updateFeature(fSFeature)


                commitRes = findSpotLayer.commitChanges()

                #log
                if commitRes:
                    for log in logs:
                        self.apisLogger(log[0], u"fundstelle", u"fundortnummer = '{0}' AND fundstellenummer = {1}".format(log[1], log[2]))

            self.siteLayer.updateFeature(feature)
            self.siteLayer.commitChanges()
            self.siteLayer.updateExtents()

            if self.canvas.isCachingEnabled():
                self.siteLayer.setCacheImage(None)
            else:
                self.canvas.refresh()
                # else:
                # self.siteLayer.rollBack()

            #dialog.removeSitesFromSiteMapCanvas()
            #dialog.loadSiteInSiteMapCanvas()
            dialog.reloadMapCanvas()

            # log
            self.apisLogger(u"editAG", u"fundort", u"fundortnummer = '{0}' ".format(siteNumber))

        self.onCancelAnyEdits()

    def discardSiteEdits(self, dialog):
        self.onCancelAnyEdits()
        #dialog.removeSitesFromSiteMapCanvas()
        #dialog.loadSiteInSiteMapCanvas()
        dialog.reloadMapCanvas()

    def allGeometriesEquals(self, layer, poly):
        #QMessageBox.warning(None, u"Fundort Update", u"{0}.".format(poly))
        iter = layer.getFeatures()
        for feat in iter:
            geom = feat.geometry()
            if not geom.equals(poly):
                return False
        return True

    def apisLogger(self, action, fromTable, primaryKeysWhere):
        toTable = fromTable + u"_log"
        query = QSqlQuery(self.dbm.db)
        query.prepare(u"INSERT INTO {0} SELECT * FROM {1} WHERE {2}".format(toTable, fromTable, primaryKeysWhere))

        res = query.exec_()
        #QMessageBox.information(None, "SqlQuery", query.executedQuery())
        if not res:
            QMessageBox.information(None, "SqlError", query.lastError().text())
        import getpass
        query.prepare(u"UPDATE {0} SET aktion = '{1}', aktionsdatum = '{2}', aktionsuser = '{3}' WHERE rowid = (SELECT max(rowid) FROM {0})".format(toTable, action, QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss"), getpass.getuser(), primaryKeysWhere))
        res = query.exec_()
        #QMessageBox.information(None, "SqlQuery", query.executedQuery())
        if not res:
            QMessageBox.information(None, "SqlError", query.lastError().text())

    def replaceProvidedSite(self):
        siteNumber, feature = self.prepareProvidedSiteEditing()
        #QMessageBox.warning(None, u"Fundort Update", u"{0}, {1}".format(siteNumber, feature))
        #
        if feature == None:
            QMessageBox.warning(None, u"Fundort Update", u"Der Fundort ({0}) existiert nicht.".format(siteNumber))
            #self.onCancelAnyEdits()
            self.uiProvidedSiteNumberEdit.setText("AUT.")
            return

        if not self.passGeometryCheck(self.polygon):
            QMessageBox.warning(None, u"Fundort Update", u"Die Geometrie des neue Fundortpolygons ist nicht gültig.")
            self.onCancelAnyEdits()
            return

        oldCountry = feature.attribute("land")
        if not self.passCountryCheck(oldCountry, self.polygon):
            QMessageBox.warning(None, u"IntersectingCountries",
                                u"Das neue Fundortpolygon befindet sich nicht mehr im bisherigen Land ({0}). Bitte erstellen Sie dazu einen neuen Fundort.".format(
                                    oldCountry))
            self.onCancelAnyEdits()
            return

        # additional warning!
        oldGeometry = feature.geometry()

        d = QgsDistanceArea()
        # d.setEllipsoidalMode(True)
        # d.setSourceCrs(self.siteLayer.crs())
        distD = d.measureLine(oldGeometry.centroid().asPoint(), self.point.asPoint())
        distM = d.convertMeasurement(distD, 2, 0, False)
        #unit = d.lengthUnits()
       # dist = d.convertLengthMeasurement(d.measureLine(oldGeometry.centroid().asPoint(), self.point.asPoint()), 8) #QGis.UnitType.Kilometers = 8

        header = self.tr(u"Fundort Update")
        question = self.tr(u"Warnung: der bestehende Fundort ({0}) befindet sich {1:.2f} km vom kartierten Fundort entfernt! Wollen Sie wirklich den Fundort editierren?")
        question = question.format(siteNumber, distM[0]/1000)

        result = QMessageBox.question(None,
                                  header,
                                  question,
                                  QMessageBox.Yes | QMessageBox.No,
                                  QMessageBox.Yes)

        # save or not save
        if result == QMessageBox.No:
            self.onCancelAnyEdits()
            return


        self.doSiteEditing(siteNumber, self.polygon, QgsGeometry(oldGeometry), oldCountry)


    def prepareProvidedSiteEditing(self):
        self.reloadSiteLayer()
        # get feature of selected site
        siteNumber = self.uiProvidedSiteNumberEdit.text()

        # select Site by Attribute Where fundortnummer = siteNumber
        expression = QgsExpression("\"fundortnummer\"='{0}'".format(siteNumber))
        featureIt = self.siteLayer.getFeatures(QgsFeatureRequest(expression))

        feature = None
        for f in featureIt:
            feature = f
        return siteNumber, feature


    def provideSiteManually(self):
        self.uiAddToSiteByIntersectionGrp.setVisible(False)
        self.uiAddToSiteManuallyGrp.setVisible(True)
        self.uiSiteMappingModesGrp.setEnabled(False)

    def editSite(self, pointGeom, polygonGeom, sourceCrs):
        pass

    def getCountryCode(self, polygon):
        polygonWkt = polygon.exportToWkt()
        query = QSqlQuery(self.dbm.db)
        # Check if Polygon is in Austria or Parts of it?
        qryStr = "SELECT code FROM osm_boundaries WHERE code = 'AUT' AND intersects(Transform(GeomFromText('{0}', 4312), 4326), geometry) AND ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'osm_boundaries' AND search_frame = Transform(GeomFromText('{0}', 4312), 4326))".format(polygonWkt)
        query.exec_(qryStr)
        query.first()
        if query.value(0) == 'AUT':
            return 'AUT'
        else:

            qryStr = "SELECT CASE WHEN code IS NULL THEN 'INT' ELSE code END as code, max(Area(intersection(Transform(GeomFromText('{0}', 4312), 4326), geometry) , 1) ) as area FROM osm_boundaries WHERE intersects(Transform(GeomFromText('{0}', 4312), 4326), geometry) AND ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'osm_boundaries' AND search_frame = Transform(GeomFromText('{0}', 4312), 4326))".format(polygonWkt)
            query.exec_(qryStr)
            query.first()
            if query.value(0) is None:
                return 'INT'
            else:
                return query.value(0)

    def getNextSiteNumberForCountry(self, country):
        query = QSqlQuery(self.dbm.db)
        qryStr = "select CASE WHEN max(fundortnummer_nn) IS NULL THEN 1 ELSE max(fundortnummer_nn)+1 END as nextSite from fundort where land = '{0}'".format(country)
        query.exec_(qryStr)
        query.first()
        return query.value(0)

    def getSiteNumberLegacy(self, kgCode):
        query = QSqlQuery(self.dbm.db)
        qryStr = "SELECT CASE WHEN MAX(fundortnummer_nn_legacy) IS NULL THEN 1 ELSE MAX(fundortnummer_nn_legacy)+1 END AS nextSiteLegacy from fundort where katastralgemeindenummer = '{0}'".format(kgCode)
        query.exec_(qryStr)
        query.first()
        nn = query.value(0)
        return u"{0}.{1}".format(kgCode, nn), nn

    def getKgNameAndCode(self, polygon):
        polygonWkt = polygon.exportToWkt()
        query = QSqlQuery(self.dbm.db)
        qryStr = "SELECT katastralgemeindenummer, katastralgemeindename, MAX(Area(Intersection(Transform(GeomFromText('{0}', 4312), 31287), geometry))) as area FROM katastralgemeinden WHERE intersects(Transform(GeomFromText('{0}', 4312), 31287), geometry) AND ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'katastralgemeinden' AND search_frame = Transform(GeomFromText('{0}', 4312), 31287))".format(polygonWkt)
        query.exec_(qryStr)
        query.first()
        if query.value(0) is None:
            return 'INT'
        else:
            return query.value(0), query.value(1)

    def doesIntersectSites(self, polygon):
        polygonWkt = polygon.exportToWkt()
        query = QSqlQuery(self.dbm.db)
        qryStr = "SELECT fundortnummer FROM fundort WHERE Intersects(GeomFromText('{0}', 4312), geometry) AND ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'fundort' AND search_frame = GeomFromText('{0}', 4312))".format(polygonWkt)
        query.exec_(qryStr)
        intersectingSites = []
        while query.next():
            intersectingSites.append(query.value(0))
        return intersectingSites


    def doesIntersectCountries(self, polygon):
        polygonWkt = polygon.exportToWkt()
        query = QSqlQuery(self.dbm.db)
        qryStr = "SELECT code FROM osm_boundaries WHERE Intersects(Transform(GeomFromText('{0}', 4312), 4326), geometry) AND ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'osm_boundaries' AND search_frame = Transform(GeomFromText('{0}', 4312), 4326))".format(polygonWkt)
        query.exec_(qryStr)
        intersectingCountries = []
        while query.next():
            intersectingCountries.append(query.value(0))
        return intersectingCountries

    def selectEditCandidateSite(self, siteNumberIdx):
        self.reloadSiteLayer()
        siteNumber = self.uiIntersectingSitesCombo.itemText(siteNumberIdx)
        # select Site by Attribute Where fundortnummer = siteNumber
        expression = QgsExpression("\"fundortnummer\"='{0}'".format(siteNumber))
        featureIterator = self.siteLayer.getFeatures(QgsFeatureRequest(expression))
        id = [feature.id() for feature in featureIterator]
        self.siteLayer.setSelectedFeatures( id )


    def openSiteDialogInAddMode(self, siteNumber, isFilmBased):
        self.siteLayer.beforeCommitChanges.disconnect(self.onBeforeCommitChanges)
        siteDlgAdd = ApisSiteDialog(self.iface, self.dbm, self.imageRegistry, self.apisLayer)
        siteDlgAdd.openInAddMode(siteNumber, isFilmBased)
        siteDlgAdd.show()
        # Run the dialog event loop

        if siteDlgAdd.exec_():
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
        siteDlgAdd.removeSitesFromSiteMapCanvas()
        self.onCancelAnyEdits()
        self.siteLayer.beforeCommitChanges.connect(self.onBeforeCommitChanges)

        # QMessageBox.warning(None, self.tr(u"Load Site"), self.tr(u"For Site: {0}".format(siteNumber)))


    def openSiteDialogInEditMode(self, siteNumber, newPolygon, oldPolygon, country, kgCode, kgName, siteArea):
        self.siteLayer.beforeCommitChanges.disconnect(self.onBeforeCommitChanges)
        siteDlgEdit = ApisSiteDialog(self.iface, self.dbm, self.imageRegistry, self.apisLayer)
        siteDlgEdit.siteAndGeometryEditsSaved.connect(self.saveSiteEdits)
        siteDlgEdit.siteAndGeometryEditsCanceled.connect(self.discardSiteEdits)
        siteDlgEdit.openInEditMode(siteNumber, newPolygon, oldPolygon, country, kgCode, kgName, siteArea)
        siteDlgEdit.show()
        #QMessageBox.information(None, "info", u"{0}".format(res1))
        #if siteDlgEdit.isActive:
        res = siteDlgEdit.exec_()
        siteDlgEdit.removeSitesFromSiteMapCanvas()
        self.onCancelAnyEdits()
        self.siteLayer.beforeCommitChanges.connect(self.onBeforeCommitChanges)
        #else:
            #self.onCancelAnyEdits()


        # were edits saved (if not do not alter geometry)
        #isGeometrySaved = siteDlgEdit.isGeometrySaved()
        #QMessageBox.warning(None, self.tr(u"Load Site"), self.tr(u"res: {0}".format(editStatus)))

        return

            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            #pass