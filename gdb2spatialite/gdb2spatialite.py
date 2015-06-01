 # -*- coding: utf-8 -*-

import os, sys
from osgeo import ogr
from pyspatialite import dbapi2 as db
import json
from datetime import datetime
from pprint import pprint

class Apis:

    def __init__(self, gdbPath, spatialitePath, obsoletTablesPath, obsoletFieldsPath, updateTablesFieldsPath, newFieldsPath, newTablesPath):

        # GeoDBs
        self.OpenGdb(gdbPath) # creates self.gdb 
        self.InitSpatialite(spatialitePath) # creates self.slconn, self.slcur
        
        # Json Files
        with open(obsoletTablesPath,'rU') as obsoletTablesFile:    
            data = json.load(obsoletTablesFile)
            self.obsoletTables = data['obsolet_tables']

        with open(obsoletFieldsPath,'rU') as obsoletFieldsFile:    
            self.obsoletFields = json.load(obsoletFieldsFile)

        with open(updateTablesFieldsPath,'rU') as updateTablesFieldsFile:    
            self.updateTablesFields = json.load(updateTablesFieldsFile)

        with open(newFieldsPath,'rU') as newFieldsFile:    
            self.newFields = json.load(newFieldsFile) 

        with open(newTablesPath,'rU') as newTablesFile:    
            self.newTables = json.load(newTablesFile) 

        self.ogr2spatialite = {
            0: "GEOMETRY",
            1: "POINT",
            2: "LINESTRING",
            3: "POLYGON",
            4: "MULTIPOINT",
            5: "MULTILINESTRING",
            6: "MULTIPOLYGON"
        }

        self.convertionDict = {
        "Integer": "INTEGER",
        "String": "TEXT",
        "Real": "REAL",
        "DateTime": "DATETIME"
    
    }

    def OpenGdb(self, gdbPath):
        ogr.UseExceptions()
        driver = ogr.GetDriverByName("OpenFileGDB")
        
        try: 
            self.gdb = driver.Open(gdbPath, 0)
            print "> Opening FileGDB"
        except Exception, e:
            print "> Error Opening FileGDB ", e
            sys.exit()

    def InitSpatialite(self, spatialitePath):
        try:
            os.remove(spatialitePath)
        except:
            pass
            
        try:
             # creating/connecting the spatialite db
            self.slconn = db.connect(spatialitePath)
            print "> Creating Spatialite"

            # creating a Cursor
            self.slcur = self.slconn.cursor()

            # testing library versions
            rs = self.slcur.execute('SELECT sqlite_version(), spatialite_version()')
            for row in rs:
                msg = "> SQLite v{0} Spatialite v{1}".format(row[0], row[1])
                print msg

            # initializing Spatial MetaData
            # using v.2.4.0 this will automatically create
            # GEOMETRY_COLUMNS and SPATIAL_REF_SYS
            sql = 'SELECT InitSpatialMetadata(1)'
            self.slcur.execute(sql)
            print "> InitSpatialMetadata"
        except OSError, e:
            print "> Error Creating Spatialite", e
            sys.exit(1)

    def GetNewTableName(self, currentName):
        newTableName = currentName

        for table in self.updateTablesFields:
            if table['name'] == currentName and 'rename' in table:
                newTableName = table['rename']

        return newTableName

    def GetNewFieldName(self, tableName, currentName):
        newFieldName = currentName

        for table in self.updateTablesFields:
            if table['name'] == tableName and 'fields' in table:
                for field in table['fields']:
                    if field['name'] == currentName and 'rename' in field:
                        newFieldName = field['rename']

        return newFieldName

    def GetNewFieldType(self, tableName, currentName, currentType):
        newFieldType = currentType

        for table in self.updateTablesFields:
            if table['name'] == tableName and 'fields' in table:
                for field in table['fields']:
                    if field['name'] == currentName and 'type' in field and 'typecast' in field:
                        newFieldType = field['typecast']

        return newFieldType

    def DoTypeCast(self, value, fromType, toType):
        if fromType == 'String' and toType == 'DateTime':
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
                    r = ''
            return r

    def GetContentConversion(self, tableName, fieldName, currentValue):
        newValue = currentValue

        for table in self.updateTablesFields:
            if table['name'] == tableName and 'fields' in table:
                for field in table['fields']:
                    if field['name'] == fieldName and 'contentconversion' in field and 'contentdefault' in field:
                        newValue = field['contentdefault']
                        for conversion in field['contentconversion']:
                            if conversion['old'] == currentValue:
                                newValue = conversion['new']
        return newValue


    def LoadFileGdb(self):
        '''
        reads ESRI GDB and extracts Structure (Tables, Fields, Types, ...) of DB to List/Dict
        '''
        #featureClassList contains GeoData and Tables without Geometry
        print "> Load FileGDB"
        self.gdbStructure = []
        
        if self.gdb:
            for fc in self.gdb:
                if fc.GetName() not in self.obsoletTables:
                    tableStructure = {}
                    srs = fc.GetSpatialRef()
                    if srs:
                        if srs.IsGeographic() == 1:  # this is a geographic srs
                            cstype = 'GEOGCS'
                        else:  # this is a projected srs
                            cstype = 'PROJCS'
                        tableStructure['epsg'] = srs.GetAuthorityCode(cstype)
                        #print srs.GetAuthorityName(cstype), srs.GetAuthorityCode(cstype), fc.GetName(), ogr.GeometryTypeToName(fc.GetGeomType())
                    #else:
                        #print ogr.GeometryTypeToName(fc.GetGeomType()), fc.GetName()
                    
                    #print fc.GetName(), fc.GetGeomType(), ogr.GeometryTypeToName(fc.GetGeomType())
                    tableStructure['name'] = fc.GetName()
                    tableStructure['type'] = fc.GetGeomType()
                    tableStructure['typeName'] = ogr.GeometryTypeToName(fc.GetGeomType())
                    tableStructure['fields'] = []
                    
                    fields = fc.GetLayerDefn()
                    for i in range(fields.GetFieldCount()):
                        field = fields.GetFieldDefn(i)
                        if fc.GetName() in self.obsoletFields and field.GetNameRef() in self.obsoletFields[fc.GetName()]:
                            continue
                        fieldStructure = {}
                        fieldStructure['name'] = field.GetNameRef()
                        fieldStructure['type'] = field.GetFieldTypeName(field.GetType())
                        tableStructure['fields'].append(fieldStructure)
                        
                    self.gdbStructure.append(tableStructure)
        
    def WriteConfigFile(self, configPath):
        '''
        Writes GDB Structure to JSON File
        '''
        if self.gdbStructure and len(self.gdbStructure) > 0:
            with open(configPath, 'w') as configFile:
                json.dump(self.gdbStructure, configFile)
        print "> Write Config to JSON"

    def CreateSpatialiteTablesFromStructure(self): 
        # iterate over structure and create tables in spatialite db
        print "> Create Spatialite"
        for table in self.gdbStructure:
            newTableName = self.GetNewTableName(table['name'])
            sql = "DROP TABLE IF EXISTS {0}".format(newTableName)
            self.slcur.execute(sql)
            sql = "CREATE TABLE {0} ".format(newTableName)
            sql += "("
            fieldCount = 0
            for field in table['fields']:
                fieldCount += 1
                sql += "{0} {1}".format(self.GetNewFieldName(table['name'], field['name']), self.convertionDict[self.GetNewFieldType(table['name'], field['name'], field['type'])])
                if fieldCount < len(table['fields']):
                    sql += ", "
            sql += ")"
            self.slcur.execute(sql)

            if table['type'] != 100:
                #print newTableName, int(table['epsg'])
                # creating a POINT Geometry column
                sql = "SELECT AddGeometryColumn(?, 'geom', ?, ?, 'XY')"
                # sql += "'geom', {0}, '{1}', 'XY')".format(table['epsg'], self.ogr2spatialite[table['type']])
                self.slcur.execute(sql, (newTableName, 4312, self.ogr2spatialite[table['type']])) #int(table['epsg'])


            # fill table
            print "> Fill Tables Spatialite: {0}".format(newTableName)
            #if table['type'] == 100:
            # INSERT INTO ...
            layer = self.gdb.GetLayerByName(table['name'].encode("utf-8"))

            #print layer.GetName(), layer.GetFeatureCount()
            if not layer:
                sys.exit("ERROR: can not find layer '{0}' in GeoDB".format(table['name'].encode("utf-8")))

            placeholder = ','.join(map(unicode, ['?' for i in range(len(table['fields']))]))
            if table['type'] != 100:
               placeholder += ',GeomFromText(?, ?)'
            sql = "INSERT INTO {0} VALUES({1})".format(newTableName, placeholder)
            #print sql
            layer.ResetReading()
            rows = []
            for feature in layer:
                r = []
                for field in table['fields']:
                    #print 
                    #ff = unicode(feature.GetField(field['name']))
                    #if type(ff) is unicode:
                    #    ff.encode("utf-8")

                    if feature.GetFieldType(field['name']) == ogr.OFTInteger:
                        v = feature.GetFieldAsInteger(field['name'])

                    elif feature.GetFieldType(field['name']) == ogr.OFTReal:    
                        v = feature.GetFieldAsDouble(field['name'])

                    elif feature.GetFieldType(field['name']) == ogr.OFTString:
                        ffs = feature.GetFieldAsString(field['name'])
                        v = ffs.decode('utf-8')

                    elif feature.GetFieldType(field['name']) == ogr.OFTDateTime:
                        v = feature.GetFieldAsString(field['name'])


                    newType = self.GetNewFieldType(table['name'], field['name'], field['type'])
                    if field['type'] != newType:
                        v = self.DoTypeCast(v, field['type'], newType)

                    v = self.GetContentConversion(table['name'], field['name'], v)

                    r.append(v)

                #add geometry
                if table['type'] != 100:
                    gm = feature.GetGeometryRef()
                    r.append(gm.ExportToWkt())
                    r.append(4312) #int(table['epsg'])))

                #pprint(r)
                #self.slcur.execute(sql, r)
                rows.append(r)
                    
            #pprint(sql)
            #pprint(rows)
            self.slcur.executemany(sql, rows)

            #Add new Cols
            for newFields in self.newFields:
                if newFields['name'] == newTableName and 'fields' in newFields:
                    for newField in newFields['fields']:
                        sql = "ALTER TABLE {0} ADD COLUMN {1} {2}".format(newTableName, newField['name'], self.convertionDict[newField['type']])
                        self.slcur.execute(sql)

            self.slconn.commit()

    def AddNewSpatialiteTablesFromJson(self):
        print "> Add new Tables Spatialite"
        for newTable in self.newTables:
            sql = "DROP TABLE IF EXISTS {0}".format(newTable['name'])
            self.slcur.execute(sql)
            sql = "CREATE TABLE {0} ".format(newTable['name'])
            sql += "("
            fieldCount = 0
            for field in newTable['fields']:
                fieldCount += 1
                sql += "{0} {1}".format(field['name'], self.convertionDict[field['type']])
                if fieldCount < len(newTable['fields']):
                    sql += ", "
            sql += ")"
            self.slcur.execute(sql)

            if newTable['type'] != 100:
                # creating a POINT Geometry column
                sql = "SELECT AddGeometryColumn('{0}',".format(newTable['name'])
                sql += "'geom', {0}, '{1}', 'XY')".format(4312, self.ogr2spatialite[newTable['type']])
                self.slcur.execute(sql)
            #self.slconn.commit()

            # Fill Table
            print "> Fill new Tables Spatialite"

            if 'data' in newTable:
                sql = "INSERT INTO {0} VALUES ({1})".format(newTable['name'], ','.join(map(unicode, ['?' for i in range(len(newTable['fields']))])))
                rows = []
                for row in newTable['data']:
                    r = ()
                    for field in newTable['fields']:
                        r += (row[field['name']],)
                    rows.append(r) 
                #pprint(rows)        
                    
                self.slcur.executemany(sql, rows)

            if 'populate' in newTable:
                if newTable['populatemode'] == "aggregate":
                    rows = []
                    for dataset in newTable['populate']: 
                        row = []  
                        for field in newTable['fields']:
                            # print field['name'], dataset[field['name']]
                            if isinstance(dataset[field['name']], dict):
                                if 'table' in dataset[field['name']] and 'attr' in dataset[field['name']]:
                                    #print dataset[field['name']]['table'], dataset[field['name']]['attr']
                                    layer = self.gdb.GetLayerByName(dataset[field['name']]['table'].encode("utf-8"))
                                    # print layer.GetFeatureCount()
                                    if not layer:
                                        sys.exit("ERROR: can not find layer '{0}' in GeoDB".format(dataset[field['name']]['table'].encode("utf-8")))
                                    layer.ResetReading()
                                    r = []
                                    for feature in layer:
                                        # FIXME was passiert mit nicht strings
                                        r.append(str(feature.GetField(dataset[field['name']]['attr'].encode("utf-8"))).decode("utf-8"))
                                        #print dataset[field['name']]['attr'], str(feature.GetField(dataset[field['name']]['attr'].encode("utf-8"))).decode("utf-8")
                                        #geom = feature.GetGeometryRef()
                                        #print geom.Centroid().ExportToWkt()
                                    row.append(r)
                            elif dataset[field['name']] == "None":
                                row.append('')
                            else: # value
                                row.append(dataset[field['name']])
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
                        results += result

                    
                    sql = "INSERT INTO {0} VALUES ({1})".format(newTable['name'], ','.join(map(unicode, ['?' for i in range(len(newTable['fields']))])))
                    self.slcur.executemany(sql, results)

                # FIXME implement unique mode         
                elif newTable['populatemode'] == "unique":
                    pass
            self.slconn.commit()
        
    def CleanUp(self):
        print "> CleanUp and finish script"
        del self.gdb
        self.slcur.close()
        self.slconn.close()

    def Run(self):
        self.LoadFileGdb() # creates self.gdbStructure
        self.WriteConfigFile('config/apis_db_config.json')

        self.CreateSpatialiteTablesFromStructure()
        self.AddNewSpatialiteTablesFromJson()
        self.CleanUp()

if __name__ == '__main__':
    d = datetime.today()

    apis = Apis(
        "geodbs/APIS.gdb", # Path to current APIS ESRI GDB
        "geodbs/APIS_{0}.sqlite".format(d.strftime("%Y%m%d_%H%M%S")), # PAth to new (not yet existing) APIS Spatialite DB
        "config/apis_db_obsolet_tables.json",
        "config/apis_db_obsolet_fields_now.json",
        "config/apis_db_update_tables_and_fields.json",
        "config/apis_db_new_fields.json",
        "config/apis_db_new_tables.json"
        )
    apis.Run()