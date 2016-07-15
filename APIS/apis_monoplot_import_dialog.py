__author__ = 'Johannes'
# -*- coding: utf-8 -*

import os, sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from PyQt4.QtXml import *
from qgis.core import *
from qgis.gui import *
import pyexiv2 as exiv
from apis_utils import *

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

# --------------------------------------------------------
# Film - Eingabe, Pflege
# --------------------------------------------------------
from apis_monoplot_import_form import *

class ApisMonoplotImportDialog(QDialog, Ui_apisMonoplotImportDialog):
    def __init__(self, parent, iface, dbm, targetLayerCP=None, targetLayerFP=None, filmId=None):
        QDialog.__init__(self)
        self.setupUi(self)
        self.iface = iface
        self.dbm = dbm
        self.filmId = filmId
        self.parent = parent
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)

        self.targetLayerCP = targetLayerCP
        self.targetLayerFP = targetLayerFP

        self.sourceLayerCP = None
        self.soruceLayerFP = None

        self.uiCenterPointMLCombo.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.uiFootPrintMLCombo.setFilters(QgsMapLayerProxyModel.PolygonLayer)

        self.uiImportBtn.clicked.connect(self.run)

    def areSourceLayerMonoplot(self):
        if self.sourceLayerCP.featureCount() != self.sourceLayerFP.featureCount() and self.sourceLayerCP.featureCount() != 0:
            #QMessageBox.warning(None, "MonoplotImport", u"{0}, {1}".format(self.sourceLayerCP.featureCount()))
            return False
        provCP = self.sourceLayerCP.dataProvider()
        fieldNamesCP = [field.name() for field in provCP.fields()]
        if set(fieldNamesCP) != set(["Image", "ERROR"]):
            return False

        provFP = self.sourceLayerFP.dataProvider()
        fieldNamesFP = [field.name() for field in provFP.fields()]
        if set(fieldNamesFP) != set(["Image", "ERROR"]):
            return False

        imageNumberCPSet = set([feature["Image"] for feature in self.sourceLayerCP.getFeatures()])
        imageNumberFPSet = set([feature["Image"] for feature in self.sourceLayerFP.getFeatures()])

        if imageNumberCPSet != imageNumberFPSet:
            return False

        #filmNumberCP = set([feature["Image"].split('_')[0] for feature in self.sourceLayerCP.getFeatures()])
        # TODO RM if len(filmNumberCP) != 1 or list(filmNumberCP)[0] != IdToIdLegacy(self.filmId):    #TODO: DELETE LEGACY MODE
        # if len(filmNumberCP) != 1 or list(filmNumberCP)[0] != self.filmId:
        #    return False

        #filmNumberFP = set([feature["Image"].split('_')[0]for feature in self.sourceLayerFP.getFeatures()])
        #TODO RM if len(filmNumberFP) != 1 or list(filmNumberFP)[0] != IdToIdLegacy(self.filmId):         # TODO: DELETE LEGACY MODE
        # if len(filmNumberFP) != 1 or list(filmNumberFP)[0] != self.filmId:
        #    return False

        return True

    def getCountryCode(self, p):
        query = QSqlQuery(self.dbm.db)
        #qryStr = "SELECT code FROM osm_boundaries WHERE within(MakePoint({0}, {1}, 4312), Geometry)".format(p.x(),p.y())
        qryStr = "SELECT code FROM osm_boundaries WHERE intersects(Transform(MakePoint({0}, {1}, 4312), 4326), geometry)  AND ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'osm_boundaries' AND search_frame = Transform(MakePoint({0}, {1}, 4312), 4326))".format(p.x(),p.y())

        query.exec_(qryStr)
        query.first()
        if query.value(0) is None:
            return 'INT'
        else:
            return query.value(0)

    def getExifForImage(self, imageNumber):
        exif = [None, None, None, None, None, None]
        dirName = self.settings.value("APIS/image_dir")
        #TODO RM imageName = IdToIdLegacy(imageNumber).replace('.','_') + '.jpg'       # TODO: RM LEGACY
        imageName = imageNumber.replace('.', '_') + '.jpg'
        #TODO RM image = os.path.normpath(dirName+'\\'+IdToIdLegacy(self.filmId)+'\\'+imageName)      # TODO: RM LEGACY
        image = os.path.normpath(dirName+'\\'+self.filmId+'\\'+imageName)
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


    def run(self):

        self.sourceLayerCP = self.uiCenterPointMLCombo.currentLayer()
        self.sourceLayerFP = self.uiFootPrintMLCombo.currentLayer()

        if self.areSourceLayerMonoplot():
            #iterate over sourceLayerCP
            iterCP = self.sourceLayerCP.getFeatures()
            iterFP = self.sourceLayerFP.getFeatures()
            existingFeaturesCP = self.targetLayerCP.getValues("bildnummer_nn")[0]
            existingFeatureFP = self.targetLayerFP.getValues("bildnummer")[0]
            capsCP = self.targetLayerCP.dataProvider().capabilities()
            capsFP = self.targetLayerFP.dataProvider().capabilities()
            if capsCP & QgsVectorDataProvider.AddFeatures and capsFP & QgsVectorDataProvider.AddFeatures:
                featuresCP = []
                featuresFP = []
                #for sourceFeat in iterCP:
                sourceFeatCP = QgsFeature()
                sourceFeatFP = QgsFeature()
                i = 0
                while iterCP.nextFeature(sourceFeatCP):
                    i += 1
                    iterFP.nextFeature(sourceFeatFP)
                    #imageNumber = int(sourceFeatCP["Image"].split('_')[1].split('.')[0])
                    imageNumber = i
                    bn = '{0}.{1:03d}'.format(self.filmId, imageNumber)
                    if imageNumber in existingFeaturesCP or imageNumber in existingFeatureFP:
                        #TODO: Wenn kartiert Abfragen ob überspringen oder überschreiben (diesmal oder alle)!
                        #TODO Löschen mit sql vs. layer
                        QMessageBox.warning(None, u"Bild Nummern", u"Ein Bild mit der Nummer {0} wurde bereits kartiert".format(imageNumber))

                        # request = QgsFeatureRequest().setFilterExpression( u'"bildnummer" = \'{0}\''.format(bn) )
                        # iterTargetCP = self.targetLayerCP.getFeatures(request)
                        # for f in iterTargetCP:
                        #     self.targetLayerCP.deleteFeature(f.id())
                        #     QMessageBox.warning(None, u"Bild Nummern", u"{0}".format(f.id()))
                        #
                        # self.targetLayerCP.commitChanges()
                        continue

                    targetFeatCP = QgsFeature(self.targetLayerCP.pendingFields())
                    #PpointGeometry
                    ct = QgsCoordinateTransform(self.sourceLayerCP.crs(), self.targetLayerCP.crs())
                    targetGeometryCP = QgsGeometry(sourceFeatCP.geometry())
                    targetGeometryCP.transform(ct)
                    targetFeatCP.setGeometry(targetGeometryCP)

                    # From Film Table
                    #filmFields = ["form1", "form2", "weise", "kammerkonstante"]
                    targetFeatCP.setAttribute('filmnummer_hh_jjjj_mm', self.parent.currentFilmInfoDict["filmnummer_hh_jjjj_mm"])
                    targetFeatCP.setAttribute('filmnummer_nn', self.parent.currentFilmInfoDict["filmnummer_nn"])
                    targetFeatCP.setAttribute('filmnummer', self.parent.currentFilmNumber)

                    targetFeatCP.setAttribute('bildnummer_nn', imageNumber)
                    #bn = '{0}.{1:03d}'.format(self.filmId, imageNumber)
                    targetFeatCP.setAttribute('bildnummer', bn)

                    #Date TODAY
                    now = QDate.currentDate()
                    targetFeatCP.setAttribute('datum_ersteintrag', now.toString("yyyy-MM-dd"))
                    targetFeatCP.setAttribute('datum_aenderung', now.toString("yyyy-MM-dd"))

                    targetFeatCP.setAttribute('copyright', self.parent.currentFilmInfoDict["copyright"])
                    # By Default Fix Value
                    targetFeatCP.setAttribute('etikett', 0)

                    targetFeatCP.setAttribute('radius', 175)
                    targetFeatCP.setAttribute('keyword', "")
                    targetFeatCP.setAttribute('description', "")

                    targetFeatCP.setAttribute('hoehe', 0)

                    # Calculated/Derived
                    cp = targetFeatCP.geometry().asPoint()
                    targetFeatCP.setAttribute('longitude', cp.x())
                    targetFeatCP.setAttribute('latitude', cp.y())

                    countryCode = self.getCountryCode(cp)
                    targetFeatCP.setAttribute('land', countryCode)

                    if countryCode == 'AUT':
                        #get meridian and epsg Code
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
                        targetFeatCP.setAttribute('meridian', meridian)
                        gk = QgsGeometry(targetFeatCP.geometry())
                        destGK = QgsCoordinateReferenceSystem()
                        destGK.createFromId(epsgGK, QgsCoordinateReferenceSystem.EpsgCrsId)
                        ctGK = QgsCoordinateTransform(self.targetLayerCP.crs(), destGK)
                        gk.transform(ctGK)
                        targetFeatCP.setAttribute('gkx', gk.asPoint().y()) # Hochwert
                        targetFeatCP.setAttribute('gky', gk.asPoint().x()) # Rechtswert

                    exif = self.getExifForImage(bn)
                    #exif = [None, None, None, None, None, None]
                    if exif[0]:
                        targetFeatCP.setAttribute('hoehe', exif[0])
                    targetFeatCP.setAttribute('gps_longitude', exif[1])
                    targetFeatCP.setAttribute('gps_latitude', exif[2])

                    if exif[1] and exif[2]:
                        capturePoint = QgsPoint(exif[1], exif[2])
                        kappa = capturePoint.azimuth(cp)
                        targetFeatCP.setAttribute('kappa', kappa)

                    targetFeatCP.setAttribute('belichtungszeit', exif[3])
                    targetFeatCP.setAttribute('fokus', exif[4]) # FocalLength
                    if exif[4] and exif[5]:
                       targetFeatCP.setAttribute('blende', exif[4]/exif[5] ) #effecitve aperture (diameter of entrance pupil) = focalLength / fNumber
                    else:
                        targetFeatCP.setAttribute('blende', None)

                    featuresCP.append(targetFeatCP)

                    targetFeatFP = QgsFeature(self.targetLayerFP.pendingFields())

                    ct = QgsCoordinateTransform(self.sourceLayerFP.crs(), self.targetLayerFP.crs())
                    targetGeometryFP = QgsGeometry(sourceFeatFP.geometry())
                    targetGeometryFP.transform(ct)
                    targetFeatFP.setGeometry(targetGeometryFP)

                    targetFeatFP.setAttribute('filmnummer', self.parent.currentFilmNumber)
                    targetFeatFP.setAttribute('bildnummer', bn)

                    featuresFP.append(targetFeatFP)

                (res, outFeats) = self.targetLayerCP.dataProvider().addFeatures(featuresCP)
                self.targetLayerCP.updateExtents()

                (res, outFeats) = self.targetLayerFP.dataProvider().addFeatures(featuresFP)
                self.targetLayerFP.updateExtents()

            else:
                QMessageBox.warning(None, u"Layer Capabilities!")


               #.warning(None, "MonoplotImport", u"{0}".format(id))
        else:
            QMessageBox.warning(None, "MonoplotImport", u"Die Ausgewählten Layer sind für den MONOPLOT Import ungeeignet!")
