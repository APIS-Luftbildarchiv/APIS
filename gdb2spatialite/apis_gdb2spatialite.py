# -*- coding: utf-8 -*-

import os, sys, math
from osgeo import ogr
from osgeo import osr
from pyspatialite import dbapi2 as db
import json
from datetime import datetime
from pprint import pprint

class ApisSpatialite:

    def __init__(self, targetDB):

        self.table = None
        self.sourceDB = None
        self.currentSoruceDBPath = None

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
            "DateTime": "DATETIME"
        }

    def _InitSpatialiteDatabase(self, spatialitePath):
        try:
            os.remove(spatialitePath)
        except:
            pass

        try:
             # creating/connecting the spatialite db
            self.slConnection = db.connect(spatialitePath)
            print "> Creating Spatialite Database ({0})".format(os.path.abspath(spatialitePath))

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
            sql = 'SELECT InitSpatialMetadata(1)'
            self.slCursor.execute(sql)
            print "> Initialize Spatialite Metadata"
        except OSError, e:
            print "> Error Creating Spatialite Database", e
            sys.exit(1)


    def _OpenGdb(self, gdbPath):
        self.currentSoruceDBPath = gdbPath
        ogr.UseExceptions()
        driver = ogr.GetDriverByName("OpenFileGDB")
        try:
            self.sourceDB = driver.Open(gdbPath, 0)
            print "> Opening ESRI FileGDB ({0})".format(os.path.abspath(gdbPath))
        except Exception, e:
            print "> Error Opening FileGDB", e
            sys.exit(1)

    def _CreateSpatialiteTable(self):
        try:
            print "> Create Spatialite Table ({0})".format(self.table['targetname'])

            sql = "DROP TABLE IF EXISTS {0}".format(self.table['targetname'])
            self.slCursor.execute(sql)

            sql = "CREATE TABLE {0} ".format(self.table['targetname'])
            sql += "("

            fieldCount = 0
            for field in self.table['fields']:
                fieldCount += 1
                sql += "{0} {1}".format(field['targetname'], self.typeDict[field['type']])
                if field['targetname'] == self.table['primary']:
                    sql += " PRIMARY KEY"
                if fieldCount < len(self.table['fields']):
                    sql += ", "
            sql += ")"
            self.slCursor.execute(sql)

            if self.table['type'] != 100:
                # creating Geometry column
                sql = "SELECT AddGeometryColumn('{0}',".format(self.table['targetname'])
                sql += "'geometry', {0}, '{1}', 'XY')".format(self.table['epsg'], self.ogr2spatialite[self.table['type']])
                self.slCursor.execute(sql)

                sql = "SELECT CreateSpatialIndex('{0}', 'geometry')".format(self.table['targetname'])
                self.slCursor.execute(sql)

            self.slConnection.commit()

        except Exception, e:
            print "> Error Creating Spatialite Table", e
            sys.exit(1)

    def _FillSpatialiteTable(self):
        if self.table['source'] == 'esrigdb':
            self._FillSpatialiteTableFromEsriGdb()

    def _FillSpatialiteTableFromEsriGdb(self):
        try:


            if self.sourceDB and self.currentSoruceDBPath != self.table['esrigdb']:
                del self.sourceDB
                self.sourceDB = None
            if not self.sourceDB:
                self._OpenGdb(self.table['esrigdb']) #self.sourceDB

            print "> Fill Spatialite Table ({0})".format(self.table['targetname'])

            sourceTable = self.sourceDB.GetLayerByName(self.table['sourcename'].encode("utf-8"))
            if not sourceTable:
                sys.exit("ERROR: can not find layer '{0}' in GeoDB".format(self.table['sourcename'].encode("utf-8")))

            placeholderFieldsArr = []
            placeholderValuesArr = []
            for field in self.table['fields']:
                if 'sourcename' not in field:
                    continue
                placeholderFieldsArr.append(field['targetname'])
                placeholderValuesArr.append('?')

            placeholderFields = ", ".join(placeholderFieldsArr)
            placeholderValues = ", ".join(placeholderValuesArr)
            if self.table['type'] != 100:
                placeholderFields += ", geometry"
                placeholderValues += ", GeomFromText(?, ?)"
            sql = "INSERT INTO {0} ({1}) VALUES({2})".format(self.table['targetname'], placeholderFields, placeholderValues)

            sourceTable.ResetReading()
            rows = []
            bildNr = []
            for feature in sourceTable:
                row = []
                for field in self.table['fields']:
                    if 'sourcename' not in field:
                        continue
                    sourceField = field['sourcename'].encode("utf-8")
                    if not feature.IsFieldSet(sourceField):
                        value = None
                    else:
                        fieldType = feature.GetFieldType(sourceField)
                        if fieldType == ogr.OFTInteger:
                            value = feature.GetFieldAsInteger(sourceField)

                        elif fieldType == ogr.OFTReal:
                            value = feature.GetFieldAsDouble(sourceField)

                        elif fieldType == ogr.OFTString:
                            ffs = feature.GetFieldAsString(sourceField)
                            value = ffs.decode('utf-8')

                        elif fieldType == ogr.OFTDateTime:
                            value = feature.GetFieldAsDateTime(feature.GetFieldIndex(sourceField))
                            value = "{0}-{1}-{2}".format(value[0],str(value[1]).zfill(2),str(value[2]).zfill(2))

                        # TODO: TypeCast (String to DateTime)

                    row.append(value)
                    if sourceField == "BILD":
                        bildNr.append(value)

                #add geometry
                if self.table['type'] != 100:
                    geometryRef = feature.GetGeometryRef()
                    defnRef = feature.GetDefnRef()
                    if defnRef.GetGeomType() == ogr.wkbMultiPolygon:
                        geometryRef = ogr.ForceToPolygon(geometryRef)

                    row.append(geometryRef.ExportToWkt())
                    row.append(int(self.table['epsg']))
                rows.append(row)

            self.slCursor.executemany(sql, rows)
            self.slConnection.commit()


        except Exception, e:
            print "> Error Filling Spatialite Table", e
            sys.exit(1)

    def _SetJsonFile(self, jsonFile):
        self.table = None
        with open(jsonFile,'rU') as table:
            self.table = json.load(table)

    def CleanUp(self):
        print "> CleanUp and finish script"
        del self.sourceDB
        self.slCursor.close()
        self.slConnection.close()

    def AddTable(self, jsonFile):
        self._SetJsonFile(jsonFile)
        self._CreateSpatialiteTable()
        self._FillSpatialiteTable()

if __name__ == '__main__':

    d = datetime.today()
    targetDB = "dbtest/APIS_{0}.sqlite".format(d.strftime("%Y%m%d_%H%M%S"))

    apis = ApisSpatialite(targetDB)

    apis.AddTable("config/luftbild_schraeg_cp.json")
    apis.AddTable("config/fundort_pol.json")

    apis.CleanUp()