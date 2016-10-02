# -*- coding: utf-8 -*

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from PyQt4.QtXml import *

from qgis.core import *
from qgis.gui import QgsMessageBar

from apis_utils import OpenFileOrFolder

from PyPDF2 import PdfFileMerger, PdfFileReader

from py_tiled_layer.tilelayer import TileLayer, TileLayerType
from py_tiled_layer.tiles import TileServiceInfo, BoundingBox #TileLayerDefinition

import os, sys, subprocess
import math


def MergePdfFiles(targetFileName, fileNames, deleteWhenDone=True):
    merger = PdfFileMerger()
    for fileName in fileNames:
        merger.append(PdfFileReader(file(fileName, 'rb')))
    merger.write(targetFileName)

    if deleteWhenDone:
        for fileName in fileNames:
            try:
                os.remove(fileName)
            except Exception, e:
                continue


class ApisPrinter():
    PORTRAIT, LANDSCAPE = range(2)
    def __init__(self, parent, dbm, imageRegistry, openFile=False, isTemp=False, fileName=None, format=0, r=300):
        self.parent = parent
        self.iface = parent.iface
        self.dbm = dbm
        self.imageRegistry = imageRegistry
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)
        self.openFile = openFile
        self.isTemp = isTemp
        self.format = format
        self.resolution = r
        self.fileName = fileName
        self.query = None
        self.info = None

        self._setupComposition()

    def setQuery(self, query):
        self.query = query

    def _setupComposition(self):
        self.ms = QgsMapSettings()
        self.comp = QgsComposition(self.ms)
        self.comp.setPlotStyle(QgsComposition.Print)
        self.comp.setPrintResolution(self.resolution)
        w = 210.0
        h = 297.0
        if self.format == self.PORTRAIT:
            self.comp.setPaperSize(w, h)
            self.pageBreak = 40
        else:
            self.comp.setPaperSize(h, w)
            self.pageBreak = 25

    def _export(self):
        if self.fileName:
            self.comp.exportAsPDF(self.fileName)
            self._openFile()

    def _openFile(self):
        if self.openFile and self.fileName and os.path.isfile(self.fileName):
            OpenFileOrFolder(self.fileName)

    def _setFileName(self, fileName, dialogTitle='Speichern', date=True):
        if date:
            dt = "_" + QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")
        else:
            dt = ""
        saveDir = self.settings.value("APIS/working_dir", QDir.home().dirName())
        self.fileName = QFileDialog.getSaveFileName(self.parent, dialogTitle, saveDir + "\\" + '{0}{1}'.format(fileName, dt), '*.pdf')

        if not self.fileName:
            self.fileName = None


    def _mergePdfs(self, targetFileName, fileNameList):
        merger = PdfFileMerger()
        for fileName in fileNameList:
            merger.append(PdfFileReader(file(fileName, 'rb')))

        merger.write(targetFileName)

        for fileName in fileNameList:
            try:
                os.remove(fileName)
            except Exception, e:
                continue

class ApisSitePrinter(ApisPrinter):

    def setStylesDir(self, stylesDir):
        self.stylesDir = stylesDir

    def exportSiteDetailsPdf(self, siteList, targetFileOrFolder, timeStamp, isTemp=False):

        query = QSqlQuery(self.dbm.db)
        query.prepare(u"SELECT * FROM fundort WHERE fundortnummer IN ({0})".format((u",".join(u"'{0}'".format(site) for site in siteList))))
        query.exec_()

        query.seek(-1)
        sitePdfs = []
        while query.next():
            siteDict = {}
            rec = query.record()
            for col in range(rec.count()-1): # -1 geometry wird nicht benötigt!
                val = u"{0}".format(rec.value(col))
                if val.replace(" ", "") == '' or val == 'NULL':
                    val = u"---"
                siteDict[unicode(rec.fieldName(col))] = val

            siteDict['datum_druck'] = QDate.currentDate().toString("dd.MM.yyyy")
            siteDict['datum_ersteintrag'] = QDate.fromString(siteDict['datum_ersteintrag'], "yyyy-MM-dd").toString("dd.MM.yyyy")
            siteDict['datum_aenderung'] = QDate.fromString(siteDict['datum_aenderung'], "yyyy-MM-dd").toString("dd.MM.yyyy")


            if siteDict['sicherheit'] == u"1":
                siteDict['sicherheit'] = u"sicher"
            elif siteDict['sicherheit'] == u"2":
                siteDict['sicherheit'] = u"wahrscheinlich"
            elif siteDict['sicherheit'] == u"3":
                siteDict['sicherheit'] = u"fraglich"
            elif siteDict['sicherheit'] == u"4":
                siteDict['sicherheit'] = u"kein Fundort"

            if siteDict['meridian'] == u"28":
                siteDict['epsg_gk'] = u"31254"
            elif siteDict['meridian'] == u"31":
                siteDict['epsg_gk'] = u"31255"
            elif siteDict['meridian'] == u"34":
                siteDict['epsg_gk'] = u"31256"
            else:
                siteDict['epsg_gk'] = u"---"

            siteDict['epsg_mgi'] = u"4312"

            query2 = QSqlQuery(self.dbm.db)
            query2.prepare(u"SELECT kg.katastralgemeindenummer as kgcode, kg.katastralgemeindename as kgname, round(100*Area(Intersection(Transform(fo.geometry, 31287), kg.geometry))/Area(Transform(fo.geometry, 31287))) as percent FROM katastralgemeinden kg, fundort fo WHERE fundortnummer = '{0}' AND intersects(Transform(fo.geometry, 31287), kg.geometry) AND kg.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'katastralgemeinden' AND search_frame = Transform(fo.geometry, 31287)) ORDER  BY percent DESC".format(siteDict['fundortnummer']))
            query2.exec_()
            query2.seek(-1)
            val = u""
            while query2.next():
                rec2 = query2.record()
                val += u"{0} {1} ({2} %)\n".format(rec2.value(0), rec2.value(1), rec2.value(2))

            siteDict['kgs_lage'] = val
            #QMessageBox.information(None, "KGS", val)

            # MapSettings
            mapSettings = QgsMapSettings()
            mapSettings.setCrsTransformEnabled(True)
            mapSettings.setDestinationCrs(QgsCoordinateReferenceSystem(3416, QgsCoordinateReferenceSystem.EpsgCrsId))

            mapSettings.setMapUnits(QGis.UnitType(0))
            mapSettings.setOutputDpi(300)

            layerSet = []
            # Site Layer
            siteLayer = self.getSpatialiteLayer(u"fundort", u'"fundortnummer" = "{0}"'.format(siteDict['fundortnummer']), u"fundort")
            siteLayer.setCrs(QgsCoordinateReferenceSystem(4312, QgsCoordinateReferenceSystem.EpsgCrsId))
            siteLayer.setCoordinateSystem()

            siteLayer.loadNamedStyle(os.path.join(self.stylesDir, u"fundort_print.qml"))
            #siteLayer.setRendererV2(self.getSiteRenderer())

            QgsMapLayerRegistry.instance().addMapLayer(siteLayer, False)  # False = don't add to Layers (TOC)
            layerSet.append(siteLayer.id())
            extent = mapSettings.layerExtentToOutputExtent(siteLayer, siteLayer.extent())

            scaleVal = max(extent.width(), extent.height())
            baseVal = max(5000.0, scaleVal*1.1)
            #QMessageBox.information(None, "MAP", "w: {0}, h: {1}".format(extent.width(), extent.height()))
            extent.scale(baseVal/scaleVal)
            #QMessageBox.information(None, "MAP", "w: {0}, h: {1}".format(extent.width(), extent.height()))
            mapWidth = 94.0
            mapHeight = 70.0
            if (extent.width()/extent.height()) > (mapWidth/mapHeight):
                newHeight = extent.width() * mapHeight / mapWidth
                yMin = extent.center().y() - (newHeight / 2.0)
                yMax = extent.center().y() + (newHeight / 2.0)
                newRect = QgsRectangle(extent.xMinimum(), yMin, extent.xMaximum(), yMax)
                extent.combineExtentWith(newRect)
            elif (extent.width()/extent.height()) < (mapWidth/mapHeight):
                newWidth = extent.height() * mapWidth / mapHeight
                xMin = extent.center().x() - (newWidth / 2.0)
                xMax = extent.center().x() + (newWidth / 2.0)
                newRect = QgsRectangle(xMin, extent.yMinimum(), xMax, extent.yMaximum())
                extent.combineExtentWith(newRect)

            # ÖK Background
            oekLayer28 = QgsRasterLayer(self.settings.value("APIS/oek50_gk_qgis_m28"), u"OKM28")
            oekLayer28.setCrs(QgsCoordinateReferenceSystem(31254, QgsCoordinateReferenceSystem.EpsgCrsId))
            QgsMapLayerRegistry.instance().addMapLayer(oekLayer28, False)
            oekLayer28.setExtent(mapSettings.mapToLayerCoordinates(oekLayer28, extent))

            oekLayer31 = QgsRasterLayer(self.settings.value("APIS/oek50_gk_qgis_m31"), u"OKM31")
            oekLayer31.setCrs(QgsCoordinateReferenceSystem(31255, QgsCoordinateReferenceSystem.EpsgCrsId))
            QgsMapLayerRegistry.instance().addMapLayer(oekLayer31, False)
            oekLayer31.setExtent(mapSettings.mapToLayerCoordinates(oekLayer31, extent))

            oekLayer34 = QgsRasterLayer(self.settings.value("APIS/oek50_gk_qgis_m34"), u"OKM34")
            oekLayer34.setCrs(QgsCoordinateReferenceSystem(31256, QgsCoordinateReferenceSystem.EpsgCrsId))
            QgsMapLayerRegistry.instance().addMapLayer(oekLayer34, False)
            oekLayer34.setExtent(mapSettings.mapToLayerCoordinates(oekLayer34, extent))

            layerSet.append(oekLayer28.id())
            layerSet.append(oekLayer31.id())
            layerSet.append(oekLayer34.id())

            # import math
            # mapWidth = 94  # 160
            # mapHeight = 70  # 120
            # c = 40075016.6855785
            # mpW = extent.width() / mapWidth
            # mpH = extent.height() / mapHeight
            # zW = math.log(c / mpW, 2) - 8
            # zH = math.log(c / mpH, 2) - 8
            # z = math.floor(min(zW, zH)) + 2
            # # self.iface.messageBar().pushMessage(self.tr('Zoom'), "z: {0}".format(z), level=QgsMessageBar.INFO)
            #
            #
            # # Tile Layer (Background Map)
            # # TODO: Move To Settings ...
            # ds = {}
            # # ds['type'] = 'TMS'
            # ds['title'] = 'basemap.at'
            # ds['attribution'] = 'basemap.at'
            # ds['attributionUrl'] = 'http://www.basemap.at'
            # ds['serviceUrl'] = "http://maps.wien.gv.at/basemap/bmaphidpi/normal/google3857/{z}/{y}/{x}.jpeg"  #geolandbasemap "https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}"
            # ds['yOriginTop'] = 1
            # ds['zmin'] = 0
            # ds['zmax'] = int(z)
            # ds['bbox'] = BoundingBox070(-180, -85.05, 180, 85.05)
            #
            # layerDef = TileLayerDefinition070(ds['title'], ds['attribution'], ds['attributionUrl'], ds['serviceUrl'],ds['yOriginTop'], ds['zmin'], ds['zmax'], ds['bbox'])
            #
            # tileLayer = TileLayer070(layerDef, False)
            # tileLayer.setCrs(QgsCoordinateReferenceSystem(3857, QgsCoordinateReferenceSystem.EpsgCrsId))
            #
            # if not tileLayer.isValid():
            #     error_message = self.tr('Background Layer %s can\'t be added to the map!') % ds['alias']
            #     self.iface.messageBar().pushMessage(self.tr('Error'),
            #                                         error_message,
            #                                         level=QgsMessageBar.CRITICAL)
            #     QgsMessageLog.logMessage(error_message, level=QgsMessageLog.CRITICAL)
            # else:
            #     QgsMapLayerRegistry.instance().addMapLayer(tileLayer, False)
            #     layerSet.append(tileLayer.id())
            #
            # # Set LayerSet
            # tileLayer.setExtent(extent)

            mapSettings.setExtent(extent)
            mapSettings.setLayers(layerSet)

            # Template
            template = os.path.dirname(__file__) + "/composer/templates/FundortDetail.qpt"  # map_print_test.qpt"
            templateDom = QDomDocument()
            templateDom.setContent(QFile(template), False)

            # Composition
            composition = QgsComposition(mapSettings)
            composition.setPlotStyle(QgsComposition.Print)
            composition.setPrintResolution(300)

            # Composer Items
            try:
                composition.loadFromTemplate(templateDom, siteDict)
            except Exception as e:
                QMessageBox.information(None, "Error", "Error Loading Template for Site Print: {0}".format(e))


            pageCount = 1

            adjustItemHightTxt = ["parzelle", "flur", "hoehe", "flaeche", "kommentar_lage", "kgs_lage", "befund", "literatur", "detailinterpretation"]

            for itemId in adjustItemHightTxt:
                itemTxt = composition.getComposerItemById(itemId + "Txt")
                if itemTxt:
                    fontHeight = QgsComposerUtils.fontHeightMM(itemTxt.font())
                    #oldHeight = itemTxt.rectWithFrame().height()
                    displayText = unicode(itemTxt.displayText())
                    w = itemTxt.rectWithFrame().width()
                    boxWidth = w - 2 * itemTxt.marginX()
                    lineCount = 0
                    oldLineCount = 0
                    spaceWidth = QgsComposerUtils.textWidthMM(itemTxt.font(), " ")
                    newText = u""
                    for line in displayText.splitlines():
                        lineWidth = max(1.0, QgsComposerUtils.textWidthMM(itemTxt.font(), line))
                        oldLineCount += math.ceil(lineWidth / boxWidth)
                        if lineWidth > boxWidth:
                            lineCount += 1
                            if lineCount > 1:
                                newText += u"\n"
                            accWordWidth = 0
                            wordNum = 0
                            for word in line.split():
                                wordNum += 1
                                wordWidth = QgsComposerUtils.textWidthMM(itemTxt.font(), word)
                                accWordWidth += wordWidth
                                if accWordWidth > boxWidth:
                                    if wordNum > 1:
                                        lineCount += 1
                                    if wordWidth > boxWidth:
                                        accCharWidth = 0
                                        newWord = u""
                                        for char in word:
                                            charWidth = QgsComposerUtils.textWidthMM(itemTxt.font(), char)
                                            accCharWidth += charWidth
                                            newWord += char
                                            if accCharWidth >= boxWidth - 5:
                                                #INSERT LINE BREAK
                                                lineCount += 1
                                                accCharWidth = 0
                                                newText += newWord
                                                newWord = u"\n"
                                        newText += newWord + u" "
                                        accWordWidth = accCharWidth + spaceWidth

                                    else:
                                        if wordNum > 1:
                                            newText += u"\n" + word + u" "

                                        accWordWidth = wordWidth + spaceWidth

                                else:
                                    accWordWidth += spaceWidth
                                    newText += word + u" "


                        else:
                            lineCount += 1 #math.ceil(textWidth / boxWidth)
                            if lineCount > 1:
                                newText += u"\n"
                            newText += line

                    itemTxt.setText(newText)

                    #QMessageBox.information(None, "LineCount", u"feld: {0}, old: {1}, new: {2}".format(itemId, oldLineCount, lineCount))

                    newHeight = fontHeight * (lineCount + 0.5)
                    newHeight += 2 * itemTxt.marginY() + 2

                    x = itemTxt.pos().x()
                    y = itemTxt.pos().y()
                    itemTxt.setItemPosition(x, y, w, newHeight, QgsComposerItem.UpperLeft, True, 1)



            adjustItems = ["parzelle", "flur", "hoehe", "flaeche", "kommentar_lage", "kgs_lage", "media", "befund", "literatur", "detailinterpretation"]

            bottomBorder = 30.0
            topBorder = 27.0
            i = 0
            newY = 0.0
            for itemId in adjustItems:
                itemTxt = composition.getComposerItemById(itemId + "Txt")
                itemLbl = composition.getComposerItemById(itemId +"Lbl")
                #itemBox = composition.getComposerItemById(itemId + "Box")


                if itemId == "media":
                    itemMap = composition.getComposerItemById("fundort_karte")
                    itemImg = composition.getComposerItemById("rep_luftbild")

                    y = newY + 5.0

                    itemMap.setItemPosition(itemMap.pos().x(), y, itemMap.rectWithFrame().width(), itemMap.rectWithFrame().height(), QgsComposerItem.UpperLeft, True, pageCount)
                    itemImg.setItemPosition(itemImg.pos().x(), y, itemImg.rectWithFrame().width(), itemImg.rectWithFrame().height(), QgsComposerItem.UpperLeft, True, pageCount)

                    itemMap.zoomToExtent(extent)

                    path = self.settings.value("APIS/repr_image_dir", QDir.home().dirName())
                    repImageName = self.getRepresentativeImage(siteDict['fundortnummer'])

                    newY = itemImg.pos().y() + itemImg.rectWithFrame().height() + 5.0

                    if repImageName:
                        path += u"\\" + repImageName + u".jpg"

                        repImageFile = QFile(path)
                        if repImageFile.exists():
                            itemImg.setPicturePath(path)
                        else:
                            #remove itemImg (to avoid red cross)
                            composition.removeComposerItem(itemImg)
                    else:
                        #remove itemImg (to avoid red cross)
                        composition.removeComposerItem(itemImg)


                if itemTxt and itemLbl:

                    x = itemTxt.pos().x()
                    if i == 0:
                        y = itemTxt.pos().y()
                    else:
                        y = newY
                    w = itemTxt.rectWithFrame().width()
                    h  = itemTxt.rectWithFrame().height()
                    newY = y + h
                    if newY > composition.paperHeight() - bottomBorder:
                        pageCount += 1
                        y = topBorder
                        newY = y + newHeight
                        #copy Header
                        header = 1
                        while composition.getComposerItemById("header_{0}".format(header)):
                            self.cloneLabel(composition, composition.getComposerItemById("header_{0}".format(header)), pageCount)
                            header += 1
                        #copyFooter
                        footer = 1
                        while composition.getComposerItemById("footer_{0}".format(footer)):
                            self.cloneLabel(composition, composition.getComposerItemById("footer_{0}".format(footer)),pageCount)
                            footer += 1

                    itemTxt.setItemPosition(x, y, w, h, QgsComposerItem.UpperLeft, True, pageCount)
                    itemLbl.setItemPosition(itemLbl.pos().x(), y, itemLbl.rectWithFrame().width(), itemLbl.rectWithFrame().height(), QgsComposerItem.UpperLeft, True, pageCount)

                    i += 1

                    #if itemBox:
                        #h = (itemBox.rectWithFrame().height() - oldHeight) + newHeight
                        #itemBox.setItemPosition(itemBox.pos().x(), itemBox.pos().y(), itemBox.rectWithFrame().width(), h, QgsComposerItem.UpperLeft, True, pageCount)
            addLineAfterItems = ["lage_und_koordinaten", "kgs_lageLbl"]
            for itemId in addLineAfterItems:
                continue
            #QMessageBox.information(None, "info", u"w: {0}, h: {1}, w: {2}, h: {3}, , x: {4}, y: {5}".format(width, height, l.rectWithFrame().width(), l.rectWithFrame().height(), l.pos().x(), l.pos().y()))

            composition.setNumPages(pageCount)

            # Create PDF
            if isTemp:
                targetFile = os.path.join(targetFileOrFolder, u"Fundort_{0}_{1}.pdf".format(siteDict['fundortnummer'], timeStamp))
            else:
                targetFile = targetFileOrFolder

            composition.exportAsPDF(targetFile)
            sitePdfs.append(targetFile)

        return sitePdfs

    def cloneLabel(self, comp, l, pageCount):
        label = QgsComposerLabel(comp)
        label.setItemPosition(l.pos().x(), l.pos().y(), l.rectWithFrame().width(), l.rectWithFrame().height(), QgsComposerItem.UpperLeft, True, pageCount)
        label.setBackgroundEnabled(True)
        label.setBackgroundColor(QColor("#CCCCCC"))
        label.setText(l.text())
        label.setVAlign(l.vAlign())
        label.setHAlign(l.hAlign())
        label.setMarginX(l.marginX())
        label.setMarginY(l.marginY())
        label.setFont(l.font())
        comp.addItem(label)

    def getSpatialiteLayer(self, layerName, subsetString=None, displayName=None):
        if not displayName:
            displayName = layerName
        uri = QgsDataSourceURI()
        uri.setDatabase(self.dbm.db.databaseName())
        uri.setDataSource('', layerName, 'geometry')
        layer = QgsVectorLayer(uri.uri(), displayName, 'spatialite')
        if subsetString:
            layer.setSubsetString(subsetString)

        return layer

    def getRepresentativeImage(self, siteNumber):
        query = QSqlQuery(self.dbm.db)
        query.prepare(u"SELECT CASE WHEN repraesentatives_luftbild IS NULL THEN 0 WHEN repraesentatives_luftbild ='_1' THEN 0 ELSE repraesentatives_luftbild END as repImage FROM fundort WHERE fundortnummer = '{0}'".format(siteNumber))
        res = query.exec_()
        query.first()
        if query.value(0) == 0:
            return False
        else:
            return unicode(query.value(0))

class ApisFindSpotPrinter(ApisPrinter):

    def exportDetailsPdf(self, findSpotList, targetFileOrFolder, timeStamp):

        queryStr = u"SELECT fundortnummer_nn, land, katastralgemeinde, katastralgemeindenummer, fundstelle.* FROM fundstelle, fundort WHERE fundstelle.fundortnummer = fundort.fundortnummer AND fundstelle.fundortnummer || '.' || fundstelle.fundstellenummer IN ({0}) ORDER BY land, katastralgemeindenummer, fundortnummer_nn, fundstelle.fundstellenummer".format((u",".join(u"'{0}'".format(findSpot) for findSpot in findSpotList)))

        query = QSqlQuery(self.dbm.db)
        query.prepare(queryStr)
        query.exec_()

        query.seek(-1)
        pdfFiles = {}
        while query.next():
            findSpotDict = {}
            rec = query.record()

            # Write SQL Result to Dict
            for col in range(rec.count()-1): # -1 because geometry not needed!
                val = u"{0}".format(rec.value(col))
                if val.replace(" ", "") == '' or val == 'NULL':
                    val = u"---"
                findSpotDict[unicode(rec.fieldName(col))] = val

            findSpotDict['datum_druck'] = QDate.currentDate().toString("dd.MM.yyyy")
            findSpotDict['datum_ersteintrag'] = QDate.fromString(findSpotDict['datum_ersteintrag'], "yyyy-MM-dd").toString("dd.MM.yyyy")
            findSpotDict['datum_aenderung'] = QDate.fromString(findSpotDict['datum_aenderung'], "yyyy-MM-dd").toString("dd.MM.yyyy")

            # Replace Codes
            if findSpotDict['sicherheit'] == u"1":
                findSpotDict['sicherheit'] = u"sicher"
            elif findSpotDict['sicherheit'] == u"2":
                findSpotDict['sicherheit'] = u"wahrscheinlich"
            elif findSpotDict['sicherheit'] == u"3":
                findSpotDict['sicherheit'] = u"fraglich"
            elif findSpotDict['sicherheit'] == u"4":
                findSpotDict['sicherheit'] = u"keine Fundstelle"

            # MapSettings (Needed for Composition)
            mapSettings = QgsMapSettings()
            mapSettings.setMapUnits(QGis.UnitType(0))
            mapSettings.setOutputDpi(300)

            # Template
            template = os.path.dirname(__file__) + "/composer/templates/FundstelleDetail.qpt"
            templateDom = QDomDocument()
            templateDom.setContent(QFile(template), False)

            # Composition
            composition = QgsComposition(mapSettings)
            composition.setPlotStyle(QgsComposition.Print)
            composition.setPrintResolution(300)
            composition.loadFromTemplate(templateDom, findSpotDict)

            # Composer Items

            pageCount = 1

            adjustItems = ["kommentar_lage", "fundbeschreibung", "fundverbleib", "befund", "fundgeschichte", "literatur", "sonstiges"]
            bottomBorder = 30.0
            topBorder = 27.0
            i = 0
            for itemId in adjustItems:

                itemTxt = composition.getComposerItemById(itemId + "Txt")
                itemLbl = composition.getComposerItemById(itemId +"Lbl")
                itemBox = composition.getComposerItemById(itemId + "Box")

                if itemTxt and itemLbl:

                    #textWidth = QgsComposerUtils.textWidthMM(itemTxt.font(), itemTxt.displayText())
                    fontHeight = QgsComposerUtils.fontHeightMM(itemTxt.font())
                    oldHeight = itemTxt.rectWithFrame().height()
                    displayText = itemTxt.displayText()
                    boxWidth = itemTxt.rectWithFrame().width() - 2 * itemTxt.marginX()
                    lineCount = 0
                    for line in displayText.splitlines():
                        textWidth = max(1.0, QgsComposerUtils.textWidthMM(itemTxt.font(), line))
                        lineCount += math.ceil(textWidth / boxWidth)

                    newHeight = fontHeight * (lineCount + 1)
                    newHeight += 2 * itemTxt.marginY() + 2

                    x = itemTxt.pos().x()
                    if i == 0:
                        y = itemTxt.pos().y()
                    else:
                        y = newY
                    w = itemTxt.rectWithFrame().width()
                    newY = y + newHeight
                    if newY > composition.paperHeight() - bottomBorder:
                        pageCount += 1
                        y = topBorder
                        newY = y + newHeight
                        #copy Header
                        header = 1
                        while composition.getComposerItemById("header_{0}".format(header)):
                            self.cloneLabel(composition, composition.getComposerItemById("header_{0}".format(header)), pageCount)
                            header += 1
                        #copyFooter
                        footer = 1
                        while composition.getComposerItemById("footer_{0}".format(footer)):
                            self.cloneLabel(composition, composition.getComposerItemById("footer_{0}".format(footer)),pageCount)
                            footer += 1

                    itemTxt.setItemPosition(x, y, w, newHeight, QgsComposerItem.UpperLeft, True, pageCount)
                    itemLbl.setItemPosition(itemLbl.pos().x(), y, itemLbl.rectWithFrame().width(), itemLbl.rectWithFrame().height(), QgsComposerItem.UpperLeft, True, pageCount)

                    i += 1

                    if itemBox:
                        h = (itemBox.rectWithFrame().height() - oldHeight) + newHeight
                        itemBox.setItemPosition(itemBox.pos().x(), itemBox.pos().y(), itemBox.rectWithFrame().width(), h, QgsComposerItem.UpperLeft, True, pageCount)


            #QMessageBox.information(None, "info", u"w: {0}, h: {1}, w: {2}, h: {3}, , x: {4}, y: {5}".format(width, height, l.rectWithFrame().width(), l.rectWithFrame().height(), l.pos().x(), l.pos().y()))

            composition.setNumPages(pageCount)

            # Create PDF
            if len(findSpotList) > 1:
                targetFile = os.path.join(targetFileOrFolder, u"Fundstelle_{0}.{1}_{2}.pdf".format(findSpotDict['fundortnummer'], findSpotDict['fundstellenummer'], timeStamp))
            else:
                targetFile = targetFileOrFolder

            composition.exportAsPDF(targetFile)
            key = u"{0}".format(findSpotDict['fundortnummer'])
            if key not in pdfFiles:
                pdfFiles[key] = []
            pdfFiles[key].append(targetFile)

        return pdfFiles

    def cloneLabel(self, comp, l, pageCount):
        label = QgsComposerLabel(comp)
        label.setItemPosition(l.pos().x(), l.pos().y(), l.rectWithFrame().width(), l.rectWithFrame().height(), QgsComposerItem.UpperLeft, True, pageCount)
        label.setBackgroundEnabled(True)
        label.setBackgroundColor(QColor("#CCCCCC"))
        label.setText(l.text())
        label.setVAlign(l.vAlign())
        label.setHAlign(l.hAlign())
        label.setMarginX(l.marginX())
        label.setMarginY(l.marginY())
        label.setFont(l.font())
        comp.addItem(label)


class ApisListPrinter(ApisPrinter):
    '''
    Input: SQL Query
    '''

    def setupInfo(self, fileName, dialogTitle, headerLeft, headerWidthAdjustment):
        self.info = {}
        self.info["file_name"] = fileName
        self.info["dialog_title"] = dialogTitle
        #self.info["list_title"] = listTitle

        self.info["header_left"] = headerLeft
        self.info["header_right"] = u"Anzahl:\t{0}"

        self.info["footer_left"] = u"Luftbildarchiv\nInstitut für Urgeschichte und Historische Archäologie\nUniversität Wien"
        self.info["footer_center"] = u"{0}".format(QDateTime.currentDateTime().toString("dd.MM.yyyy"))
        self.info["footer_right"] = u"Seite {0}"

        self.info["header_width_adjustment"] = headerWidthAdjustment

    def printList(self, updateScan=None, updateOrtho=None, updateHiRes=None):
        if self.query and self.info:
            if not self.fileName:
                self._setFileName(self.info["file_name"], self.info["dialog_title"])
            #fileName = QFileDialog.getSaveFileName(self.parent, "ABC", "test", '*.pdf')
            if self.fileName:

                query = QSqlQuery(self.dbm.db)
                query.prepare(self.query)
                query.exec_()

                #updateFields = [u"Gescannt"]

                rowCount = 0
                hLabels = [u"#"]
                #tabColsHeader.append(QgsComposerTableColumn(u"#"))
                while query.next():
                    if rowCount == 0:
                        for i in range(query.record().count()):
                            hLabels.append(query.record().fieldName(i))
                            #tabColsHeader.append(QgsComposerTableColumn(query.record().fieldName(i)))
                    rowCount += 1
                self.info["header_right"] = self.info["header_right"].format(rowCount)
                query.seek(-1)

                hLabelsAdjust = []
                for l in hLabels:
                    hLabelsAdjust.append(l.ljust(self.info["header_width_adjustment"]))
                    #hLabelsAdjust.append(l)

                count = 0
                countTotal = 0
                page = 1
                prevPage = 0
                hHight = 15
                fHight = 15
                margin = 15
                mTab = 5
                hWidth = self.comp.paperWidth() / 2 - margin
                fWidth = (self.comp.paperWidth() - (2 * margin)) / 3

                while query.next():
                    countTotal += 1
                    count += 1
                    if count > self.pageBreak:
                        count = 1
                        page += 1
                    if page > prevPage:
                        prevPage = page
                        #Header
                        self._addLabel(self.info["header_left"], margin, margin, hWidth, hHight, QgsComposerItem.UpperLeft, page, 5, Qt.AlignLeft, QFont("Arial", 16, 100))
                        self._addLabel(self.info["header_right"], self.comp.paperWidth()/2, margin, hWidth , hHight, QgsComposerItem.UpperLeft, page, 5, Qt.AlignRight)
                        #Footer
                        self._addLabel(self.info["footer_left"], margin, self.comp.paperHeight()-margin, fWidth, fHight, QgsComposerItem.LowerLeft, page)
                        self._addLabel(self.info["footer_center"], margin+fWidth, self.comp.paperHeight()-margin, fWidth, fHight, QgsComposerItem.LowerLeft, page, 5, Qt.AlignHCenter)
                        self._addLabel(self.info["footer_right"].format(page), margin + (2 * fWidth), self.comp.paperHeight()-margin, fWidth, fHight, QgsComposerItem.LowerLeft, page, 5, Qt.AlignRight)


                        #
                        table = QgsComposerTextTable(self.comp)
                        #self.comp.addMultiFrame(table)

                        #frame1 = QgsComposerFrame(self.comp, table, margin+mTab, margin + hHight + mTab, 200, 200)
                        #frame1.setFrameEnabled(False) #True)
                        #frame1.setItemPosition(margin+mTab, margin+hHight+mTab, 200, 200, QgsComposerItem.UpperLeft, page)
                        #table.addFrame(frame1)
                        #self.comp.addItem(frame1)

                        #table.setColumns(tabColsHeader)
                        table.setShowGrid(True)
                        table.setGridStrokeWidth(0.2)
                        table.setLineTextDistance(1.2)
                        table.setHeaderFont(QFont("Arial", 9, 100))

                        table.setHeaderLabels(hLabelsAdjust)
                        table.setItemPosition(margin + mTab, margin + hHight + mTab, QgsComposerItem.UpperLeft, page)
                        self.comp.addItem(table)


                    row = []
                    rec = query.record()
                    for i in range(rec.count()):
                        fieldName = rec.fieldName(i)

                        if fieldName == updateScan:
                            if rec.contains("bildnummer"):
                                value = "ja" if self.imageRegistry.hasImage(unicode(rec.value("bildnummer"))) else "nein"
                            else:
                                value = self.imageRegistry.hasImageRE(unicode(rec.value("filmnummer")) + "_.+")
                            rec.setValue(i, value)
                        elif fieldName == updateOrtho:
                            if rec.contains("bildnummer"):
                                value = "ja" if self.imageRegistry.hasOrtho(unicode(rec.value("bildnummer"))) else "nein"
                            else:
                                value = self.imageRegistry.hasOrthoRE(unicode(rec.value("filmnummer")) + "_.+")
                            rec.setValue(i, value)
                        elif fieldName == updateHiRes:
                            if rec.contains("bildnummer"):
                                value = "ja" if self.imageRegistry.hasHiRes(unicode(rec.value("bildnummer"))) else "nein"
                            else:
                                value = self.imageRegistry.hasHiResRE(unicode(rec.value("filmnummer")) + "_.+")
                            rec.setValue(i, value)

                        row.append(unicode("" if rec.isNull(i) else rec.value(i)))

                    table.addRow([str(countTotal).zfill(len(str(rowCount)))] + row)

                self.comp.setNumPages(page)
                self._export()

                return self.fileName



    def _addLabel(self, text, x, y, w, h, pos, page, marginX=5, halign=Qt.AlignLeft, font=QFont("Arial", 8)):
        label = QgsComposerLabel(self.comp)
        label.setItemPosition(x, y, w, h, pos, False, page)
        label.setBackgroundEnabled(True)
        label.setBackgroundColor(QColor("#CCCCCC"))
        label.setText(text)
        label.setVAlign(Qt.AlignVCenter)
        label.setHAlign(halign)
        label.setMarginX(marginX)
        label.setFont(font)
        self.comp.addItem(label)


class ApisDetailPrinter(ApisPrinter):

    def setDetailQuery(self, query):
        self.detailQuery = query

    def _loadTemplate(self):
        pass

    def _loadMap(self):

        self.ms.setCrsTransformEnabled(True)
        self.ms.setDestinationCrs(QgsCoordinateReferenceSystem(3857, QgsCoordinateReferenceSystem.EpsgCrsId))
        self.ms.setMapUnits(QGis.UnitType(0))
        self.ms.setOutputDpi(300)


        # self.iface.messageBar().pushMessage(self.tr('WH'), "w: {0}, h: {1}".format(composerMap.rect().width(), composerMap.rect().height()), level=QgsMessageBar.INFO)

        layerSet = []

        # Vector Layer
        flightpathDir = self.settings.value("APIS/flightpath_dir")
        uri = flightpathDir + "\\2010\\02101101_lin.shp"
        vectorLayer = QgsVectorLayer(uri, "FlightPath", "ogr")

        # GET CRS FROM LAYER !!!!

        # Sets layer's spatial reference system
        vectorLayer.setCrs(QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId))
        # Setup the coordinate system transformation for the layer.
        vectorLayer.setCoordinateSystem()

        lineSymbol = QgsLineSymbolV2.createSimple({'color': 'orange', 'line_width': '0.3'})
        vectorLayer.rendererV2().setSymbol(lineSymbol)

        QgsMapLayerRegistry.instance().addMapLayer(vectorLayer, False)  # False = don't add to Layers (TOC)
        layerSet.append(vectorLayer.id())

        extent = self.ms.layerExtentToOutputExtent(vectorLayer, vectorLayer.extent())
        extent.scale(1.1)

        # e = vectorLayer.extent()
        # eGeo = QgsGeometry.fromRect(e)
        # gt = QgsCoordinateTransform(QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId), QgsCoordinateReferenceSystem(3857, QgsCoordinateReferenceSystem.EpsgCrsId))
        # eGeo.transform(gt)
        # eRect = eGeo.boundingBox()

        import math
        mapWidth = 160
        mapHeight = 120
        c = 40075016.6855785
        mpW = extent.width() / mapWidth
        mpH = extent.height() / mapHeight
        zW = math.log(c / mpW, 2) - 8
        zH = math.log(c / mpH, 2) - 8
        z = math.floor(min(zW, zH)) + 2
        #self.iface.messageBar().pushMessage(self.parent.tr('Zoom'), "z: {0}".format(z), level=QgsMessageBar.INFO)

        # Tile Layer (Background Map)
        #title, attribution, serviceUrl, yOriginTop = 1, zmin = TileDefaultSettings.ZMIN, zmax = TileDefaultSettings.ZMAX, bbox = None
        ds = {}
        ds['type'] = 'TMS'
        ds['alias'] = 'Google'
        ds['copyright_text'] = 'Google'
        ds['copyright_url'] = 'http://www.google.com'
        ds['tms_url'] = "https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}"

        service_info = TileLayerDefinition(ds['alias'], ds['alias'], ds['tms_url'])
        service_info.zmin = 0
        service_info.zmax = int(z)
        # if ds.tms_y_origin_top is not None:
        #    service_info.yOriginTop = ds.tms_y_origin_top
        service_info.epsg_crs_id = 3857
        service_info.postgis_crs_id = None
        service_info.custom_proj = None
        service_info.bbox = BoundingBox(-180, -85.05, 180, 85.05)

        tileLayer = TileLayer(service_info, False)
        tileLayer.setCrs(QgsCoordinateReferenceSystem(3857, QgsCoordinateReferenceSystem.EpsgCrsId))

        if not tileLayer.isValid():
            error_message = self.parent.tr('Background Layer %s can\'t be added to the map!') % ds['alias']
            self.iface.messageBar().pushMessage(self.parent.tr('Error'),
                                                error_message,
                                                level=QgsMessageBar.CRITICAL)
            QgsMessageLog.logMessage(error_message, level=QgsMessageLog.CRITICAL)
        else:
            # Set Attributes
            tileLayer.setAttribution(ds['copyright_text'])
            tileLayer.setAttributionUrl(ds['copyright_url'])
            QgsMapLayerRegistry.instance().addMapLayer(tileLayer, False)
            layerSet.append(tileLayer.id())

        # Set LayerSet
        tileLayer.setExtent(extent)
        self.ms.setExtent(extent)

        self.ms.setLayers(layerSet)

        self.extent = extent

        # Refreshes the composition when composer related options change
        #self.comp.updateSettings()



        #self.comp.updateSettings()

    def _loadImage(self):
        pass

    def _setupDict(self):
        pass

    def printToPdf(self):
        pass

class ApisFilmDetailPrinter(ApisDetailPrinter):

    def printFilmDetail(self):
        if self.query:

            query = QSqlQuery(self.dbm.db)
            query.prepare(self.query)
            query.exec_()

            rowCount = 0
            while query.next():
                rowCount += 1
            query.seek(-1)

            if rowCount <= 1:
                query.next()
                singleEntry = query.value(0)
                fileName = u"Filmdetails_{0}".format(singleEntry)
                query.seek(-1)
            else:
                fileName = u"Filmdetails_Sammlung"

            self._setFileName(fileName, "Film Details Speichern", True)

            if self.fileName:


                # load maps

                #load temlate

                tempFileNames = []
                while query.next():
                    filmDict = {}
                    rec = query.record()
                    for col in range(rec.count()):
                        val = unicode(rec.value(col))
                        if val.replace(" ", "") == '' or val == 'NULL':
                            val = u"---"

                        filmDict[unicode(rec.fieldName(col))] = val

                    filmDict['wetter_description'] = self._generateWeatherCode(filmDict['wetter'])
                    filmDict['datum_druck'] = QDate.currentDate().toString("yyyy-MM-dd")

                    self._loadMap()

                    self.template = os.path.dirname(__file__) + "/composer/templates/map_print_test.qpt"
                    self.templateDOM = QDomDocument()
                    self.templateDOM.setContent(QFile(self.template), False)

                    composition = QgsComposition(self.ms)
                    composition.setPlotStyle(QgsComposition.Print)
                    composition.setPrintResolution(300)

                    composition.loadFromTemplate(self.templateDOM, filmDict, False, True)

                    composerMap = composition.getComposerMapById(0)
                    composerMap.zoomToExtent(self.extent)

                    composition.exportAsPDF(self.fileName)
                    self._openFile()

                    if rowCount > 1:
                        tempFileName = self.fileName + "." + filmDict["filmnummer"] + ".pdf"
                        self.comp.exportAsPDF(tempFileName)
                        tempFileNames.append(tempFileName)
                return

                if tempFileNames and rowCount > 1:
                    self._mergePdfs(self.fileName,tempFileNames)
                    self._openFile()
                else:
                    self._export()

    def _generateWeatherCode(self, weatherCode):
        categories = ["Low Cloud Amount", "Visibility Kilometres", "Low Cloud Height", "Weather", "Remarks Mission",
                      "Remarks Weather"]
        query = QSqlQuery(self.dbm.db)
        pos = 0
        help = 0
        weatherDescription = ""
        for c in weatherCode:
            qryStr = "select description from wetter where category = '{0}' and code = '{1}' limit 1".format(categories[pos - help], c)
            query.exec_(qryStr)
            query.first()
            fn = query.value(0)
            if pos <= 5:
                weatherDescription += categories[pos] + ': ' + fn
                if pos < 5:
                    weatherDescription += '\n'
            else:
                weatherDescription += '; ' + fn

            if pos >= 5:
                help += 1
            pos += 1
        return weatherDescription


class ApisFilmDetailsPrinter(ApisDetailPrinter):
    '''
    Input: List of FilmIDs
    '''
    def printToPdf(self, filmIdList):
        self.filmIdList = filmIdList
        self._save()
        if self.fileName:
            self._prepair()
            #self._export()
            #self._cleanup()
            #if self.openFile:
                #self._openFile()

    def _save(self):
        if len(self.filmIdList) <= 1:
            self._setFileName(u"Filmdetails_{0}".format(self.filmIdList[0]), u"Filmdetails speichern")
        else:
            self._setFileName(u"Filmdetails_Sammlung", u"Filmdetails speichern")

    def _prepair(self):
        try:

            #FIXME template from Settings ':/plugins/APIS/icons/settings.png'
            template = 'C:/Users/Johannes/.qgis2/python/plugins/APIS/composer/templates/test.qpt'
            #if os.path.isfile(template):
            templateDOM = QDomDocument()
            templateDOM.setContent(QFile(template), False)

            #for filmId in self.filmIdList:

            #FIXME load correct Flightpath; from Settings
            #printLayers = []
            #flightpathDir = self.settings.value("APIS/flightpath_dir")
            #uri = flightpathDir + "\\" + self.uiFlightDate.date().toString("yyyy") + "\\" + filmId + "_lin.shp"
            #printLayer = QgsVectorLayer(uri, "FlightPath", "ogr")
            #QgsMapLayerRegistry.instance().addMapLayer(printLayer, False) #False = don't add to Layers (TOC)
            #extent = printLayer.extent()

            #layerset.append(printLayer.id())
            #printLayers.append(printLayer.id())

            #urlWithParams = ' '
            #urlWithParams = 'url=http://wms.jpl.nasa.gov/wms.cgi&layers=global_mosaic&styles=pseudo&format=image/jpeg&crs=EPSG:4326'
            #rlayer = QgsRasterLayer(urlWithParams, 'basemap', 'wms')
            #QgsMapLayerRegistry.instance().addMapLayer(rlayer)
            #printLayers.append(rlayer.id())

            #ms = QgsMapSettings()
            #ms.setExtent(extent)
            #mr.setLayerSet(layerset)

            #mapRectangle = QgsRectangle(140,-28,155,-15)
            #mr.setExtent(extent)

            #comp = QgsComposition(ms)
            #comp.setPlotStyle(QgsComposition.Print)
            #comp.setPrintResolution(300)

            #m = self.mapper.model()
            #r = self.mapper.currentIndex()

            filmDict = {'filmnummer': 'abc'}
            #for c in range(m.columnCount()):
                #filmDict[m.headerData(c, Qt.Horizontal)] = unicode(m.data(m.createIndex(r, c)))
                #QMessageBox.warning(None, "Save", "{0}:{1}".format(colName, value))

            #self.comp.setNumPages(13)
            self.comp.loadFromTemplate(templateDOM, filmDict)
            QMessageBox.warning(None, "Save",self.fileName)
            self.comp.exportAsPDF(self.fileName)
            #self._export()

        except:
            raise IOError



        #composerMap = comp.getComposerMapById(0)
        #composerMap.setKeepLayerSet(True)
        #composerMap.setLayerSet(printLayers)
        #composerMap.renderModeUpdateCachedImage()
        #ms.setLayers(printLayers)

        #if composerMap:
            #QMessageBox.warning(None, "Save", composerMap)
        #composerMap.setKeepLayerSet(True)
        #composerMap.setLayerSet(layerset)






    def _cleanup():
         #FIXME: Delete all alyers (array) not just one layer
         #QgsMapLayerRegistry.instance().removeMapLayer(printLayer.id())
        pass


class ApisLabelPrinter():

    def __init__(self, parent, captureMode, pageSettings, labelSettings, labelLayout, labelItemOrder, labelsData):
        self.parent = parent
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)
        self.pageSettings = {}
        self.labelSettings = {}
        self.labelsData = labelsData
        self.labelLayout = labelLayout
        self.labelItemOrder = labelItemOrder

        saveDir = self.settings.value("APIS/working_dir", QDir.home().dirName())
        dt = QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")
        fileName = u"Etiketten_{0}".format(captureMode)
        self.fileName = QFileDialog.getSaveFileName(self.parent, u"Etiketten Export", saveDir + u"\\" + u"{0}_{1}".format(fileName, dt), '*.pdf')

        if not self.fileName:
            self.fileName = None
            return

        self.pageSettings['width'] = max(10.0, pageSettings['width']) if 'width' in pageSettings else 210.0
        self.pageSettings['height'] = max(10.0, pageSettings['height']) if 'height' in pageSettings else 297.0
        self.pageSettings['top'] = max(0.0, pageSettings['top']) if 'top' in pageSettings else 0.0
        self.pageSettings['bottom'] = max(0.0, pageSettings['bottom']) if 'bottom' in pageSettings else 0.0
        self.pageSettings['left'] = max(0.0, pageSettings['left']) if 'left' in pageSettings else 0.0
        self.pageSettings['right'] = max(0.0, pageSettings['right']) if 'right' in pageSettings else 0.0
        self.pageSettings['right'] = max(0.0, pageSettings['right']) if 'right' in pageSettings else 0.0
        self.pageSettings['page_resolution'] = max(150.0, pageSettings['page_resolution']) if 'page_resolution' in pageSettings else 300.0

        self.labelSettings['width'] = max(10.0, labelSettings['width']) if 'width' in labelSettings else 70.0
        self.labelSettings['height'] = max(10.0, labelSettings['height']) if 'height' in labelSettings else 45.0

        self.colCount = int((self.pageSettings['width'] - (self.pageSettings['left'] + self.pageSettings['right'])) / self.labelSettings['width'])
        self.rowCount = int((self.pageSettings['height'] - (self.pageSettings['top'] + self.pageSettings['bottom'])) / self.labelSettings['height'])
        #QMessageBox.information(None, "info", "cols: {0} rows: {1}".format(self.colCount, self.rowCount))
        self.currentCol = 0
        self.currentRow = 0
        self.labelCount = 0
        self.pageCount = 1

        self._setupComposition()
        #generate Labels
        labelGroups = []
        for labelData in self.labelsData:
            newLabelGroups = self._generateLabel(labelData)
            labelGroups += newLabelGroups

        #QMessageBox.information(None, "Info", "{0}".format(len(labelGroups)))

        for labelGroup in labelGroups:
            dx = self.currentCol * self.labelSettings['width']
            dy = self.currentRow * self.labelSettings['height']
            labelGroup.setItemPosition(dx, dy, QgsComposerItem.UpperLeft, self.pageCount)
            self.composition.addItem(labelGroup)
            self.currentCol += 1
            if self.currentCol >= self.colCount:
                self.currentCol = 0
                self.currentRow += 1
            if self.currentRow >= self.rowCount:
                self.currentRow = 0
                self.pageCount += 1

        self._exportLabelsToPdf()

    def _setupComposition(self):
        self.mapSettings = QgsMapSettings()
        self.composition = QgsComposition(self.mapSettings)
        self.composition.setPlotStyle(QgsComposition.Print)
        self.composition.setPrintResolution(self.pageSettings['page_resolution'])
        self.composition.setPaperSize(self.pageSettings['width'], self.pageSettings['height'])

    def _generateLabel(self, labelData):
        x = 0
        y = 0
        maxH = 0
        labelGroups = []
        for key in self.labelItemOrder:
            for item in labelData[key]:

                w = self.labelSettings['width'] * self.labelLayout[key]['width']
                h = self.labelSettings['height'] * self.labelLayout[key]['height']
                maxH = max(maxH, h)

                if x+w > self.labelSettings['width']:
                    x = 0
                    y += maxH
                    maxH = max(maxH, h)

                if y+h > self.labelSettings['height']:
                    y = 0
                    x = 0

                if y == 0:
                    labelGroups.append(QgsComposerItemGroup(self.composition))
                    labelGroups[len(labelGroups)-1].setItemPosition(0, 0, self.labelSettings['width'], self.labelSettings['height'])

                label = self._generateLabelItem(u"{0}".format(item), x, y, w, h, key)
                labelGroups[len(labelGroups)-1].addItem(label)

                x += w

        return labelGroups

    def _generateLabelItem(self, text, x, y, w, h, key):
        label = QgsComposerLabel(self.composition)
        label.setItemPosition(x, y, w, h)
        #label.setBackgroundEnabled(True)
        #label.setBackgroundColor(QColor("#CCCCCC"))
        label.setText(text)
        label.setVAlign(self.labelLayout[key]['valign'])
        label.setHAlign(self.labelLayout[key]['halign'])
        label.setMarginX(0)
        label.setMarginY(0)
        label.setFont(self.labelLayout[key]['font'])
        self.composition.addItem(label)
        return label

    def _exportLabelsToPdf(self):
        if self.fileName:
            self.composition.setNumPages(self.pageCount)
            self.composition.exportAsPDF(self.fileName)
            self._openFile()

    def _openFile(self):
        if self.fileName and os.path.isfile(self.fileName):
            OpenFileOrFolder(self.fileName)




