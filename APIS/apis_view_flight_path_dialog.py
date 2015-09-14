# -*- coding: utf-8 -*

import os

from PyQt4.QtCore import QSettings, Qt
from PyQt4.QtGui import *
from PyQt4.QtSql import QSqlQuery

from qgis.core import *

from apis_points2path import Points2Path

import sys
import os.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

# --------------------------------------------------------
# Film - Eingabe, Pflege
# --------------------------------------------------------
from apis_view_flight_path_form import *

class ApisViewFlightPathDialog(QDialog, Ui_apisViewFlightPathDialog):

    def __init__(self, iface, dbm):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.dbm = dbm
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)
        self.accepted.connect(self.onAccepted)

        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        self.chkBoxes = [self.uiGpsFlightPointChk, self.uiGpsFlightLineChk, self.uiGpsCameraPointChk, self.uiGpsCameraLineChk, self.uiMappingPointChk, self.uiMappingLineChk]
        for chkBox in self.chkBoxes:
            chkBox.stateChanged.connect(self.onSelectionChange)

    def showEvent(self, evnt):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        for chkBox in self.chkBoxes:
            chkBox.setCheckState(Qt.Unchecked)

    def onSelectionChange(self):
        status = False
        for chkBox in self.chkBoxes:
            if chkBox.checkState() == Qt.Checked:
                status = True
                break
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(status)

    def viewFilms(self, films):
        #QMessageBox.warning(None, "Test", ";".join(films))

        #s = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)
        query = QSqlQuery(self.dbm.db)

        table = self.uiFlightPathAvailabilityTable
        table.setRowCount(0)

        self.filmsDict = {}
        chkAvailability = [False, False, False, False]

        for film in films:
            availability = [False] * 4
            flightPathDirectory = self.settings.value("APIS/flightpath_dir") + "\\" + self.yearFromFilm(film)
            if os.path.isdir(flightPathDirectory):
                availability[0] = os.path.isfile(flightPathDirectory + "\\" + film + ".shp")
                if availability[0]:
                    chkAvailability[0] = True
                availability[1] = os.path.isfile(flightPathDirectory + "\\" + film + "_lin.shp")
                if availability[1]:
                    chkAvailability[1] = True
                availability[2] = os.path.isfile(flightPathDirectory + "\\" + film + "_gps.shp")
                if availability[2]:
                    chkAvailability[2] = True

            # Kartierung
            # Input Filmnummer, weise > je nacch weise andere Tabelle (CenterPoint) für Select (COUNT)
            # Wenn für Film Bilder kartiert sind ja anzeigen

            qryStr = "select weise from film where filmnummer = '{0}'".format(film)
            query.exec_(qryStr)
            query.first()
            fn = query.value(0)

            if fn == u"schräg":
                self.orientation = "schraeg"
            else:
                self.orientation = "senk"

            qryStr = "select count(*) from luftbild_{0}_cp where filmnummer = '{1}'".format(self.orientation,film)
            query.exec_(qryStr)
            query.first()
            fn = query.value(0)

            if fn > 0:
                availability[3] = True
                chkAvailability[3] = True

            rowPosition = table.rowCount()
            table.insertRow(rowPosition)
            table.setItem(rowPosition , 0, QTableWidgetItem(film))
            table.setItem(rowPosition , 1, QTableWidgetItem(unicode(availability[0])))
            table.setItem(rowPosition , 2, QTableWidgetItem(unicode(availability[1])))
            table.setItem(rowPosition , 3, QTableWidgetItem(unicode(availability[2])))
            table.setItem(rowPosition , 4, QTableWidgetItem(unicode(availability[3])))

            table.resizeRowsToContents()
            table.resizeColumnsToContents()
            table.horizontalHeader().setResizeMode(QHeaderView.Stretch)

            self.filmsDict[film] = availability

        self.uiGpsFlightPointChk.setEnabled(chkAvailability[0])
        self.uiGpsFlightLineChk.setEnabled(chkAvailability[1])
        self.uiGpsCameraPointChk.setEnabled(chkAvailability[2])
        self.uiGpsCameraLineChk.setEnabled(chkAvailability[2])
        self.uiMappingPointChk.setEnabled(chkAvailability[3])
        self.uiMappingLineChk.setEnabled(chkAvailability[3])

    def loadLayer(self):
        uri = QgsDataSourceURI()
        uri.setDatabase(self.dbm.db.databaseName())

        for key, item in self.filmsDict.items():
            flightPathDirectory =  self.settings.value("APIS/flightpath_dir") + "\\" + self.yearFromFilm(key)
            if item[0] and self.uiGpsFlightPointChk.checkState() == Qt.Checked:
                self.iface.addVectorLayer(flightPathDirectory+ "\\" + key + ".shp", "flugstrecke {0}".format(key), 'ogr')
            if item[1] and self.uiGpsFlightLineChk.checkState() == Qt.Checked:
                self.iface.addVectorLayer(flightPathDirectory+ "\\" + key + "_lin.shp", "flugstrecke {0}".format(key), 'ogr')
            if item[2] and (self.uiGpsCameraPointChk.checkState() == Qt.Checked or self.uiGpsCameraLineChk.checkState() == Qt.Checked):
                #self.iface.addVectorLayer(flightPathDirectory+ "\\" + key + "_gps.shp", "flugstrecke {0} gps p".format(key), 'ogr')

                vlayer = QgsVectorLayer(flightPathDirectory+ "\\" + key + "_gps.shp", "flugstrecke {0} gps p".format(key), 'ogr')
                if self.uiGpsCameraPointChk.checkState() == Qt.Checked:
                    QgsMapLayerRegistry.instance().addMapLayer(vlayer)

                if self.uiGpsCameraLineChk.checkState() == Qt.Checked:
                    p2p = Points2Path(vlayer, 'flugstrecke {0} gps l'.format(key), False, ["bildnr"])
                    vlayer_l = p2p.run()
                    QgsMapLayerRegistry.instance().addMapLayer(vlayer_l)

            if item[3] and (self.uiMappingPointChk.checkState() == Qt.Checked or self.uiMappingLineChk.checkState() == Qt.Checked):
                uri.setDataSource('', 'luftbild_{0}_cp'.format(self.orientation), 'geom')

                vlayer = QgsVectorLayer(uri.uri(), 'Kartierung {0} p'.format(key), 'spatialite')
                vlayer.setSubsetString(u'"filmnummer" = "{0}"'.format(key))
                if self.uiMappingPointChk.checkState() == Qt.Checked:
                    QgsMapLayerRegistry.instance().addMapLayer(vlayer)

                if self.uiMappingLineChk.checkState() == Qt.Checked:
                    p2p = Points2Path(vlayer, 'Kartierung {0} l'.format(key), False, ["bildnummer_nn"])
                    vlayer_l = p2p.run()
                    QgsMapLayerRegistry.instance().addMapLayer(vlayer_l)


    def yearFromFilm(self, film):
        year = ""
        if film[:2] == "01":
            year = "19"
        elif film[:2] == "02":
            year = "20"
        return year + film[2:4]

    def onAccepted(self):
        self.loadLayer()
