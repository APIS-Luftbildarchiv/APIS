# -*- coding: utf-8 -*-
import os.path
import json

from PyQt4.QtCore import Qt, QSettings
from PyQt4.QtGui  import QMessageBox
from qgis.core import QgsProject, QgsDataSourceURI, QgsVectorLayer, QgsMapLayerRegistry, QgsLayerTree, QgsCoordinateReferenceSystem


class ApisLayerManager:
    def __init__(self, pluginDir, iface, dbm):
        self.layerTreeConfigFile = pluginDir + "\\layer_tree\\apis_layer_tree_config.json"
        self.stylesDir = pluginDir + "\\layer_tree\\styles\\"
        self.iface = iface
        self.dbm = dbm

        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)
        if self.settings.value("APIS/disable_site_and_findspot", "0") != "1":
            self.version = 2
        else:
            self.version = 1

        self.isLoaded = False

        self.tocRoot = QgsProject.instance().layerTreeRoot()

        self._imageObliqueCPLayer = None
        self._imageObliqueFPLayer = None
        self._imageObliqueCPLayerId = None
        self._imageObliqueFPLayerId = None

        self._imageVerticalCPLayer = None
        self._imageVerticalFPLayer = None
        self._imageVerticalCPLayerId = None
        self._imageVerticalFPLayerId = None

        self._siteLayer = None
        self._findSpotLayer = None
        self._siteLayerId = None
        self._findSpotLayerId = None


        self._loadApisLayerTreeConfig()


    def _loadApisLayerTreeConfig(self):
        if os.path.isfile(self.layerTreeConfigFile):
            with open(self.layerTreeConfigFile, 'rU') as lT:
                layerTreeConfig = json.load(lT)
                self.__layers = layerTreeConfig["layers"]
                self.__groups = layerTreeConfig["groups"]
                self.__groupsOrder = layerTreeConfig["groups_order"]
                self.isLoaded = True
        else:
            self.isLoaded = False

    def loadDefaultLayerTree(self):
        if self.isLoaded:
            self._loadDefaultApisLayers()

            # return
            #
            # uri = QgsDataSourceURI()
            # uri.setDatabase(self.dbm.db.databaseName())
            #
            # for layer in self.__layers:
            #     if "default" in self.__layers[layer] and self.__layers[layer]["default"]:
            #         #QMessageBox.information(None, "LayerTree", "LoadLayerTree {0}".format(len(self.__layers)))
            #         groupName = self.__groups[self.__layers[layer]["group"]]
            #         if not self.tocRoot.findGroup(groupName):
            #             idx = 0
            #             orderIdx = self.__groupsOrder.index(self.__layers[layer]["group"])
            #             for child in self.tocRoot.children():
            #                 if QgsLayerTree.isGroup(child):
            #                     i = self.__groupsOrder.index(self.__layers[layer]["group"])
            #
            #                     #idx = min(groupCount, )
            #             QMessageBox.information(None, "Sources", u"{0}, {1}".format(groupName, idx))
            #             g = self.tocRoot.insertGroup(idx, groupName)
            #             g.setCustomProperty("apis_group_id", self.__layers[layer]["group"])
            #
            #         group = self.tocRoot.findGroup(groupName)
            #
            #         #layersInGroup = group.findLayers()
            #         layerNamesInGroup = [layerInGroup.layerName() for layerInGroup in group.findLayers()]
            #
            #         if self.__layers[layer]["display_name"] not in layerNamesInGroup:
            #             uri.setDataSource('', self.__layers[layer]["name"], 'geometry')
            #             vectorLayer = QgsVectorLayer(uri.uri(), self.__layers[layer]["display_name"], 'spatialite')
            #             vectorLayer.loadNamedStyle(self.stylesDir + self.__layers[layer]["style"])
            #             QgsMapLayerRegistry.instance().addMapLayer(vectorLayer, False)
            #             group.insertLayer(0, vectorLayer)
            #             prfx = "dbname='"
            #             dSU = vectorLayer.dataProvider().dataSourceUri()
            #             ext = ".sqlite"
            #             dbPath = dSU[dSU.find(prfx) + len(prfx):dSU.find(ext) + len(ext)]
            #             #QMessageBox.information(None, "Sources", u"{0}, {1}".format(os.path.normpath(dbPath), os.path.normpath(self.dbm.db.databaseName())))


    # def _loadApisLayerGroups(self):
    #     #self.tocRoot = QgsProject.instance().layerTreeRoot()
    #     for groupId in self.__groups:
    #         groupName = self.__groups[groupId]["display_name"]
    #         self._addGroupIfMissing(groupName)

    def requestSiteLayer(self):
        groupName = self.__groups[self.__layers["sites"]["group"]]["display_name"]
        group = self._addGroupIfMissing(groupName)

        stylePath = self.stylesDir + self.__layers["sites"]["style"]
        layer = self.requestSpatialiteTable(self.dbm.db.databaseName(), self.__layers["sites"]["name"],
                                    self.__layers["sites"]["display_name"], groupName, None, True, True, stylePath)

        return layer

    def requestFindSpotLayer(self):
        groupName = self.__groups[self.__layers["find_spots"]["group"]]["display_name"]
        group = self._addGroupIfMissing(groupName)

        stylePath = self.stylesDir + self.__layers["find_spots"]["style"]
        layer = self.requestSpatialiteTable(self.dbm.db.databaseName(), self.__layers["find_spots"]["name"],
                                    self.__layers["find_spots"]["display_name"], groupName, None, True, True, stylePath)

        return layer

    def _getPosOfPrevGroup(self, groupName):
        topLevelGroups = [child.name() for child in self.tocRoot.children() if QgsLayerTree.isGroup(child)]
        if groupName in topLevelGroups:
            return topLevelGroups.index(groupName)
        else:
            return None

    def _loadDefaultApisLayers(self):
        for layer in self.__layers:
            if "default" in self.__layers[layer] and self.__layers[layer]["default"] <= self.version:
                # QMessageBox.information(None, "LayerTree", "LoadLayerTree {0}".format(len(self.__layers)))
                groupName = self.__groups[self.__layers[layer]["group"]]["display_name"]
                group = self._addGroupIfMissing(groupName)

                stylePath = self.stylesDir + self.__layers[layer]["style"]
                self.requestSpatialiteTable(self.dbm.db.databaseName(), self.__layers[layer]["name"], self.__layers[layer]["display_name"], groupName, None, True, True, stylePath)


    def _isApisGroupName(self, groupName):
        apisGroupNames = [self.__groups[groupId]["display_name"] for groupId in self.__groups]
        return groupName in apisGroupNames

    def _getApisGroupId(self, groupName):
        groupId = None
        for groupId in self.__groups:
            if groupName == self.__groups[groupId]["display_name"]:
                return groupId
        return groupId

    def _addApisGroup(self, groupName):
        group = self.tocRoot.findGroup(groupName)
        if not group:
            groupId = self._getApisGroupId(groupName)
            posAfterId = self.__groups[groupId]["pos_after"]
            if posAfterId == 0 or posAfterId not in self.__groups or posAfterId == groupId:
                group = self.tocRoot.insertGroup(0, groupName)
                return group
            else:
                foundPrevGroup = False
                while not foundPrevGroup:
                    prevGroupName = self.__groups[posAfterId]["display_name"]
                    if self.tocRoot.findGroup(prevGroupName):
                        idx = self._getPosOfPrevGroup(prevGroupName)
                        idx += 1
                        group = self.tocRoot.insertGroup(idx, groupName)
                        foundPrevGroup = True
                        return group
                    else:
                        posAfterId = self.__groups[posAfterId]["pos_after"]
                        if posAfterId == 0:
                            group = self.tocRoot.insertGroup(0, groupName)
                            foundPrevGroup = True
                            return group
        else:
            return group

    def _addGroupIfMissing(self, groupName):
        group = self.tocRoot.findGroup(groupName)
        if not group:
            if self._isApisGroupName(groupName):
                group = self._addApisGroup(groupName)
            else:
                group = self.tocRoot.insertGroup(0, groupName)
            return group
        else:
            return group

    def addLayerToCanvas(self, layer, groupName=None):
        try:
            ret = QgsMapLayerRegistry.instance().addMapLayer(layer, False)
            if ret:
                if groupName:
                    group = self._addGroupIfMissing(groupName)
                    group.insertLayer(0, layer)
                else:
                    self.tocRoot.insertLayer(0, layer)
                return True
            else:
                return False
        except:
            return False

    def _loadSpaitaliteTable(self, databaseName, tableName, displayName=None, subsetString=None):
        try:
            if not displayName:
                displayName = tableName

            uri = QgsDataSourceURI()
            uri.setDatabase(databaseName)
            uri.setDataSource('', tableName, 'geometry')
            layer = QgsVectorLayer(uri.uri(), displayName, 'spatialite')
            if subsetString:
                layer.setSubsetString(subsetString)

            return layer
        except Exception, e:
            QMessageBox.warning(None, "Error Loading Spatialtie Table", u"{0}".format(e))
            return None

    # def _addSpatialiteLayerToCanvas(self, layer, groupName=None):
    #     ret = QgsMapLayerRegistry.instance().addMapLayer(layer, False)

    # def requestSiteLayer(self, addToCanvas=False):
    #     siteLayer = self._requestApisLayer(self._siteLayer, self._siteLayerId, 'fundort', addToCanvas)
    #     return siteLayer
    #
    # def _requestApisLayer(self, apisLayer, apisLayerId, layerName, addToCanvas=False):
    #     # Is site Layer in Canvas
    #     layerNamesInGroup = [layerInGroup.layerName() for layerInGroup in self.tocRoot.findLayers()]
    #
    #     # if apisLayer:
    #     #     return apisLayer
    #     # else:
    #     #     self._siteLayer = self.loadSpatialiteLayer()
    #     #
    #     # if apisLayer and addToCanvas:
    #     #     self._addSpatialiteLayerToCanvas(apisLayer)
    #     #
    #     # return apisLayer

    def requestSpatialiteTable(self, databaseName, tableName, displayName=None, groupName=None, subsetString=None, useLayerFromTree=True, addToCanvas=False, stylePath=None):
        try:
            if not displayName:
                displayName = tableName

            if useLayerFromTree:
                layer = self.findSpatialiteLayerInTree(databaseName, tableName)

            if layer is None:
                layer = self._loadSpaitaliteTable(databaseName, tableName, displayName, subsetString)

                if addToCanvas:
                    if stylePath:
                        layer.loadNamedStyle(stylePath)
                    self.addLayerToCanvas(layer, groupName)
            return layer
        except Exception as e:
            QMessageBox.warning(None, "Error Requesting Spatialtie Table", u"{0}".format(e))
            return None

    def requestShapeFile(self, shapeFilePath, epsg=None, layerName=None, groupName=None, useLayerFromTree=True, addToCanvas=False):
        try:
            #QMessageBox.information(None, "Info", "LOAD SHP")
            layer = None
            if not layerName:
                layerName = os.path.basename(shapeFilePath)
                root, ext = os.path.splitext(layerName)
                if ext == '.shp':
                    layerName = root

            if useLayerFromTree:
                layer = self.findShapeFileLayerInTree(shapeFilePath)

            if layer is None:
                layer = QgsVectorLayer(shapeFilePath, layerName, "ogr")
                if epsg != None:
                    layer.setCrs(QgsCoordinateReferenceSystem(epsg, QgsCoordinateReferenceSystem.EpsgCrsId))

                if addToCanvas:
                    self.addLayerToCanvas(layer, groupName)

            return layer
        except Exception as e:
            QMessageBox.warning(None, "Error Loading Shape File", u"{0}".format(e))
            return None

    def findShapeFileLayerInTree(self, layerUri):
        for treeLayer in self.tocRoot.findLayers():
            if treeLayer.layer().type() == 0: # 0 ... VectorLayer
                dSU = treeLayer.layer().dataProvider().dataSourceUri()
                if  os.path.normpath(dSU[:dSU.find(u"|")]) == os.path.normpath(layerUri):
                    return treeLayer.layer()

        return None

    def findSpatialiteLayerInTree(self, databaseUri, tableName):
        for treeLayer in self.tocRoot.findLayers():
            if treeLayer.layer().type() == 0:  # 0 ... VectorLayer
                dSU = treeLayer.layer().dataProvider().dataSourceUri()
                prfxDatabase = "dbname='"
                ext = ".sqlite"
                prfxTable = "table=\""
                sufxTable = "\" ("
                dSU_databaseUri = dSU[dSU.find(prfxDatabase) + len(prfxDatabase):dSU.find(ext) + len(ext)]
                dSU_tableName = dSU[dSU.find(prfxTable) + len(prfxTable):dSU.find(sufxTable)]
                # QMessageBox.information(None, "Sources", u"{0}, {1}".format(os.path.normpath(dbPath), os.path.normpath(self.dbm.db.databaseName())))
                #if os.path.normpath(dSU[:dSU.find(u"|")]) == os.path.normpath(layerUri):
                if os.path.normpath(dSU_databaseUri) == os.path.normpath(databaseUri) and dSU_tableName == tableName:
                    return treeLayer.layer()

        return None

    def getStylesDir(self):
        return self.stylesDir