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
    def __init__(self, parent, iface, dbm, sourceLayerCP, sourceLayerFP, targetLayerCP, targetLayerFP, filmId):
        QDialog.__init__(self)
        self.setupUi(self)
        self.iface = iface
        self.dbm = dbm
        self.filmId = filmId
        self.parent = parent
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)

        self.targetLayerCP = targetLayerCP
        self.targetLayerFP = targetLayerFP

        self.sourceLayerCP = sourceLayerCP
        self.sourceLayerFP = sourceLayerFP
        #self.sourceLayerCP = self.uiCenterPointMLCombo.currentLayer()
        #self.sourceLayerFP = self.uiFootPrintMLCombo.currentLayer()
        self.uiReportPTxt.setCenterOnScroll(True)
        self.writeMsg(u"Monoplot/INS2CAM import für Film: {0}".format(self.filmId))
        self.uiImportBtn.clicked.connect(self.run)

    def areSourceLayerMonoplot(self):
        if self.sourceLayerCP.featureCount() == 0 or self.sourceLayerFP.featureCount() == 0:
            return False, u"Zumindest einer der Layer aht keine Features (Centerpoint: {0}, Footprint: {1})".format(self.sourceLayerCP.featureCount(), self.sourceLayerFP.featureCount())
        if self.sourceLayerCP.featureCount() != self.sourceLayerFP.featureCount():
            return False, u"Die Feature Anzahl stimmt nicht überein (Centerpoint: {0}, Footprint: {1})".format(self.sourceLayerCP.featureCount(), self.sourceLayerFP.featureCount())

        provCP = self.sourceLayerCP.dataProvider()
        fieldNamesCP = set([field.name() for field in provCP.fields()])
        if "Image" not in fieldNamesCP:
            return False, u"Der Centerpoint Layer hat kein Attribut 'Image'."
        if "ERROR" not in fieldNamesCP:
            return False, u"Der Centerpoint Layer hat kein Attribut 'ERROR'."

        provFP = self.sourceLayerFP.dataProvider()
        fieldNamesFP = set([field.name() for field in provFP.fields()])
        if "Image" not in fieldNamesFP:
            return False, u"Der Footprint Layer hat kein Attribut 'Image'."
        if "ERROR" not in fieldNamesFP:
            return False, u"Der Footprint Layer hat kein Attribut 'ERROR'."

        numOfImagesCPSet = set([feature["Image"] for feature in self.sourceLayerCP.getFeatures()])
        numOfImagesFPSet = set([feature["Image"] for feature in self.sourceLayerFP.getFeatures()])

        if numOfImagesCPSet != numOfImagesFPSet:
            return False, u"Die Werte des Attributes 'Image' stimmen zwischen den Layern nicht überein."

        filmNumberCP = set([feature["Image"].split('_')[0] for feature in self.sourceLayerCP.getFeatures()])
        if len(filmNumberCP) != 1:
            return False, u"Im Centerpoint Layer gibt es Bilder von mehr als einem Film ({0}).".format(u', '.join(list(filmNumberCP)))

        filmNumber = list(filmNumberCP)[0]
        if len(filmNumber) == 8:
            #old Id
            mil =u""
            if filmNumber[:2] == u"01":
                mil = u"19"
            elif filmNumber[:2] == u"02":
                mil = u"20"
            else:
                return False, u"Die Filmnummer im Centerpoint Layer entspricht weder dem alten (8-stellig) nch dem neuen (10-stellig) Filmnummernschema ({0}).".format()
            filmNumber = u"01{0}{1}".format(mil,filmNumber[2:])
        elif len(filmNumber) == 10:
            #new Id
            pass
        else:
            return False, u"Die Filmnummer im Centerpoint Layer entspricht weder dem alten (8-stellig) nch dem neuen (10-stellig) Filmnummernschema ({0}).".format()

        if filmNumber != self.filmId:
            return False, u"Im Centerpoint Layer sind Bilder eines anderen Films ({0}).".format(list(filmNumberCP)[0])

        filmNumberFP = set([feature["Image"].split('_')[0]for feature in self.sourceLayerFP.getFeatures()])
        if len(filmNumberFP) != 1:
            return False, u"Im Footprint Layer gibt es Bilder von mehr als einem Film ({0}).".format(u', '.join(list(filmNumberFP)))

        filmNumber = list(filmNumberFP)[0]
        if len(filmNumber) == 8:
            #old Id
            mil =u""
            if filmNumber[:2] == u"01":
                mil = u"19"
            elif filmNumber[:2] == u"02":
                mil = u"20"
            else:
                return False, u"Die Filmnummer im Footprint Layer entspricht weder dem alten (8-stellig) nch dem neuen (10-stellig) Filmnummernschema ({0}).".format()
            filmNumber = u"01{0}{1}".format(mil,filmNumber[2:])
        elif len(filmNumber) == 10:
            #new Id
            pass
        else:
            return False, u"Die Filmnummer im Footprint Layer entspricht weder dem alten (8-stellig) nch dem neuen (10-stellig) Filmnummernschema ({0}).".format()

        if filmNumber != self.filmId:
            return False, u"Im Footprint Layer sind Bilder eines anderen Films ({0}).".format(list(filmNumberFP)[0])


        return True, u"MonoplotLayer"

    def checkIfTargetIsClean(self):
        if self.targetLayerCP.featureCount() != self.targetLayerFP.featureCount():
            return False, u"Die Feature Anzahl bereits kartierter Bilder stimmt nicht überein (Centerpoint: {0}, Footprint: {1})".format(self.targetLayerCP.featureCount(), self.targetLayerFP.featureCount())

        existingFeaturesCP = set(self.targetLayerCP.getValues("bildnummer")[0])
        existingFeaturesFP = set(self.targetLayerFP.getValues("bildnummer")[0])
        CPwoFP = list(set(existingFeaturesCP) - set(existingFeaturesFP))
        FPwoCP = list(set(existingFeaturesFP) - set(existingFeaturesCP))

        if len(CPwoFP) > 0 or len(FPwoCP) > 0:
            errorMsg = u"Bitte beheben Sie folgende Probleme vor dem Import. Centerpoints ohne Footprints oder umgekehrt"
            if len(CPwoFP) > 0:
                errorMsg += u"\n{0}".format(u", ".join(CPwoFP))
            if len(FPwoCP) > 0:
                errorMsg += u"\n{0}".format(u", ".join(FPwoCP))
            return False, errorMsg

        return True, u"TargetIsClean"

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

    def writeMsg(self, msg):
        self.uiReportPTxt.insertPlainText(msg)
        self.uiReportPTxt.insertPlainText(u"\n")
        self.uiReportPTxt.ensureCursorVisible()

    def run(self):
        self.uiImportBtn.setEnabled(False)
        res1, msg1 = self.areSourceLayerMonoplot()
        res2, msg2 = self.checkIfTargetIsClean()
        if res1 and res2:

            iterCP = self.sourceLayerCP.getFeatures()
            iterFP = self.sourceLayerFP.getFeatures()
            existingFeaturesCP = self.targetLayerCP.getValues("bildnummer")[0]
            existingFeaturesFP = self.targetLayerFP.getValues("bildnummer")[0]

            mode = 1 #eintragen
            if self.targetLayerCP.featureCount() > 0 or self.targetLayerFP.featureCount() > 0:

                msgBox = QMessageBox()
                msgBox.setWindowTitle(u'Monoplot Import')
                msgBox.setText(u"Für den Film {0} sind kartierte Bilder vorhanden:".format(self.filmId))
                msgBox.addButton(QPushButton(u'Überschreiben'), QMessageBox.ActionRole)
                msgBox.addButton(QPushButton(u'Nicht überschreiben'), QMessageBox.ActionRole)
                msgBox.addButton(QPushButton(u'Abbrechen'), QMessageBox.RejectRole)
                ret = msgBox.exec_()
                if ret == 0:
                    mode = 2 #überschreiben
                    self.writeMsg(u"Bereits kartierte Bilder: überschreiben")
                elif ret == 1:
                    mode = 3 #nicht überschreiben/überspringen
                    self.writeMsg(u"Bereits kartierte Bilder: nicht überschreiben")
                else:
                    self.writeMsg(u"Vorgang wurde abgebrochen.")
                    self.uiImportBtn.setEnabled(True)
                    return

            capsCP = self.targetLayerCP.dataProvider().capabilities()
            capsFP = self.targetLayerFP.dataProvider().capabilities()
            if capsCP & QgsVectorDataProvider.AddFeatures and capsFP & QgsVectorDataProvider.AddFeatures:
                featuresCP = []
                featuresFP = []
                imagesToDelete = []
                #for sourceFeat in iterCP:
                sourceFeatCP = QgsFeature()
                sourceFeatFP = QgsFeature()
                i = 0
                while iterCP.nextFeature(sourceFeatCP):
                    i += 1
                    iterFP.nextFeature(sourceFeatFP)

                    imageNumber = int(sourceFeatCP["Image"].split('_')[1].split('.')[0])
                    imageNumberFP = int(sourceFeatFP["Image"].split('_')[1].split('.')[0])
                    if imageNumber != imageNumberFP:
                        self.writeMsg(u"SKIP: Die fortlaufende Bildnummer in Reihe {i} stimmen im Centerpoint ({1}) und Footprint ({2}) Layer nicht überein.".format(i, imageNumber, imageNumberFP))
                        continue

                    bn = '{0}.{1:03d}'.format(self.filmId, imageNumber)

                    errorCP = int(sourceFeatCP["ERROR"])
                    errorFP = int(sourceFeatFP["ERROR"])

                    if errorCP > 0 or errorFP > 0:
                        self.writeMsg(u"SKIP: {0}: Zumindest in einem Layer ist der ERROR Wert > 0 (CP: {1}, FP: {2})".format(bn, errorCP, errorFP))
                        continue

                    if bn in existingFeaturesCP or bn in existingFeaturesFP:
                        if mode == 2:
                            # überschreiben
                            #QMessageBox.warning(None, u"Bild Nummern", u"Ein Bild mit der Nummer {0} wurde bereits kartiert".format(imageNumber))
                            self.writeMsg(u"UPDATE: {0}: wird überchrieben.".format(bn))
                            imagesToDelete.append(bn)

                        elif mode == 3:
                            # nicht überschreiben
                            self.writeMsg(u"SKIP: {0}: wurde bereits kartiert.".format(bn))
                            continue
                    else:
                        self.writeMsg(u"NEW: {0}: wird erstellt.".format(bn))


                    #CENTERPOINT

                    targetFeatCP = QgsFeature(self.targetLayerCP.pendingFields())
                    #PpointGeometry
                    #ct = QgsCoordinateTransform(self.sourceLayerCP.crs(), self.targetLayerCP.crs())
                    #targetGeometryCP = QgsGeometry(sourceFeatCP.geometry())
                    #targetGeometryCP.transform(ct)
                    targetGeometryCP = TransformGeometry(QgsGeometry(sourceFeatCP.geometry()), self.sourceLayerCP.crs(), self.targetLayerCP.crs())
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

                    #targetFeatCP.setAttribute('radius', 175)
                    #targetFeatCP.setAttribute('keyword', NULL)
                    #targetFeatCP.setAttribute('description', NULL)

                    targetFeatCP.setAttribute('hoehe', 0)

                    # Calculated/Derived
                    cp = targetFeatCP.geometry().asPoint()
                    targetFeatCP.setAttribute('longitude', cp.x())
                    targetFeatCP.setAttribute('latitude', cp.y())

                    countryCode = self.getCountryCode(cp)
                    targetFeatCP.setAttribute('land', countryCode)

                    if countryCode == 'AUT':
                        #get meridian and epsg Code
                        meridian, epsgGK = GetMeridianAndEpsgGK(cp.x())

                        # get KG Coordinates
                        gk = TransformGeometry(QgsGeometry(targetFeatCP.geometry()), self.targetLayerCP.crs(), QgsCoordinateReferenceSystem(epsgGK, QgsCoordinateReferenceSystem.EpsgCrsId))
                        gkx = gk.asPoint().y()  # Hochwert
                        gky = gk.asPoint().x()  # Rechtswert
                    else:
                        meridian = NULL
                        gkx = NULL
                        gky = NULL

                    targetFeatCP.setAttribute('meridian', meridian)
                    targetFeatCP.setAttribute('gkx', gkx) # Hochwert
                    targetFeatCP.setAttribute('gky', gky) # Rechtswert

                    exif = self.getExifForImage(bn)
                    #exif = [None, None, None, None, None, None]
                    if exif[0]:
                        targetFeatCP.setAttribute('hoehe', exif[0])

                    targetFeatCP.setAttribute('gps_longitude', exif[1] if exif[1] is not None else NULL)
                    targetFeatCP.setAttribute('gps_latitude', exif[2] if exif[2] is not None else NULL)

                    if exif[1] and exif[2]:
                        capturePoint = QgsPoint(exif[1], exif[2])
                        kappa = capturePoint.azimuth(cp)
                    else:
                        kappa = NULL

                    targetFeatCP.setAttribute('kappa', kappa)

                    targetFeatCP.setAttribute('belichtungszeit', exif[3] if exif[3] is not None else NULL)
                    targetFeatCP.setAttribute('fokus', exif[4] if exif[4] is not None else NULL) # FocalLength
                    if exif[4] and exif[5]:
                        blende =exif[4]/exif[5] #effecitve aperture (diameter of entrance pupil) = focalLength / fNumber
                    else:
                        blende = NULL
                    targetFeatCP.setAttribute('blende', blende)



                    # FOOTPRINT

                    targetFeatFP = QgsFeature(self.targetLayerFP.pendingFields())

                    targetGeometryFP = TransformGeometry(QgsGeometry(sourceFeatFP.geometry()), self.sourceLayerFP.crs(), self.targetLayerFP.crs())
                    targetFeatFP.setGeometry(targetGeometryFP)

                    pointCP = QgsGeometry(sourceFeatCP.geometry())
                    polyline = sourceFeatFP.geometry().asPolygon()[0]
                    points = [QgsGeometry.fromPoint(point) for point in polyline]
                    dists = list(set([point.distance(pointCP) for point in points]))
                    #QMessageBox.information(None, "Radius", u"{0}, {1}".format(sorted(dists)[0], sorted(dists)[1]))
                    r = int((sorted(dists)[0]+sorted(dists)[1])/2.0)
                    targetFeatCP.setAttribute('radius', r if r > 175 else 175)

                    targetFeatFP.setAttribute('filmnummer', self.parent.currentFilmNumber)
                    targetFeatFP.setAttribute('bildnummer', bn)


                    featuresCP.append(targetFeatCP)
                    featuresFP.append(targetFeatFP)

                if imagesToDelete:
                    request = QgsFeatureRequest().setFilterExpression(u'"bildnummer" IN ({0})'.format(u', '.join(u'\'{0}\''.format(img) for img in imagesToDelete)))
                    featureIdsCPToDelete = []
                    featureIdsFPToDelete = []

                    for f in self.targetLayerCP.getFeatures(request):
                        featureIdsCPToDelete.append(f.id())

                    for f in self.targetLayerFP.getFeatures(request):
                        featureIdsFPToDelete.append(f.id())

                    res = self.targetLayerCP.dataProvider().deleteFeatures(featureIdsCPToDelete)
                    res = self.targetLayerFP.dataProvider().deleteFeatures(featureIdsFPToDelete)

                if featuresCP:
                    (res, outFeats) = self.targetLayerCP.dataProvider().addFeatures(featuresCP)
                    self.targetLayerCP.updateExtents()

                if featuresFP:
                    (res, outFeats) = self.targetLayerFP.dataProvider().addFeatures(featuresFP)
                    self.targetLayerFP.updateExtents()

                if self.iface.mapCanvas().isCachingEnabled():
                    self.targetLayerCP.setCacheImage(None)
                    self.targetLayerFP.setCacheImage(None)
                else:
                    self.iface.mapCanvas().refresh()

            else:
                QMessageBox.warning(None, u"Layer Capabilities!" u"Probleme mit Layer Capabilities!")


               #.warning(None, "MonoplotImport", u"{0}".format(id))
        else:
            if not res1:
                QMessageBox.warning(None, "MonoplotImport", u"Die Ausgewählten Centerpoint und Footprint Layer sind für den MONOPLOT Import ungeeignet:\n{0}".format(msg1))

            if not res2:
                QMessageBox.warning(None, "MonoplotImport", u"Es sind Probleme bei bereits kartierten Bildern vorhanden:\n{0}".format(msg2))
