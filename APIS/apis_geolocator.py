# -*- coding: utf-8 -*

from PyQt4.QtSql import *
from qgis.core import *

class ApisGeolocator:

    def __init__(self, dbm):

        self.dbm = dbm

        # Load kgs
        # Load countries

    def setLocation(self, location):
        self.__location = QgsPoint(location)
        # Handle Projection
        self.__countryName, self.__countryCode = self.__getCountryDetails()
        #self.__kgName, self.__kgCode = self.getKgDetails()

    def countryName(self):
        return self.__countryName

    def countryCode(self):
        return self.__countryCode

    def kgName(self):
        if self.__countryCode == 'AUT':
            return self.__kgName
        else:
            return False

    def kgCode(self):
        if self.__countryCode == 'AUT':
            return self.__kgCode
        else:
            return False

    def __getCountryDetails(self):
        self.query = QSqlQuery(self.dbm.db)
        qryStr = "SELECT NAME as name, ISO3166 as code FROM osm_borders WHERE within(MakePoint({0}, {1}, 4312), Geometry)".format(self.__location.x(), self.__location.y())
        self.query.exec_(qryStr)
        self.query.first()
        return self.query.value(0), self.query.value(1)

    def __getKgDetails(self):
        self.query = QSqlQuery(self.dbm.db)
        qryStr = "SELECT KGNAME as name, KGNUM as code FROM kgs WHERE within(MakePoint({0}, {1}, {2}), geom)".format(self.__location.x(), self.__location.y(), 4312)
        self.query.exec_(qryStr)
        self.query.first()
        return self.query.value(0), self.query.value(1)

