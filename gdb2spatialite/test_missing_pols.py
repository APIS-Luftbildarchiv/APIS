# -*- coding: utf-8 -*-

import os, sys, math
from osgeo import ogr
from osgeo import osr
from pyspatialite import dbapi2 as db
import json
from datetime import datetime
import logging

from pprint import pprint

class ApisSpatialite:

    def __init__(self, targetDB):

        self.table = None
        self._InitSpatialiteDatabase(targetDB) # self.slConnection, self.slCursor

        self.ogr2spatialite = {
            0: "GEOMETRY",
            1: "POINT",
            2: "LINESTRING",
            3: "POLYGON",
            4: "MULTIPOINT",
            5: "MULTILINESTRING",
            6: "MULTIPOLYGON"
        }

        self.typeDict = {
            "Integer": "INTEGER",
            "String": "TEXT",
            "Real": "REAL",
            "DateTime": "DATETIME",
            "Date": "DATETIME",
            "Time": "DATETIME"
        }

    def _InitSpatialiteDatabase(self, spatialitePath):
        try:
             # creating/connecting the spatialite db
            self.slConnection = db.connect(spatialitePath)
            print "> Connecting Spatialite Database ({0})".format(os.path.abspath(spatialitePath))

            # creating a Cursor
            self.slCursor = self.slConnection.cursor()

            # testing library versions
            rs = self.slCursor.execute('SELECT sqlite_version(), spatialite_version()')
            for row in rs:
                msg = "> SQLite v{0} Spatialite v{1}".format(row[0], row[1])
                print msg

            # initializing Spatial MetaData
            # using v.2.4.0 this will automatically create
            # GEOMETRY_COLUMNS and SPATIAL_REF_SYS
            #sql = 'SELECT InitSpatialMetadata(1)'
            #self.slCursor.execute(sql)
            #print "> Initialize Spatialite Metadata"
        except OSError, e:
            print "> Error Connecting Spatialite Database", e
            sys.exit(1)

    def CleanUp(self):
        print "> CleanUp and finish script"
        self.slCursor.close()
        self.slConnection.close()

    def _PointToRectangle(self, cpWkt, d=100, epsg=4312):
        #print cpWkt, r, dpWkt
        cp = ogr.CreateGeometryFromWkt(cpWkt)
        cpWGS = ogr.CreateGeometryFromWkt(cpWkt)

        source = osr.SpatialReference()
        source.ImportFromEPSG(epsg)

        target2 = osr.SpatialReference()
        target2.ImportFromEPSG(4326)

        t = osr.CoordinateTransformation(source, target2)
        cpWGS.Transform(t)

        target = osr.SpatialReference()
        target.ImportFromProj4(self._Proj4Utm(cpWGS))
        #print target.ExportToProj4()

        tF = osr.CoordinateTransformation(source, target)
        tI = osr.CoordinateTransformation(target, source)

        cp.Transform(tF)

        #poly2 = cp.Buffer(100).Simplify(20)
        # s = (d/2)/math.sqrt(2)
        s = 70
        l = cp.GetX() - s
        b = cp.GetY() - s
        r = cp.GetX() + s
        t = cp.GetY() + s

        poly = ogr.CreateGeometryFromWkt("POLYGON (({0} {1}, {2} {1}, {2} {3}, {0} {3}, {0} {1}))".format(l,b,r,t))
        sa = poly.GetArea()
        sl = 0.0
        #sl = ogr.ForceToLineString(poly).Length()
        poly.Transform(tI)

        return poly, sl, sa

    def _Proj4Utm(self, p):
        x = p.GetX()
        y = p.GetY()
        z = math.floor((x + 180)/6) + 1

        if y >= 56.0 and y < 64.0 and x >= 3.0 and x < 12.0:
            z = 32

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

    def generateMissingSitePolygons(self):
        # Get Site Points which miss a Polygon
        rs = self.slCursor.execute("SELECT fundortnummer, filmnummer_projekt, AsText(geometry) FROM fundort_pnt WHERE fundort_pnt.fundortnummer IS NOT NULL AND fundort_pnt.fundortnummer NOT IN (SELECT fundort_pol.fundortnummer FROM fundort_pol WHERE fundort_pol.fundortnummer IS NOT NULL)")
        rows_pol = []
        for row_pnt in rs:
            row_pol = [row_pnt[0], row_pnt[1], "-1"]
            poly, sl, sa = self._PointToRectangle(row_pnt[2])
            polGeom = ogr.ForceToMultiPolygon(poly)
            epsg = 4312

            row_pol += [sl, sa, polGeom.ExportToWkt(), epsg]
            rows_pol.append(row_pol)

        sql = "INSERT INTO fundort_pol (fundortnummer, filmnummer_projekt, bildnummer, shape_length, shape_area, geometry) VALUES(?,?,?,?,?,GeomFromText(?, ?))"

        self.slCursor.executemany(sql, rows_pol)
        self.slConnection.commit()

    def generateMissingFindSpotPolygons(self):
        # Get FindSpots Points which miss a Polygon
        rs = self.slCursor.execute("SELECT fundortnummer, fundstellenummer, AsText(geometry) FROM fundstelle_pnt WHERE fundstelle_pnt.fundortnummer IS NOT NULL AND fundstelle_pnt.fundortnummer NOT IN (SELECT fundstelle_pol.fundortnummer FROM fundstelle_pol WHERE fundstelle_pol.fundortnummer IS NOT NULL)")

        rows_pol = []
        for row_pnt in rs:
            row_pol = [row_pnt[0], row_pnt[1]]
            poly, sl, sa = self._PointToRectangle(row_pnt[2])
            polGeom = ogr.ForceToMultiPolygon(poly)
            epsg = 4312

            row_pol += [sl, sa, polGeom.ExportToWkt(), epsg]
            rows_pol.append(row_pol)

        sql = "INSERT INTO fundstelle_pol (fundortnummer, fundstellenummer, shape_length, shape_area, geometry) VALUES(?,?,?,?,GeomFromText(?, ?))"

        self.slCursor.executemany(sql, rows_pol)
        self.slConnection.commit()


if __name__ == '__main__':
    d = datetime.today()
    targetDB = "dbtest/APIS_20160105_183606_17.sqlite"
    #" #APIS_20160105_183606.sqlite"

    apis = ApisSpatialite(targetDB)

    apis.generateMissingSitePolygons()
    apis.generateMissingFindSpotPolygons()

    apis.CleanUp()