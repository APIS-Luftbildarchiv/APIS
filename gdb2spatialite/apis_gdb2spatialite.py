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
            "DateTime": "DATETIME",
            "Date": "DATETIME",
            "Time": "DATETIME"
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
                if 'typecast' in field:
                    t = 'typecast'
                else:
                    t = 'type'
                sql += "{0} {1}".format(field['targetname'], self.typeDict[field[t]])
                #if field['targetname'] == self.table['primary']:
                #    sql += " PRIMARY KEY"
                if fieldCount < len(self.table['fields']):
                    sql += ", "
            if len(self.table['primary']) > 0:
                sql += ", CONSTRAINT pk_{0} PRIMARY KEY ({1})".format(self.table['targetname'], ", ".join(self.table['primary']))
            sql += ")"
            self.slCursor.execute(sql)

            if self.table['type'] != 100:
                # creating Geometry col:umn
                sql = "SELECT AddGeometryColumn('{0}',".format(self.table['targetname'])
                sql += "'geometry', {0}, '{1}', 'XY')".format(self.table['epsg'], self.ogr2spatialite[self.table['type']])
                self.slCursor.execute(sql)

                sql = "SELECT CreateSpatialIndex('{0}', 'geometry')".format(self.table['targetname'])
                self.slCursor.execute(sql)

            self.slConnection.commit()

        except Exception, e:
            print "> Error Creating Spatialite Table", e
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            sys.exit(1)

    def _FillSpatialiteTable(self):
        if self.table['source'] == 'esrigdb':
            self._FillSpatialiteTableFromEsriGdb()
        elif self.table['source'] == 'esrishp':
            self._FillSpatialiteTableFromEsriShp()
        elif self.table['source'] == 'data':
            self._FillSpatialiteTableFromData()
        elif self.table['source'] == 'aggregate':
            self._FillSpatialiteTableByAggregation()

    def _FillSpatialiteTableFromData(self):
        try:
            sql = "INSERT INTO {0} VALUES ({1})".format(self.table['targetname'], ','.join(map(unicode, ['?' for i in range(len(self.table['fields']))])))
            rows = []
            for row in self.table['data']:
                r = ()
                for field in self.table['fields']:
                    r += (row[field['targetname']],)
                rows.append(r)       
                    
            self.slCursor.executemany(sql, rows)
            self.slConnection.commit()
        except Exception, e:
            print "> Error Filling Spatialite Table", e
            sys.exit(1)

    def _FillSpatialiteTableFromEsriGdb(self):
        try:
            if self.sourceDB and self.currentSoruceDBPath != self.table['esrigdb']:
                del self.sourceDB
                self.sourceDB = None
            if not self.sourceDB:
                self._OpenGdb(self.table['esrigdb']) #self.sourceDB
            info = "> Fill Spatialite Table ({0})".format(self.table['targetname'])
            print info
            logging.info(info)

            sourceTable = self.sourceDB.GetLayerByName(self.table['sourcename'].encode("utf-8"))
            if not sourceTable:
                sys.exit("ERROR: can not find layer '{0}' in GeoDB".format(self.table['sourcename'].encode("utf-8")))

            placeholderFieldsArr = []
            placeholderValuesArr = []
            for field in self.table['fields']:
                if 'sourcename' not in field and 'incrementByFieldRow' not in field:
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
            primaryArr = []
            addFlag = True
            primary = self.table['primary']
            featureCount = 0
            for feature in sourceTable:
                row = []
                primaryValuesRow = []
                featureCount += 1
                for field in self.table['fields']:
                    targetField = field['targetname'].encode("utf-8")
                    if 'sourcename' not in field:
                        if 'incrementByFieldRow' in field:
                            if targetField in primary:
                                primaryValuesRow.append(featureCount)
                            row.append(featureCount)
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

                            if "".join(value.split()) == "":
                                value = None

                        elif fieldType == ogr.OFTDateTime:
                            value = feature.GetFieldAsDateTime(feature.GetFieldIndex(sourceField))
                            value = "{0}-{1}-{2}".format(value[0],str(value[1]).zfill(2),str(value[2]).zfill(2))

                        # TypeCast (String to DateTime)
                        if value and 'typecast' in field:
                            value = self._DoTypeCast(value, field['type'].encode("utf-8"), field['typecast'].encode("utf-8"))

                    # FIXME Problem wenn mehrere Felder Primary Key
                    if targetField in primary:
                        primaryValuesRow.append(value)

                    row.append(value)


                #add geometry
                if self.table['type'] != 100:
                    geometryRef = feature.GetGeometryRef()
                    defnRef = feature.GetDefnRef()
                    if defnRef.GetGeomType() == ogr.wkbMultiPolygon:
                        if 'geometrycheck' in self.table:
                            featureKey = feature.GetField(self.table['geometrycheck']['featurekey'].encode("utf-8"))
                            geometryRef = self._DoGeometryCheck(self.table['geometrycheck'], geometryRef, featureKey)
                            if self.table['type'] == 3:
                                geometryRef = ogr.ForceToPolygon(geometryRef)
                            else:
                                geometryRef = ogr.ForceToMultiPolygon(geometryRef)
                        else:
                            if self.table['type'] == 3:
                                geometryRef = ogr.ForceToPolygon(geometryRef)
                            else:
                                geometryRef = ogr.ForceToMultiPolygon(geometryRef)
                        
                    row.append(geometryRef.ExportToWkt())
                    row.append(int(self.table['epsg']))

                if len(primaryValuesRow) > 0 and set(primaryValuesRow) in primaryArr:
                    addFlag = False
                else:
                    addFlag = True
                    if len(primaryValuesRow) > 0:
                        primaryArr.append(set(primaryValuesRow))

                if addFlag:
                    rows.append(row)
                else:
                    i = 0
                    for item in primaryValuesRow:
                        if item is None:
                            primaryValuesRow[i] = 'NULL'
                        i += 1

                    val = ",".join(unicode(v) for v in primaryValuesRow)

                    warning = "> Warning: Row with primary key ({0}) already exists! It will not be added to new Database!".format(val)
                    print warning
                    logging.warning(warning)

            self.slCursor.executemany(sql, rows)
            self.slConnection.commit()

        except Exception, e:
            print "> Error Filling Spatialite Table", e
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            sys.exit(1)

    def _FillSpatialiteTableFromEsriShp(self):
        try:
            print "> Fill Spatialite Table ({0})".format(self.table['targetname'])

            driver = ogr.GetDriverByName('ESRI Shapefile')
            sourceShp = driver.Open(self.table['esrishp'], 0) # 0 means read-only. 1 means writeable.
            if sourceShp is None:
                sys.exit("ERROR: can not find shp '{0}'".format(self.table['esrishp'].encode("utf-8")))

            sourceTable = sourceShp.GetLayer()
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
            primaryArr = []
            addFlag = True
            primary = self.table['primary'][0]
            for feature in sourceTable:
                row = []
                for field in self.table['fields']:
                    if 'sourcename' not in field:
                        continue
                    sourceField = field['sourcename'].encode("utf-8")
                    targetField = field['targetname'].encode("utf-8")

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

                            if "".join(value.split()) == "":
                                value = None

                        elif fieldType == ogr.OFTDateTime:
                            value = feature.GetFieldAsDateTime(feature.GetFieldIndex(sourceField))
                            value = "{0}-{1}-{2}".format(value[0],str(value[1]).zfill(2),str(value[2]).zfill(2))

                        if value and 'typecast' in field:
                            value = self._DoTypeCast(value, field['type'].encode("utf-8"), field['typecast'].encode("utf-8"))

                    if targetField == primary:
                        if value in primaryArr:
                            addFlag = False
                        else:
                            addFlag = True
                            primaryArr.append(value)

                    row.append(value)

                #add geometry
                if self.table['type'] != 100:
                    geometryRef = feature.GetGeometryRef()
                    if self.table['type'] == 6:
                        geometryRef = ogr.ForceToMultiPolygon(geometryRef)
                    # defnRef = feature.GetDefnRef()
                    # if defnRef.GetGeomType() == ogr.wkbMultiPolygon:
                    #     if 'geometrycheck' in self.table:
                    #         featureKey = feature.GetField(self.table['geometrycheck']['featurekey'].encode("utf-8"))
                    #         geometryRef = self._DoGeometryCheck(self.table['geometrycheck'], geometryRef, featureKey)
                    #         geometryRef = ogr.ForceToPolygon(geometryRef)
                    #     else:
                    #         geometryRef = ogr.ForceToPolygon(geometryRef)

                    row.append(geometryRef.ExportToWkt())
                    row.append(int(self.table['epsg']))

                if addFlag:
                    rows.append(row)

            self.slCursor.executemany(sql, rows)
            self.slConnection.commit()

        except Exception, e:
            print "> Error Filling Spatialite Table", e
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            sys.exit(1)

    def _FillSpatialiteTableByAggregation(self):
        try:
            if self.sourceDB and self.currentSoruceDBPath != self.table['esrigdb']:
                del self.sourceDB
                self.sourceDB = None
            if not self.sourceDB:
                self._OpenGdb(self.table['esrigdb']) #self.sourceDB

            print "> Fill Spatialite Table ({0})".format(self.table['targetname'])

            rows = []
            for dataset in self.table['aggregate']: 
                row = []  
                for field in self.table['fields']:
                    # print field['name'], dataset[field['name']]
                    if isinstance(dataset[field['targetname']], dict):
                        if 'table' in dataset[field['targetname']] and 'attr' in dataset[field['targetname']]:
                            #print dataset[field['name']]['table'], dataset[field['name']]['attr']
                            layer = self.sourceDB.GetLayerByName(dataset[field['targetname']]['table'].encode("utf-8"))
                            # print layer.GetFeatureCount()
                            if not layer:
                                sys.exit("ERROR: can not find layer '{0}' in GeoDB".format(dataset[field['targetname']]['table'].encode("utf-8")))
                            layer.ResetReading()
                            r = []
                            for feature in layer:

                                # FIXME was passiert mit nicht strings
                                r.append(str(feature.GetField(dataset[field['targetname']]['attr'].encode("utf-8"))).decode("utf-8"))

                                #print dataset[field['name']]['attr'], str(feature.GetField(dataset[field['name']]['attr'].encode("utf-8"))).decode("utf-8")
                                #geom = feature.GetGeometryRef()
                                #print geom.Centroid().ExportToWkt()
                            row.append(r)
                    elif dataset[field['targetname']] == "None":
                        row.append(None)
                    else: # value
                        row.append(dataset[field['targetname']])
                rows.append(row)
            #sql
            #pprint(rows)
            results = []
            for r1 in rows:
                result = []
                result.append([])
                for i in r1:
                    if isinstance(i, list):
                        #print len(i), len(result)
                        while len(i) > len(result):
                            result.append([a for a in result[len(result)-1]])

                        for j, item in enumerate(result):
                            item.append(i[j])
                    else:
                        for insert in result:
                            insert.append(i)

                #remove dublicates
                resultChecked = [list(t) for t in set(tuple(element) for element in result)]
                results += resultChecked

            sql = "INSERT INTO {0} VALUES ({1})".format(self.table['targetname'], ','.join(map(unicode, ['?' for i in range(len(self.table['fields']))])))
            self.slCursor.executemany(sql, results)


        except Exception, e:
            print "> Error Filling Spatialite Table", e
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
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

    def AddTableJson(self, jsonFile):
        self._SetJsonFile(jsonFile)
        self._CreateSpatialiteTable()
        self._FillSpatialiteTable()

    # def AddTableSqlite(self, sqliteFile, tableName):
    #     try:
    #         print "> Adding Spatialite Table ({0} from {1})".format(tableName, sqliteFile)
    #         # Attach db to connection
    #         self.slCursor.execute("ATTACH DATABASE ? AS db2", (sqliteFile, ))
    #
    #         rs = self.slCursor.execute("SELECT DISTINCT Srid(geometry), GeometryType(geometry) FROM db2.{0}".format(tableName))
    #         for row in rs:
    #             epsg = row[0]
    #             geomType = row[1]
    #
    #         # Create new Table
    #         self.slCursor.execute("CREATE TABLE AS SELECT * FROM db2.{0}".format(tableName))
    #
    #
    #
    #         self.slCursor.execute("SELECT CreateSpatialIndex('{0}', 'geometry')".format(tableName))
    #
    #         # Detach db from connection
    #         self.slCursor.execute("DETACH DATABASE db2")
    #
    #         self.slConnection.commit()
    #
    #     except Exception, e:
    #         print "> Error Adding Spatialite Table", e
    #         sys.exit(1)

    def RunSqlUpdates(self, sqlUpdatesJson):
        try:
            print "> Running SQL Updates"
            with open(sqlUpdatesJson,'rU') as sqlUpdates:
                self.sqlUpdates = json.load(sqlUpdates)

            updateCount = len(self.sqlUpdates['sqlupdates'])
            updateCurrent = 0
            for update in self.sqlUpdates['sqlupdates']:
                updateCurrent += 1
                print "> Update {0}/{1}".format(updateCurrent, updateCount)
                self.slCursor.execute(update)

            self.slConnection.commit()

        except Exception, e:
            print "> Error Running SQL Updates", e
            sys.exit(1)

    def _DoTypeCast(self, value, fromType, toType):
        if fromType == 'String' and toType == 'Time':
            v = value.strip()

            if any(d in v for d in ('.',':')):
                r = v.split('.')
                if len(r) < 2:
                    r = v.split(':')
                r = "{0}:{1}:00".format(r[0].zfill(2), r[1].zfill(2))
            else:
                if len(v) == 4:
                    r = "{0}:{1}:00".format(v[0:2], v[2:4])
                elif len(v) == 3:
                    r = "{0}:{1}:00".format(v[0].zfill(2), v[1:3])
                elif len(v) == 2:
                    r = "{0}:00:00".format(v[0:2])
                elif len(v) == 1:
                    r = "{0}:00:00".format(v[0].zfill(2))
                else:
                    r = None
            return r
        elif fromType == 'String' and toType == 'Date':
            if len(value) == 10:
                r = "{0}-{1}-{2}".format(value[6:10], value[0:2], value[3:5]) # month-day-year > year-month-day
            elif len(value) == 19:
                r = "{0}-{1}-{2}".format(value[6:10], value[3:5], value[0:2]) # day-month-year > year-month-day
            else:
                r = None
            return r
        elif fromType == 'Real' and toType == 'Integer':
            return int(value)

    def _DoGeometryCheck(self, check, geometryRef, featureKey):
        try: 
            if check['type'] == "circle2polygon":

                for i in range(0, geometryRef.GetGeometryCount()):
                    g = geometryRef.GetGeometryRef(i)
                    for j in range(0, g.GetGeometryCount()):
                        circleCandidate = g.GetGeometryRef(i)
                        if circleCandidate and circleCandidate.GetPointCount() <= 2:
                            sql = check['sql'].encode("utf-8").format(featureKey)
                            rs = self.slCursor.execute(sql)
                            
                            for row in rs:
                                dp = circleCandidate.GetPoint(0)
                                geometryRef = self._Circle2Polygon(row[0], row[1], 'POINT ({0} {1})'.format(dp[0], dp[1]), check['epsg'])
            
            return geometryRef

        except Exception, e:
            print "> Error Doing Geometry Check", e
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            sys.exit(1)

    def _Circle2Polygon(self, cpWkt, r, dpWkt, epsg):
        #print cpWkt, r, dpWkt
        cp = ogr.CreateGeometryFromWkt(cpWkt)
        dp = ogr.CreateGeometryFromWkt(dpWkt)

        source = osr.SpatialReference()
        source.ImportFromEPSG(epsg)

        target = osr.SpatialReference()
        target.ImportFromProj4(self._Proj4Utm(cp))
        #print target.ExportToProj4()

        tF = osr.CoordinateTransformation(source, target)
        tB = osr.CoordinateTransformation(target, source)

        cp.Transform(tF)
        dp.Transform(tF)

       # print r, int(math.ceil(cp.Distance(dp)))

        poly = cp.Buffer(math.ceil(cp.Distance(dp)))
        poly.Transform(tB)

        return poly

    def _Point2Rectangle(self, cpWkt, d=100, epsg=4312):
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
            poly, sl, sa = self._Point2Rectangle(row_pnt[2])
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
            poly, sl, sa = self._Point2Rectangle(row_pnt[2])
            polGeom = ogr.ForceToMultiPolygon(poly)
            epsg = 4312

            row_pol += [sl, sa, polGeom.ExportToWkt(), epsg]
            rows_pol.append(row_pol)

        sql = "INSERT INTO fundstelle_pol (fundortnummer, fundstellenummer, shape_length, shape_area, geometry) VALUES(?,?,?,?,GeomFromText(?, ?))"

        self.slCursor.executemany(sql, rows_pol)
        self.slConnection.commit()



if __name__ == '__main__':
    d = datetime.today()
    targetDB = "dbtest/APIS_{0}.sqlite".format(d.strftime("%Y%m%d_%H%M%S"))
    logging.basicConfig(filename='{0}.log'.format(d.strftime("%Y%m%d_%H%M%S")),level=logging.DEBUG)

    apis = ApisSpatialite(targetDB)

    # Add Spatial Reference Tables: OSM Boundaries, Katastralgemeinden from SHP
    apis.AddTableJson("config/katastralgemeinden.json")
    apis.AddTableJson("config/osm_boundaries.json")

    # Add all independen Tables
    apis.AddTableJson("config/hersteller.json")
    apis.AddTableJson("config/projekt.json")
    apis.AddTableJson("config/copyright.json")
    apis.AddTableJson("config/kamera.json")
    apis.AddTableJson("config/film_fabrikat.json")
    apis.AddTableJson("config/target.json")
    apis.AddTableJson("config/wetter.json")
    apis.AddTableJson("config/fundart.json")
    apis.AddTableJson("config/kultur.json")
    apis.AddTableJson("config/phase.json")
    apis.AddTableJson("config/zeit.json")
    apis.AddTableJson("config/fundgewinnung.json")
    apis.AddTableJson("config/fundgewinnung_quelle.json")
    apis.AddTableJson("config/datierung_quelle.json")

    apis.AddTableJson("config/begehung.json")
    apis.AddTableJson("config/begehung_zustand.json")
    apis.AddTableJson("config/begehung_begehtyp.json")

    apis.AddTableJson("config/film.json")

    apis.AddTableJson("config/luftbild_schraeg_cp.json")
    apis.AddTableJson("config/luftbild_schraeg_fp.json")

    apis.AddTableJson("config/luftbild_senk_cp.json")
    apis.AddTableJson("config/luftbild_senk_fp.json")

    apis.AddTableJson("config/fundort_pnt.json")
    apis.AddTableJson("config/fundort_pol.json")
    apis.AddTableJson("config/fundort_interpretation.json")

    apis.AddTableJson("config/fundstelle_pnt.json")
    apis.AddTableJson("config/fundstelle_pol.json")

    apis.AddTableJson("config/fundort_log_pnt.json")
    apis.AddTableJson("config/fundort_log_pol.json")
    apis.AddTableJson("config/fundstelle_log_pnt.json")
    apis.AddTableJson("config/fundstelle_log_pol.json")

    apis.RunSqlUpdates("config/sqlupdates.json")
    #apis.RunSqlUpdates("config/sqlupdates_test.json")

    apis.generateMissingSitePolygons()
    apis.generateMissingFindSpotPolygons()

    apis.CleanUp()