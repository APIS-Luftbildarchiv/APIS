# -*- coding: utf-8 -*

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from qgis.core import *
from qgis.gui import *
from apis_db_manager import *
import sys, os, math, string
import pyexiv2 as exiv
import os.path

from apis_film_number_selection_dialog import *
from apis_monoplot_import_dialog import *

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
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)
        self.dbm = dbm
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self)
        self.hide()
        self.canvas = self.iface.mapCanvas()

        self.imageCenterPoint = None
        self.cpLayerId = None
        self.fpLayerId = None

        self.setPointMapTool = QgsMapToolEmitPoint(self.canvas) #SetPointMapTool(self.canvas)
        self.setPointMapTool.canvasClicked.connect(self.updatePoint)
        #self.setPointMapTool.canvasDoubleClicked.connect(self.handleDoubleClick)
        self.setPointMapTool.setButton(self.uiSetCenterPointBtn)
        self.uiSetCenterPointBtn.setCheckable(True)
        self.uiSetCenterPointBtn.toggled.connect(self.toggleSetCenterPoint)
        #self.uiSetCenterPointBtn.clicked.connect(self.activateSetCenterPoint)

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

        self.uiMonoplotImportBtn.clicked.connect(self.openMonoplotImportDialog)

        self.uiAddCenterPointBtn.clicked.connect(self.startAddingDetails)

        self.uiCancelCenterPointBtn.clicked.connect(self.onCancelAddCenterPoint)
        self.uiSaveCenterPointBtn.clicked.connect(self.onSaveAddCenterPoint)

        self.uiGenerateFootprintsBtn.clicked.connect(self.generateFootprints)

        self.uiAddProjectObliqueBtn.clicked.connect(self.addProjectOblique)
        self.uiAddProjectVerticalBtn.clicked.connect(self.addProjectVertical)

        self.uiRemoveProjectObliqueBtn.clicked.connect(self.removeProjectOblique)
        self.uiRemoveProjectVerticalBtn.clicked.connect(self.removeProjectVertical)

        self.resetCurrentFilmNumber()

    def openFilmSelectionDialog(self):
        """Run method that performs all the real work"""
        self.filmSelectionDlg.show()
        self.filmSelectionDlg.uiFilmNumberEdit.setFocus()
        if self.filmSelectionDlg.exec_():
            if not self.checkFilmNumber(self.filmSelectionDlg.filmNumber()):
                self.resetCurrentFilmNumber()
                #self.openFilmSelectionDialog()
            else:
                self.setCurrentFilmNumber(self.filmSelectionDlg.filmNumber())

    def openMonoplotImportDialog(self):
        """Run method that performs all the real work"""
        self.reloadCpLayer()
        self.reloadFpLayer()

        monoplotImportDlg = ApisMonoplotImportDialog(self, self.iface, self.dbm, self.cpLayer, self.fpLayer, self.currentFilmNumber)
        monoplotImportDlg.show()
        if monoplotImportDlg.exec_():
            self.cpLayer.updateExtents()
            self.fpLayer.updateExtents()

    def setCurrentFilmNumber(self, filmNumber):
        self.currentFilmNumber = filmNumber
        self.uiCurrentFilmNumberEdit.setText(self.currentFilmNumber)

        # Get Information & Stats: schräg/senk, bildanzahl, ...
        self.getFilmInfo()
        self.getMappingStats()
        self.updateMappingDetails()

        # Enable Controls
        self.setCurrentLayout(True,True,self.isOblique,False)
        if not self.imageCenterPoint:
            self.uiAddCenterPointBtn.setEnabled(False)

        if not self.uiSetCenterPointBtn.isChecked():
            self.uiSetCenterPointBtn.click()

        # Remove old Layer & Load New Layer
        self.removeCenterPointLayer()
        self.removeFootPrintLayer()
        self.loadCenterPointLayerForFilm()
        self.loadFootPrintLayerForFilm()

    def resetCurrentFilmNumber(self):
        self.uiCurrentFilmNumberEdit.clear()
        self.setCurrentLayout(True,False,False,False)

        self.canvas.unsetMapTool(self.setPointMapTool)
        self.vertexMarker.hide()
        self.vertexMarker2.hide()

        #TODO reset & remove layer!!!
        self.removeCenterPointLayer()
        self.removeFootPrintLayer()

    def enableItemsInLayout(self, layout, enable):
        for i in range(layout.count()):
            if layout.itemAt(i).widget():
                layout.itemAt(i).widget().setEnabled(enable)

    def checkFilmNumber(self, filmNumber):
        query = QSqlQuery(self.dbm.db)
        qryStr = "SELECT rowid FROM film WHERE filmnummer = '{0}'".format(filmNumber)
        # qryStr = "SELECT" \
        #          "  (SELECT COUNT(*)" \
        #          "       FROM film AS t2" \
        #          "       WHERE t2.rowid < t1.rowid" \
        #          "      ) + (" \
        #          "         SELECT COUNT(*)" \
        #          "         FROM film AS t3" \
        #          "        WHERE t3.rowid = t1.rowid AND t3.rowid < t1.rowid" \
        #          "      ) AS rowNum" \
        #          "   FROM film AS t1" \
        #          "   WHERE filmnummer = '{0}'" \
        #          "   ORDER BY t1.rowid ASC".format(filmNumber)
        query.exec_(qryStr)
        query.first()
        if query.value(0) != None:
            # Film exists
            return True
        else:
            # Film does not exist
            QMessageBox.warning(None, "Film Nummer", unicode("Der Film mit der Nummer {0} existiert nicht!".format(filmNumber)))
            return False

    def getFilmInfo(self):
        filmFields = ["filmnummer_hh_jjjj_mm", "filmnummer_nn", "filmnummer", "anzahl_bilder", "form1", "form2", "weise", "kammerkonstante", "datum_ersteintrag", "datum_aenderung", "projekt", "copyright"]
        self.currentFilmInfoDict = {}
        query = QSqlQuery(self.dbm.db)
        qryStr = "SELECT {0} FROM film WHERE filmnummer = '{1}'".format(", ".join(filmFields), self.currentFilmNumber)
        query.exec_(qryStr)
        query.first()
        if query.value(0) != None:
            for key in filmFields:
                value = query.value(query.record().indexOf(key))
                self.currentFilmInfoDict[key] = value

            if self.currentFilmInfoDict["weise"] == u"schräg":
                self.orientation = "schraeg"
                self.isOblique = True
            else:
                self.orientation = "senk"
                self.isOblique = False
        else:
            QMessageBox.warning(None, u"Film Nummer", u"Der Film mit der Nummer {0} existiert nicht!".format(self.currentFilmNumber))

    def getMappingStats(self):
        self.imageStatsDict = {}
        query = QSqlQuery(self.dbm.db)
        qryStr = "SELECT COUNT(*) AS anzahl_kartiert, MAX(bildnummer_nn) AS letzte_bildnummer, MIN(bildnummer_nn) AS erste_bildnummer FROM luftbild_{0}_cp WHERE filmnummer = '{1}'".format(self.orientation, self.currentFilmNumber)
        query.exec_(qryStr)
        query.first()
        statFields =["anzahl_kartiert", "letzte_bildnummer", "erste_bildnummer"]
        if query.value(0) != None:
            for key in statFields:
                idx = query.record().indexOf(key)
                if query.isNull(idx):
                    self.imageStatsDict[key] = 0
                else:
                    self.imageStatsDict[key] = query.value(idx)

            #QMessageBox.warning(None, u"Film Nummer", u"{0}, {1}, {2}".format(self.imageStatsDict["anzahl_kartiert"],self.imageStatsDict["letzte_bildnummer"],self.imageStatsDict["erste_bildnummer"]))
        else:
            self.imageStatsDict["anzahl_kartiert"] = 0
            self.imageStatsDict["letzte_bildnummer"] = 0
            self.imageStatsDict["erste_bildnummer"] = 0
            QMessageBox.warning(None, u"Film Nummer", u"Für den Film mit der Nummer {0} sind noch keine Bilder kartiert!".format(self.currentFilmNumber))


    def updateMappingDetails(self):
        if self.isOblique:
            self.uiMappingDetailsTBox.setCurrentIndex(0)
            self.uiImageNumberFromSpn.setValue(self.imageStatsDict["letzte_bildnummer"] + 1)
            self.uiImageNumberToSpn.setValue(self.imageStatsDict["letzte_bildnummer"] + 1)

            # Projekte
            # DropDown Reset
            # von Film in DropDown hinzufügen
            self.uiProjectObliqueCombo.clear()
            if self.currentFilmInfoDict["projekt"]:
                self.uiProjectObliqueCombo.addItems(string.split(self.currentFilmInfoDict["projekt"], ";"))
            else:
                #deactivate buttons
                pass

        else:
            self.uiMappingDetailsTBox.setCurrentIndex(1)
            self.uiImageNumberSpn.setValue(self.imageStatsDict["letzte_bildnummer"] + 1)
            self.uiProjectVerticalCombo.clear()
            if self.currentFilmInfoDict["projekt"]:
                self.uiProjectVerticalCombo.addItems(string.split(self.currentFilmInfoDict["projekt"], ";"))
            else:
                #deactivate buttons
                pass

    def toggleSetCenterPoint(self, isChecked):
        if isChecked:
            self.canvas.setMapTool(self.setPointMapTool)
            self.iface.messageBar().pushMessage(u"APIS Bild Kartierung", u"Positionieren Sie den Bildmittelpunkt mit der linken Maustaste und klicken Sie auf das Plus Symbol (oder verwenden Sie die reche Maustaste)", level=QgsMessageBar.INFO)
            self.vertexMarker.show()
            self.vertexMarker2.show()
        else:
            self.canvas.unsetMapTool(self.setPointMapTool)
            self.iface.actionTouch().trigger()
            self.vertexMarker.hide()
            self.vertexMarker2.hide()
            self.iface.messageBar().clearWidgets()

    def activateSetCenterPoint(self):
        if self.uiSetCenterPointBtn.isChecked():
            self.canvas.setMapTool(self.setPointMapTool)
            self.vertexMarker.show()
            self.vertexMarker2.show()
        else:
            self.canvas.unsetMapTool(self.setPointMapTool)
            self.vertexMarker.hide()
            self.vertexMarker2.hide()

    def updatePoint(self, point, button):
        self.reloadCpLayer()
        self.imageCenterPoint = self.canvas.mapSettings().mapToLayerCoordinates(self.cpLayer, QgsPoint(point))
        #self.gl.setLocation(self.imageCenterPoint)
        self.vertexMarker.setCenter(point)
        self.vertexMarker2.setCenter(point)
        self.uiXCoordinateLbl.setText("{}".format(point.x()))
        self.uiYCoordinateLbl.setText("{}".format(point.y()))
        self.uiAddCenterPointBtn.setEnabled(True)
        if not self.vertexMarker.isVisible():
            self.vertexMarker.show()
            self.vertexMarker2.show()
        if button == Qt.RightButton:
            self.startAddingDetails()

    def startAddingDetails(self):
        #TODO Delete Comments
        #QMessageBox.warning(None, u"Film Nummer", u"Bildmittelpunkt Kartieren")
        # Disable Layouts
        self.canvas.unsetMapTool(self.setPointMapTool)
        self.setCurrentLayout(False, False, False, True)
        #self.enableItemsInLayout(self.uiFilmSelectionHorizontalLayout, False)
        #self.enableItemsInLayout(self.uiMappingGridLayout, False)
        #if self.isOblique:
            #self.enableItemsInLayout(self.uiMonoplotHorizontalLayout, False)
        # Enable Layout
        #self.enableItemsInLayout(self.uiMappingDetailsGridLayout, True)
        # Disable Page

        self.uiMappingDetailsTBox.setItemEnabled(int(self.isOblique), False)

        #if self.isOblique:
        #    self.uiMappingDetailsTBox.setItemEnabled(1, False)
        #else:
        #    self.uiMappingDetailsTBox.setItemEnabled(0, False)

    def loadCenterPointLayerForFilm(self):
        uri = QgsDataSourceURI()
        uri.setDatabase(self.dbm.db.databaseName())
        uri.setDataSource('', 'luftbild_{0}_cp'.format(self.orientation), 'geometry')
        self.cpLayer = QgsVectorLayer(uri.uri(), u'Kartierung {0} Mittelpunkt'.format(self.currentFilmNumber), 'spatialite')
        self.cpLayer.setSubsetString(u'"filmnummer" = "{0}"'.format(self.currentFilmNumber))
        QgsMapLayerRegistry.instance().addMapLayer(self.cpLayer)
        self.cpLayerId = self.cpLayer.id()

    def loadFootPrintLayerForFilm(self):
        uri = QgsDataSourceURI()
        uri.setDatabase(self.dbm.db.databaseName())
        uri.setDataSource('', 'luftbild_{0}_fp'.format(self.orientation), 'geometry')
        self.fpLayer = QgsVectorLayer(uri.uri(), u'Kartierung {0} Footprint'.format(self.currentFilmNumber), 'spatialite')
        self.fpLayer.setSubsetString(u'"filmnummer" = "{0}"'.format(self.currentFilmNumber))
        QgsMapLayerRegistry.instance().addMapLayer(self.fpLayer)
        self.fpLayerId = self.fpLayer.id()

    def removeCenterPointLayer(self):
        if self.cpLayerId in QgsMapLayerRegistry.instance().mapLayers():
            QgsMapLayerRegistry.instance().removeMapLayer(self.cpLayer.id())

    def removeFootPrintLayer(self):
        if self.fpLayerId in QgsMapLayerRegistry.instance().mapLayers():
            QgsMapLayerRegistry.instance().removeMapLayer(self.fpLayer.id())

    def onCancelAddCenterPoint(self):
        self.setCurrentLayout(True, True, self.isOblique, False)
        self.getMappingStats()
        self.updateMappingDetails()
        self.canvas.setMapTool(self.setPointMapTool)

    def onSaveAddCenterPoint(self):
        #QMessageBox.warning(None, u"Film Nummer", u"{0},{1},{2}".format(self.imageCenterPoint.x(), self.imageCenterPoint.y(), type(self.imageCenterPoint)))
        #return
        self.reloadCpLayer()

        #Prepare Image Numbers
        if self.isOblique:
            fromImageNumber =  self.uiImageNumberFromSpn.value()
            toImageNumber = self.uiImageNumberToSpn.value()
            if fromImageNumber > toImageNumber:
                QMessageBox.warning(None, u"Bild Nummern", u"Die erste Bildnummer darf nicht größer als die zweite sein.")
                return
            else:
                imageNumbers = range(fromImageNumber, toImageNumber + 1)
        else:
           imageNumbers = [self.uiImageNumberSpn.value()]
        #filmImageNumbers = []
        #for imageNumber in imageNumbers:
            #filmImageNumbers.append('{0}.{1:03d}'.format(self.currentFilmNumber, imageNumber))

        #QMessageBox.warning(None, u"Bild Nummern", ",".join(imageNumbers))

        #for filmImageNumber in self.cpLayer.getValues("BILD"):
        #    QMessageBox.warning(None, u"Bild Nummern", "{0}".format(filmImageNumber))


        #Check if Image Number in Table
        for imageNumber in imageNumbers:
            if imageNumber in self.cpLayer.getValues("bildnummer_nn")[0]:
                QMessageBox.warning(None, u"Bild Nummern", u"Ein Bild mit der Nummer {0} wurde bereits kartiert".format(imageNumber))
                return

        caps = self.cpLayer.dataProvider().capabilities()
        if caps & QgsVectorDataProvider.AddFeatures:
            features = []

            feat = QgsFeature(self.cpLayer.pendingFields())
            feat.setGeometry(QgsGeometry.fromPoint(self.imageCenterPoint))

            # From Film Table
            #filmFields = ["form1", "form2", "weise", "kammerkonstante"]
            feat.setAttribute('filmnummer_hh_jjjj_mm', self.currentFilmInfoDict["filmnummer_hh_jjjj_mm"])
            feat.setAttribute('filmnummer_nn', self.currentFilmInfoDict["filmnummer_nn"])
            feat.setAttribute('filmnummer', self.currentFilmNumber)

            #Date TODAY
            now = QDate.currentDate()
            feat.setAttribute('datum_ersteintrag', now.toString("yyyy-MM-dd"))
            feat.setAttribute('datum_aenderung', now.toString("yyyy-MM-dd"))


            # Iterate over Project Selection List und String mit ; trennung generieren
            feat.setAttribute('copyright', self.currentFilmInfoDict["copyright"])

            # By Default Fix Value
            feat.setAttribute('etikett', 0)

            # Get Projects from Projekte Liste
            items = []
            # From Input (Radius, Höhe, Schlüsslewort, Beschreibung)
            if self.isOblique:
                feat.setAttribute('radius', self.uiImageDiameterSpn.value()/2)
                feat.setAttribute('keyword', self.uiImageKeywordEdit.text())
                feat.setAttribute('description', self.uiImageDescriptionEdit.text())
                h = self.uiFlightHeightObliqueSpn.value()
                for j in xrange(self.uiProjectObliqueList.count()):
                    items.append(self.uiProjectObliqueList.item(j))
            else:
                h = self.uiFlightHeightVerticalSpn.value()
                feat.setAttribute('fokus', self.currentFilmInfoDict["kammerkonstante"])
                if not self.currentFilmInfoDict["kammerkonstante"] or self.currentFilmInfoDict["kammerkonstante"] < 1:
                    feat.setAttribute('massstab', 0)
                else:
                    feat.setAttribute('massstab', h/self.currentFilmInfoDict["kammerkonstante"]*1000)
                for j in xrange(self.uiProjectVerticalList.count()):
                    items.append(self.uiProjectVerticalList.item(j))


            feat.setAttribute('projekt',  ";".join([i.text() for i in items]))
            feat.setAttribute('hoehe', h)

            # Calculated/Derived
            feat.setAttribute('longitude', self.imageCenterPoint.x())
            feat.setAttribute('latitude', self.imageCenterPoint.y())

            countryCode = self.getCountryCode()
            feat.setAttribute('land', countryCode)

            if countryCode == 'AUT':
                #get meridian and epsg Code
                lon = self.imageCenterPoint.x()
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
                gk = QgsGeometry().fromPoint(self.imageCenterPoint)
                destGK = QgsCoordinateReferenceSystem()
                destGK.createFromId(epsgGK, QgsCoordinateReferenceSystem.EpsgCrsId)
                ctGK = QgsCoordinateTransform(self.cpLayer.crs(), destGK)
                gk.transform(ctGK)
                feat.setAttribute('gkx', gk.asPoint().y()) # Hochwert
                feat.setAttribute('gky', gk.asPoint().x()) # Rechtswert


            for imageNumber in imageNumbers:
                f = QgsFeature(feat)
                f.setAttribute('bildnummer_nn', imageNumber)
                bn = '{0}.{1:03d}'.format(self.currentFilmNumber, imageNumber)
                f.setAttribute('bildnummer', bn)

                if self.isOblique:
                    exif = self.getExifForImage(bn)
                    #exif = [None, None, None, None, None, None]
                    if exif[0]:
                        f.setAttribute('hoehe', exif[0])
                    f.setAttribute('gps_longitude', exif[1])
                    f.setAttribute('gps_latitude', exif[2])

                    if exif[1] and exif[2]:
                        capturePoint = QgsPoint(exif[1], exif[2])
                        kappa = capturePoint.azimuth(self.imageCenterPoint)
                        f.setAttribute('kappa', kappa)

                    f.setAttribute('belichtungszeit', exif[3])
                    f.setAttribute('fokus', exif[4]) # FocalLength
                    if exif[4] and exif[5]:
                       f.setAttribute('blende', exif[4]/exif[5] ) #effecitve aperture (diameter of entrance pupil) = focalLength / fNumber
                    else:
                        f.setAttribute('blende', None)

                features.append(f)

            (res, outFeats) = self.cpLayer.dataProvider().addFeatures(features)
            self.cpLayer.updateExtents()

            if res and self.isOblique:
                self.generateFootprintsForFilmOblique()

            #QMessageBox.warning(None, u"Film Nummer", u"{0},{1}".format(res, outFeats))
        else:
            QMessageBox.warning(None, u"Layer Capabilities!")

        if self.canvas.isCachingEnabled():
            self.cpLayer.setCacheImage(None)
        else:
            self.canvas.refresh()

        self.onCancelAddCenterPoint()

    def getCountryCode(self):
        query = QSqlQuery(self.dbm.db)
        #qryStr = "SELECT code FROM osm_boundaries WHERE within(MakePoint({0}, {1}, 4312), geometry)".format(self.imageCenterPoint.x(), self.imageCenterPoint.y())
        qryStr = "SELECT code FROM osm_boundaries WHERE intersects(Transform(MakePoint({0}, {1}, 4312), 4326), geometry)  AND ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'osm_boundaries' AND search_frame = Transform(MakePoint({0}, {1}, 4312), 4326))".format(self.imageCenterPoint.x(), self.imageCenterPoint.y())
        query.exec_(qryStr)
        query.first()
        if query.value(0) is None:
            return 'INT'
        else:
            return query.value(0)

    def getExifForImage(self, imageNumber):
        exif = [None, None, None, None, None, None]
        dirName = self.settings.value("APIS/image_dir")
        imageName = self.imageToImageLegacy(imageNumber).replace('.','_') + '.jpg'
        image = os.path.normpath(dirName+'\\'+self.filmToFilmLegacy(self.currentFilmNumber)+'\\'+imageName)
        #QMessageBox.warning(None, u"exif", image)

        if os.path.isfile(image):
            md = exiv.ImageMetadata(image)
            md.read()

            if "Exif.GPSInfo.GPSAltitude" in md.exif_keys:
                exif[0] = float(md["Exif.GPSInfo.GPSAltitude"].value)

            if "Exif.GPSInfo.GPSLongitude" in md.exif_keys:
                lon = md["Exif.GPSInfo.GPSLongitude"].value
                exif[1] = float(lon[0])+((float(lon[1])+(float(lon[2])/60))/60)

            if "Exif.GPSInfo.GPSLatitude" in md.exif_keys:
                lat = md["Exif.GPSInfo.GPSLatitude"].value
                exif[2] = float(lat[0])+((float(lat[1])+(float(lat[2])/60))/60)

            if "Exif.Photo.ExposureTime" in md.exif_keys:
                exif[3] = float(md["Exif.Photo.ExposureTime"].value)

            if "Exif.Photo.FocalLength" in md.exif_keys:
                exif[4] = float(md["Exif.Photo.FocalLength"].value)

            if "Exif.Photo.FNumber" in md.exif_keys:
                exif[5] = md["Exif.Photo.FNumber"].value

        return exif

    def filmToFilmLegacy(self, film):
        mil = ""
        if film[2:4] == "19":
            mil = "01"
        elif film[2:4] == "20":
            mil = "02"
        return mil + film[4:]

    def imageToImageLegacy(self, image):
        mil = ""
        if image[2:4] == "19":
            mil = "01"
        elif image[2:4] == "20":
            mil = "02"
        return mil + image[4:]

    def reloadCpLayer(self):
         if self.cpLayerId not in QgsMapLayerRegistry.instance().mapLayers():
            self.loadCenterPointLayerForFilm()

    def reloadFpLayer(self):
         if self.fpLayerId not in QgsMapLayerRegistry.instance().mapLayers():
            self.loadFootPrintLayerForFilm()

    def generateFootprints(self):
        if self.isOblique:
            self.generateFootprintsForFilmOblique()
        else:
            self.generateFootprintsForFilmVertical()

    def generateFootprintsForFilmVertical(self):
        self.reloadCpLayer()
        self.reloadFpLayer()
        #uri = QgsDataSourceURI()
        #uri.setDatabase(self.dbm.db.databaseName())
        #uri.setDataSource('', 'luftbild_{0}_fp'.format(self.orientation), 'geometry')
        #self.fpLayer = QgsVectorLayer(uri.uri(), u'Kartierung {0} Footprint'.format(self.currentFilmNumber), 'spatialite')
        #self.fpLayer.setSubsetString(u'"filmnummer" = "{0}"'.format(self.currentFilmNumber))
        #QgsMapLayerRegistry.instance().addMapLayer(self.fpLayer)

        # Error wenn nur ein punkt vorhanden
        if self.cpLayer.featureCount() > 1:
            caps = self.fpLayer.dataProvider().capabilities()
            if caps & QgsVectorDataProvider.AddFeatures:
                #Get FORM1 from FilmInfoDict
                f1 = self.currentFilmInfoDict["form1"]

                iter = self.cpLayer.getFeatures()
                iterNext = self.cpLayer.getFeatures()
                existingFootpints = self.fpLayer.getValues("bildnummer")[0]
                ft = QgsFeature()
                ftNext = QgsFeature()
                iterNext.nextFeature(ftNext)
                fpFeats = []
                #iterate over points from CP Layer > LON, LAT
                i = 0

                while iter.nextFeature(ft):
                    i += 1
                    iterNext.nextFeature(ftNext)
                    p = QgsPoint(ft.geometry().asPoint())
                    if ft['bildnummer'] in existingFootpints:
                        #pPrev = QgsPoint(p)
                        pPrevGeom = QgsGeometry(ft.geometry())
                        #QMessageBox.warning(None, u"Bild Nummern", u"Footprint für das Bild mit der Nummer {0} wurde bereits erstellt.".format(ft['BILD']))
                        continue
                    if i == 1:
                        #pPrev = QgsPoint(ftNext.geometry().asPoint())
                        pPrevGeom = QgsGeometry(ftNext.geometry())
                    #if iterNext.isClosed():
                    #    #use pPrev as pNext
                    #    pNext = QgsPoint(pPrev)
                    #else:
                    #    pNext = QgsPoint(ftNext.geometry().asPoint())

                    #kappa = p.azimuth(pPrev)

                    #kappa = p.azimuth(pNext)


                    #d = math.sqrt(2*((f1/2 * ft['MASS']/1000)**2))
                    d = f1/2 * ft['massstab']/1000
                    #QMessageBox.warning(None, u"Bild Nummern", "{0}".format(d))

                    calcCrs = QgsCoordinateReferenceSystem()
                    calcCrs.createFromProj4(self.Proj4Utm(p))
                    ctF = QgsCoordinateTransform(self.cpLayer.crs(), calcCrs)

                    cpMetric = QgsGeometry(ft.geometry())
                    cpMetric.transform(ctF)
                    pPrevGeom.transform(ctF)
                    pMetric = QgsPoint(cpMetric.asPoint())
                    pPrevMetric = QgsPoint(pPrevGeom.asPoint())
                    kappaMetric = pMetric.azimuth(pPrevMetric)
                    #pPrev = QgsPoint(p)
                    pPrevGeom = QgsGeometry(ft.geometry())
                    l = pMetric.x() - d
                    b = pMetric.y() - d
                    r = pMetric.x() + d
                    t = pMetric.y() + d

                    #R = 6371
                    #D = (d/1000)
                    #cpLat = math.radians(p.y())
                    #cpLon = math.radians(p.x())
                    #urLat = math.asin( math.sin(cpLat)*math.cos(D/R) + math.cos(cpLat)*math.sin(D/R)*math.cos(urBrng) )
                    #urLon = cpLon + math.atan2(math.sin(urBrng)*math.sin(D/R)*math.cos(cpLat), math.cos(D/R)-math.sin(cpLat)*math.sin(urLat))

                    #top = math.asin( math.sin(cpLat)*math.cos(D/R) + math.cos(cpLat)*math.sin(D/R) )
                    #bottom = math.asin( math.sin(cpLat)*math.cos(D/R) + math.cos(cpLat)*math.sin(D/R)*-1 )

                    #lat = math.asin( math.sin(cpLat)*math.cos(D/R) )
                    #right = cpLon + math.atan2(math.sin(D/R)*math.cos(cpLat), math.cos(D/R)-math.sin(cpLat)*math.sin(lat))
                    #left = cpLon + math.atan2(-1*math.sin(D/R)*math.cos(cpLat), math.cos(D/R)-math.sin(cpLat)*math.sin(lat))

                    #QMessageBox.warning(None, u"Bild Nummern", "{0}, {1}, {2}, {3}".format(math.degrees(top), math.degrees(bottom), math.degrees(left), math.degrees(right)))

                    #rect = QgsRectangle(math.degrees(left), math.degrees(bottom), math.degrees(right), math.degrees(top))
                    #l = math.degrees(left)
                    #b = math.degrees(bottom)
                    #r = math.degrees(right)
                    #t = math.degrees(top)
                    p1 = QgsGeometry.fromPoint(QgsPoint(l, b))
                    p2 = QgsGeometry.fromPoint(QgsPoint(r, b))
                    p3 = QgsGeometry.fromPoint(QgsPoint(r, t))
                    p4 = QgsGeometry.fromPoint(QgsPoint(l, t))
                    #p1.rotate(kappa+90, p)
                    #p2.rotate(kappa+90, p)
                    #p3.rotate(kappa+90, p)
                    #p4.rotate(kappa+90, p)
                    pol = [[p1.asPoint(), p2.asPoint(), p3.asPoint(), p4.asPoint()]]
                    geom = QgsGeometry.fromPolygon(pol)
                    geom.rotate(kappaMetric, pMetric)
                    #Transform to DestinationCRS
                    ctB = QgsCoordinateTransform(calcCrs, self.fpLayer.crs())
                    geom.transform(ctB)

                    feat = QgsFeature(self.fpLayer.pendingFields())
                    feat.setGeometry(geom)
                    feat.setAttribute('filmnummer', self.currentFilmNumber)
                    feat.setAttribute('bildnummer', ft['bildnummer'])
                    #TODO Shape_Length, Shape_Area
                    fpFeats.append(feat)

                    #r = QgsRubberBand(self.canvas, True)
                    #r.setToGeometry(geom, None)

                    # QMessageBox.warning(None, u"Bild Nummern", "{0}, {1}".format(math.degrees(urLat), math.degrees(urLon)))
                    #m = QgsVertexMarker(self.canvas)
                    #m.setCenter(QgsPoint(math.degrees(urLon), math.degrees(urLat)))


                    #TODO update Kappa in cpLayer
                    #if not self.cpLayer.isEditable():
                    #    self.cpLayer.startEditing()
                    #r = self.cpLayer.changeAttributeValue(ft.id(), self.cpLayer.fieldNameIndex("kappa"), kappaMetric)
                    #QMessageBox.warning(None, "Titel", u"{0}, {1}, {2}, {3}".format(r, ft.id(), self.cpLayer.fieldNameIndex("kappa"), kappaMetric))

                #self.cpLayer.commitChanges()
                (res, outFeats) = self.fpLayer.dataProvider().addFeatures(fpFeats)


                self.fpLayer.updateExtents()
                if self.canvas.isCachingEnabled():
                    self.fpLayer.setCacheImage(None)
                else:
                    self.canvas.refresh()
            else:
                #Caps
                QMessageBox.warning(None, u"Layer Capabilities!",u"Layer Capabilities!" )
        else:
            #small feature count
            QMessageBox.warning(None, u"Footprints", u"Zum Berechnen der senkrecht Footprint müssen mindestens zwei Bilder kartiert werden!")


    def generateFootprintsForFilmOblique(self):
        self.reloadCpLayer()
        self.reloadFpLayer()

        caps = self.fpLayer.dataProvider().capabilities()
        if caps & QgsVectorDataProvider.AddFeatures:
            iter = self.cpLayer.getFeatures()
            existingFootpints = self.fpLayer.getValues("bildnummer")[0]
            cpFt = QgsFeature()
            fpFts = []
            #iterate over points from CP Layer > LON, LAT
            while iter.nextFeature(cpFt):
                if cpFt['bildnummer'] in existingFootpints:
                    #QMessageBox.warning(None, u"Bild Nummern", u"Footprint für das Bild mit der Nummer {0} wurde bereits erstellt.".format(ft['BILD']))
                    continue
                cp = cpFt.geometry()
                cpMetric = QgsGeometry(cp)
                destCrs = QgsCoordinateReferenceSystem()
                destCrs.createFromProj4(self.Proj4Utm(cp.asPoint()))
                coordTransformF = QgsCoordinateTransform(self.cpLayer.crs(), destCrs)
                coordTransformB = QgsCoordinateTransform(destCrs, self.cpLayer.crs())
                cpMetric.transform(coordTransformF)
                if cpFt['radius'] == '':
                    r = 175
                else:
                    r = int(cpFt['radius'])
                fpMetric = QgsGeometry(cpMetric.buffer(r,18))
                fp = QgsGeometry(fpMetric)
                fp.transform(coordTransformB)

                fpFt = QgsFeature(self.fpLayer.pendingFields())
                fpFt.setGeometry(fp)
                fpFt.setAttribute("bildnummer", cpFt["bildnummer"])
                fpFt.setAttribute("filmnummer", cpFt["filmnummer"])
                fpFts.append(fpFt)
            (res, outFeats) = self.fpLayer.dataProvider().addFeatures(fpFts)
            self.fpLayer.updateExtents()
        else:
            QMessageBox.warning(None, u"Layer Capabilities!")


    def Proj4Utm(self,  p):
        x = p.x()
        y = p.y()
        z = math.floor((x + 180)/6) + 1

        if y >= 56.0 and y < 64.0 and x >= 3.0 and x < 12.0:
            ZoneNumber = 32

        #Special zones for Svalbard
        if y >= 72.0 and y < 84.0 :
            if y >= 0.0 and y <  9.0:
                z = 31
            elif y >= 9.0 and y < 21.0:
                z = 33
            elif y >= 21.0 and y < 33.0:
                z = 35
            elif y >= 33.0 and y < 42.0:
                z = 37

        return "+proj=utm +zone={0} +datum=WGS84 +units=m +no_defs".format(int(z))

    def setCurrentLayout(self, film=True, mapping=False, monoplot=False, details=False):
        self.enableItemsInLayout(self.uiFilmSelectionHorizontalLayout, film)
        self.enableItemsInLayout(self.uiMappingGridLayout, mapping)
        self.enableItemsInLayout(self.uiMonoplotHorizontalLayout, monoplot)
        self.enableItemsInLayout(self.uiMappingDetailsGridLayout, details)

    def addProjectOblique(self):
        self.addProject(self.uiProjectObliqueList, self.uiProjectObliqueCombo.currentText())

    def addProjectVertical(self):
        self.addProject(self.uiProjectVerticalList, self.uiProjectVerticalCombo.currentText())

    def removeProjectOblique(self):
        self.removeProject(self.uiProjectObliqueList)

    def removeProjectVertical(self):
        self.removeProject(self.uiProjectVerticalList)

    def addProject(self, editor, value):
        notInList = True
        for row in range(editor.count()):
            if value == editor.item(row).data(0):
                notInList = False
                break
        if notInList:
            editor.addItem(value)
            editor.sortItems()

    def removeProject(self, editor):
        editor.takeItem(editor.currentRow())


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