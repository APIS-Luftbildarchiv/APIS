# -*- coding: utf-8 -*

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from qgis.core import *
from qgis.gui import *
from apis_db_manager import *
from apis_map_tools import *
import sys, os, math, string
import os.path

from apis_site_dialog import *

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

# --------------------------------------------------------
# Fundort - Eingabe
# --------------------------------------------------------
from apis_site_mapping_form import *

class ApisSiteMappingDialog(QDockWidget, Ui_apisSiteMappingDialog):
    def __init__(self, iface, dbm):
        QDockWidget.__init__(self)
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.setupUi(self)
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)
        self.dbm = dbm
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self)
        self.hide()

        self.point = None
        self.polygon = None
        self.crs = None


        self.siteLayerId = None
        self.siteLayer = None

        self.changedGeometries = {}

        self.uiSiteMappingModesGrp.setEnabled(False)

        self.uiAddToSiteManuallyGrp.setVisible(False)
        self.uiAddToSiteByIntersectionGrp.setVisible(False)

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


    def onCancelAnyEdits(self):
        # CleanUp Map Canvas
        self.cleanUpMapCanvas()
        # Reset UI
        self.onNewSiteChanged()

    def cleanUpMapCanvas(self):
        # deselect
        self.siteLayer.removeSelection()
        # remove map tool rRubberBands/VertexMarker
        self.siteMapToolByPoint.clearScene()
        self.siteMapToolByPolygon.clearScene()


    def onNewSiteChanged(self):
        self.uiMapPointAndSquareBtn.setChecked(False)
        self.uiMapPolygonAndPointBtn.setChecked(False)

        self.uiAddToSiteManuallyGrp.setVisible(False)
        self.uiAddToSiteByIntersectionGrp.setVisible(False)

        if self.siteLayer and self.siteLayer.isEditable() and not self.uiEditGeometryRBtn.isChecked():
            self.siteLayer.rollBack()

        if self.uiNewSiteYesRBtn.isChecked():
            # Add New Site
            self.uiNewSiteInterpretationGrp.setEnabled(True)
            self.uiSiteMappingModesGrp.setVisible(True)
            self.uiSiteMappingModesGrp.setEnabled(False)
            self.uiNewSiteInterpretationGrp.setEnabled(True)
            self.uiNewSiteInterpretationGrp.setVisible(True)
        elif self.uiNewSiteNoRBtn.isChecked():
            # Add To Existing Site
            self.uiNewSiteInterpretationGrp.setEnabled(False)
            self.uiSiteMappingModesGrp.setVisible(True)
            self.uiSiteMappingModesGrp.setEnabled(True)
            self.uiNewSiteInterpretationGrp.setVisible(False)
        elif  self.uiEditGeometryRBtn.isChecked():
            # siteStart Layer in Edit Mode!

            self.uiSiteMappingModesGrp.setVisible(False)
            self.uiNewSiteInterpretationGrp.setVisible(False)
            self.startEditingSiteLayer()
        else:
            return

    def startEditingSiteLayer(self):
        self.reloadSiteLayer()
        self.siteLayer.startEditing()

    def onVisibilityChanged(self, isVisible):
        #QMessageBox.warning(None, self.tr(u"SearchDialog Visibility"), u"Visibility Search Dialog: {0}".format(visibility))
        if not isVisible:
            # datctivate mapping tools
            self.uiMapPointAndSquareBtn.setChecked(False)
            self.uiMapPolygonAndPointBtn.setChecked(False)

            #unload layers
            self.removeSiteLayer()
        else:
            #load layers
            self.removeSiteLayer()
            self.loadSiteLayer()


    def removeSiteLayer(self):
        if self.siteLayerId in QgsMapLayerRegistry.instance().mapLayers():
            QgsMapLayerRegistry.instance().removeMapLayer(self.siteLayer.id())

    def reloadSiteLayer(self):
        if self.siteLayerId not in QgsMapLayerRegistry.instance().mapLayers():
            self.loadSiteLayer()

    def loadSiteLayer(self):
        uri = QgsDataSourceURI()
        uri.setDatabase(self.dbm.db.databaseName())
        uri.setDataSource('', 'fundort', 'geometry')
        self.siteLayer = QgsVectorLayer(uri.uri(), u'Fundorte', 'spatialite')

        self.siteLayer.geometryChanged.connect(self.onSiteGeometryEditing)
        #self.siteLayer.editCommandEnded.connect(self.onEditCommandEnded)
        #self.siteLayer.editCommandStarted.connect(self.onEditCommandStarted)
        #self.siteLayer.committedGeometriesChanges.connect(self.geometriesChanged)
        self.siteLayer.beforeCommitChanges.connect(self.onBeforeCommitChanges)

        symbol_layer = QgsSimpleLineSymbolLayerV2()
        symbol_layer.setWidth(0.6)
        symbol_layer.setColor(QColor(100, 50, 140, 255))
        self.siteLayer.rendererV2().symbols()[0].changeSymbolLayer(0, symbol_layer)

        QgsMapLayerRegistry.instance().addMapLayer(self.siteLayer)
        self.siteLayerId = self.siteLayer.id()

    def geometriesChanged(self, layerId, changedGeometries):
        for fid, geom in changedGeometries.items():
            QMessageBox.warning(None, self.tr(u"Site Mapping"), u"{0}, {1}".format(fid, geom))

    def onBeforeCommitChanges(self):
        for fid, geom in self.changedGeometries.items():
            QMessageBox.warning(None, self.tr(u"Site Mapping"), u"{0}, {1}".format(fid, geom))
        #QMessageBox.warning(None, self.tr(u"Site Mapping"), u"Before Commit Changes")
        self.changedGeometries.clear()


    def onSiteGeometryEditing(self, fid, geom):
        self.changedGeometries[fid] = geom
        #QMessageBox.warning(None, self.tr(u"Site Mapping"), u"{0}, {1}".format(fid, geom))

    def onEditCommandEnded(self):
        QMessageBox.warning(None, self.tr(u"Site Mapping"), u"Edit Command ended!")

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
        if self.isFilm(self.uiFilmOrProjectEdit.text()):
            QMessageBox.warning(None, self.tr(u"Site Mapping"), u"{0} ist ein bestehender Film".format(self.uiFilmOrProjectEdit.text()))
            # Bildnummer Freischalten
            self.uiImageNumberEdit.setEnabled(True)
        else:
            QMessageBox.warning(None, self.tr(u"Site Mapping"), u"{0} ist kein Film".format(self.uiFilmOrProjectEdit.text()))
            self.uiImageNumberEdit.setEnabled(False)
            self.uiImageNumberEdit.setText('-1')


    def isFilm(self, filmNumber):
        # check if filmNumber is a filmNumber in film Table
        qryStr = "SELECT COUNT(*) FROM film WHERE filmnummer = '{0}'".format(filmNumber)
        query = QSqlQuery(self.dbm.db)
        query.exec_(qryStr)
        query.first()
        return query.value(0)


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

            feat.setAttribute('filmnummer_projekt', self.uiFilmOrProjectEdit.text().strip())
            feat.setAttribute('bildnummer', self.uiImageNumberEdit.text().strip() if len(self.uiImageNumberEdit.text().strip()) > 0 else '-1')

            # Date TODAY
            now = QDate.currentDate()
            feat.setAttribute('datum_ersteintrag', now.toString("yyyy-MM-dd"))
            feat.setAttribute('datum_aenderung', now.toString("yyyy-MM-dd"))

            # Aktions
            import getpass
            feat.setAttribute('aktion', 'added')
            feat.setAttribute('aktionsdatum', now.toString("yyyy-MM-dd"))
            feat.setAttribute('aktionsuser', getpass.getuser())


            # Calculated/Derived
            p = self.point.asPoint()
            feat.setAttribute('longitude', p.x())
            feat.setAttribute('latitude', p.y())



            if countryCode == 'AUT':
                # get meridian and epsg Code
                lon = p.x()
                if lon < 11.8333333333:
                    meridian = 28
                    epsgGK = 31254
                elif lon > 14.8333333333:
                    meridian = 34
                    epsgGK = 31256
                else:
                    meridian = 31
                    epsgGK = 31255
                feat.setAttribute('meridian', meridian)
                gk = QgsGeometry(self.point)
                destGK = QgsCoordinateReferenceSystem()
                destGK.createFromId(epsgGK, QgsCoordinateReferenceSystem.EpsgCrsId)
                ctGK = QgsCoordinateTransform(self.siteLayer.crs(), destGK)
                gk.transform(ctGK)
                feat.setAttribute('gkx', gk.asPoint().y())  # Hochwert
                feat.setAttribute('gky', gk.asPoint().x())  # Rechtswert

                # KG Name und Nummer
                kgCode, kgName = self.getKgNameAndCode(self.polygon)
                feat.setAttribute('katastralgemeindenummer', kgCode)
                feat.setAttribute('katastralgemeinde', kgName)
                #QMessageBox.warning(None, u"CoutnryCode", u"{0} - {1}".format(kgCode, kgName))

            features.append(feat)

            (res, outFeats) = self.siteLayer.dataProvider().addFeatures(features)
            self.siteLayer.updateExtents()

            self.openSiteDialog(siteNumber)
        else:
            QMessageBox.warning(None, u"Layer Capabilities!")

        if self.canvas.isCachingEnabled():
            self.siteLayer.setCacheImage(None)
        else:
            self.canvas.refresh()


    def siteAreaHa(self, polygon):
        a = QgsDistanceArea()
        a.setEllipsoidalMode(True)
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


        self.doSiteEditing(siteNumber, feature, newGeometry, oldCountry)



    def replaceSelectedSite(self):
        siteNumber, feature = self.prepareSelectedSiteEditing()

        oldCountry = feature.attribute("land")

        if not self.passGeometryCheck(self.polygon):
            QMessageBox.warning(None, u"Fundort Update", u"Die Geometrie des neue Fundortpolygons ist nicht gültig.")
            self.onCancelAnyEdits()
            return

        if not self.passCountryCheck(oldCountry, self.polygon):
            QMessageBox.warning(None, u"IntersectingCountries", u"Das neue Fundortpolygon befindet sich nicht mehr im bisherigen Land ({0}). Bitte erstellen Sie dazu einen neuen Fundort.".format(oldCountry))
            self.onCancelAnyEdits()
            return

        self.doSiteEditing(siteNumber, feature, self.polygon, oldCountry)


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

    def doSiteEditing(self, siteNumber, feature, polygon, country):
        siteArea = self.siteAreaHa(polygon)
        if country == 'AUT':
            kgCode, kgName = self.getKgNameAndCode(polygon)
        else:
            kgCode = None
            kgName = None

        editsSaved = self.openSiteDialogInEditMode(siteNumber, kgCode, kgName, siteArea)

        # open Dialog in editMode if cancel do not commit Changes but cancel Editing some rollback!


        if editsSaved:

            self.siteLayer.startEditing()
            feature.setGeometry(polygon)

            cpGeom = polygon.centroid()
            nearestCp = polygon.nearestPoint(cpGeom)
            cp = nearestCp.asPoint()
            feature.setAttribute('longitude', cp.x())
            feature.setAttribute('latitude', cp.y())

            # Aktions
            import getpass
            now = QDate.currentDate()
            feature.setAttribute('aktion', 'edited')
            feature.setAttribute('aktionsdatum', now.toString("yyyy-MM-dd"))
            feature.setAttribute('aktionsuser', getpass.getuser())

            if country == 'AUT':
                # get meridian and epsg Code
                lon = cp.x()
                if lon < 11.8333333333:
                    meridian = 28
                    epsgGK = 31254
                elif lon > 14.8333333333:
                    meridian = 34
                    epsgGK = 31256
                else:
                    meridian = 31
                    epsgGK = 31255
                feature.setAttribute('meridian', meridian)
                gk = QgsGeometry(nearestCp)
                destGK = QgsCoordinateReferenceSystem()
                destGK.createFromId(epsgGK, QgsCoordinateReferenceSystem.EpsgCrsId)
                ctGK = QgsCoordinateTransform(self.siteLayer.crs(), destGK)
                gk.transform(ctGK)
                feature.setAttribute('gkx', gk.asPoint().y())  # Hochwert
                feature.setAttribute('gky', gk.asPoint().x())  # Rechtswert

            self.siteLayer.updateFeature(feature)
            self.siteLayer.commitChanges()
            self.siteLayer.updateExtents()

            if self.canvas.isCachingEnabled():
                self.siteLayer.setCacheImage(None)
            else:
                self.canvas.refresh()
                # else:
                # self.siteLayer.rollBack()

        self.onCancelAnyEdits()

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


        self.doSiteEditing(siteNumber, feature, self.polygon, oldCountry)


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


    def openSiteDialog(self, siteNumber):
        siteDlgAdd = ApisSiteDialog(self.iface, self.dbm)
        siteDlgAdd.openInAddMode(siteNumber)
        siteDlgAdd.show()
        # Run the dialog event loop

        if siteDlgAdd.exec_():
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

        self.onCancelAnyEdits()
        # QMessageBox.warning(None, self.tr(u"Load Site"), self.tr(u"For Site: {0}".format(siteNumber)))


    def openSiteDialogInEditMode(self, siteNumber, kgCode, kgName, siteArea):
        siteDlgEdit = ApisSiteDialog(self.iface, self.dbm)
        siteDlgEdit.openInEditMode(siteNumber, kgCode, kgName, siteArea)
        siteDlgEdit.show()

        res = siteDlgEdit.exec_()
        # were edits saved (if not do not alter geometry)
        isGeometrySaved = siteDlgEdit.isGeometrySaved()
        #QMessageBox.warning(None, self.tr(u"Load Site"), self.tr(u"res: {0}".format(editStatus)))
        return isGeometrySaved

            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            #pass