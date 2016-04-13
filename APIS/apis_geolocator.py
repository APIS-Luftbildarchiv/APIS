# -*- coding: utf-8 -*

from PyQt4.QtSql import *
from qgis.core import *

class ApisGeolocator:

    def __init__(self, dbm):

        self.dbm = dbm

        # Load kgs
        # Load countries

    def countryByPoint(self, point):
        qryStr = "SELECT code FROM osm_boundaries WHERE intersects(Transform(MakePoint({0}, {1}, 4312), 4326), geometry)  AND ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'osm_boundaries' AND search_frame = Transform(MakePoint({0}, {1}, 4312), 4326))".format(
            self.imageCenterPoint.x(), self.imageCenterPoint.y())
        query.exec_(qryStr)
        query.first()
        if query.value(0) is None:
            return 'INT'
        else:
            return query.value(0)
        return code, name

    def countryByPolygon(self, polygon):
        pass
        return code, name

    def kgAustriaByPoint(self, point):
        pass
        return code, name

    def kgAustriaByPolygon(self, point):
        pass
        return code, name

    def isPointInAustria(self, point):
        pass

    def intersectsPolygonAustira(self, polygon):
        pass


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

