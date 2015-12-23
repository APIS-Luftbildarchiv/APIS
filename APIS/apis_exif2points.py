# -*- coding: utf-8 -*-
#-----------------------------------------------------------
#
# Points2One
# Copyright (C) 2010 Pavol Kapusta <pavol.kapusta@gmail.com>
# Copyright (C) 2010, 2013, 2015 Goyo <goyodiaz@gmail.com>
#
#-----------------------------------------------------------
#
# licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#---------------------------------------------------------------------

from itertools import groupby

from PyQt4.QtCore import *
from PyQt4.QtGui import QMessageBox, QProgressBar
from qgis.core import *
from qgis.gui import QgsMessageBar

import pyexiv2 as exif
import glob
import os.path

class Exif2Points(object):
    """Data processing for Point2One."""

    def __init__(self, iface, filmNumber):
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)
        self.filmNumber = filmNumber
        self.iface = iface
        self.imagePath = os.path.normpath(self.settings.value("APIS/image_dir"))
        self.filmPath = os.path.join(self.imagePath, self.filmNumber)
        self.images = glob.glob(os.path.normpath(self.filmPath + "\\" + self.filmNumber + "_*.*"))
        self.flightPath = os.path.join(os.path.normpath(self.settings.value("APIS/flightpath_dir")), self.yearFromFilm(self.filmNumber))
        self.shpFile = os.path.normpath(self.flightPath + "\\" + self.filmNumber + "_gps.shp")

    def run(self):
        """Create the output shapefile."""
        gpsStatus = self.checkGpsStatus()
        if gpsStatus:
            pass
            #QMessageBox.warning(None, "Test", "Create GPS SHP")
        elif gpsStatus == None:
            QMessageBox.warning(None, "Verzeichnis", u"Es wurde kein Bildverzeichnis für diesen Film gefunden.")
            return
        else:
            QMessageBox.warning(None, "Bilder", u"Die vorhandenen Bilder enthalten keine GPS Information.")
            return

        check = QFile(self.shpFile)
        if check.exists():
            if not QgsVectorFileWriter.deleteShapeFile(self.shpFile):
                msg = 'Unable to delete existing shapefile "{}"'
                self.iface.messageBar().pushMessage(u"Error", u"Die Datei existiert bereits und kann nicht überschrieben werden (Eventuell in QGIS geladen!).", level=QgsMessageBar.CRITICAL, duration=10)
                return False

        #fields
        fields = QgsFields()
        fields.append(QgsField("bildnr", QVariant.Int))
        fields.append(QgsField("lat", QVariant.Double))
        fields.append(QgsField("lon", QVariant.Double))
        fields.append(QgsField("alt", QVariant.Double))

        writer = QgsVectorFileWriter(str(self.shpFile), "UTF-8", fields, QGis.WKBPoint, QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId))

        mb = self.iface.messageBar().createMessage(u"EXIF", u"Die EXIF Daten (Geo Koordinaten und Höhe) werden aus den Bildern ausgelesen")
        progress = QProgressBar()
        progress.setMinimum(0)
        progress.setMaximum(0)
        progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        mb.layout().addWidget(progress)
        self.iface.messageBar().pushWidget(mb, QgsMessageBar.INFO)

        for feature in self.iter_points():
            writer.addFeature(feature)
        del writer
        self.iface.messageBar().clearWidgets()
        self.iface.messageBar().pushMessage(u"EXIF", u"Die Shape Datei wurde erfolgreich erstellt und in QGIS geladen!", level=QgsMessageBar.SUCCESS, duration=10)


        return self.shpFile

    def checkGpsStatus(self):
        if os.path.isdir(self.filmPath) and len(self.images) > 0:
            for image in self.images:
                md = exif.ImageMetadata(image)
                md.read()
                a = ["Exif.GPSInfo.GPSLongitude", "Exif.GPSInfo.GPSLatitude"]
                b = md.exif_keys
                any_in = any(i in b for i in a)
                if any_in:
                    return True
            return False
        else:
            return None

    def iter_points(self):
        """Iterate over the features of the input layer.
    
        Yields pairs of the form (QgsPoint, attributeMap).
        Each time a vertice is read hook is called.
    
        """
        #provider = self.layer.dataProvider()
        #features = provider.getFeatures()
        #feature = QgsFeature()

        #while(features.nextFeature(feature)):
            #geom = feature.geometry().asPoint()
            #attributes = feature.attributes()
        for image in self.images:
            imageName = os.path.basename(image)
            imageNumber = int(imageName[9:12])
            md = exif.ImageMetadata(image)
            md.read()

            #for key in md.exif_keys:
            if "Exif.GPSInfo.GPSLongitude" in md.exif_keys:
                lon = md["Exif.GPSInfo.GPSLongitude"].value
                ddlon = float(lon[0])+((float(lon[1])+(float(lon[2])/60))/60)
            else:
                ddlon = None
                continue

            if "Exif.GPSInfo.GPSLatitude" in md.exif_keys:
                lat = md["Exif.GPSInfo.GPSLatitude"].value
                ddlat = float(lat[0])+((float(lat[1])+(float(lat[2])/60))/60)
            else:
                ddlat = None
                continue

            if "Exif.GPSInfo.GPSAltitude" in md.exif_keys:
                alt = float(md["Exif.GPSInfo.GPSAltitude"].value)
            else:
                alt = None

            #if "Exif.GPSInfo.GPSMapDatum" in md.exif_keys:
            #    mapDatum = unicode(md["Exif.GPSInfo.GPSMapDatum"].value)
            #else:
            #    mapDatum = None

            #print imageName, imageNumber, ddlon, ddlat, alt, mapDatum
            attributes = [imageNumber, ddlat, ddlon, alt]

            del md
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPoint(QgsPoint(ddlon, ddlat)))
            feature.setAttributes(attributes)
            yield feature
                                                                       
    def log_warning(self, message):
        """Log a warning."""
        self.logger.append(message)

    def get_logger(self):
        """Return the list of logged warnings."""
        return self.logger

    def yearFromFilm(self, film):
        year = ""
        if film[:2] == "01":
            year = "19"
        elif film[:2] == "02":
            year = "20"
        return year + film[2:4]