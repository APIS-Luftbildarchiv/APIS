# -*- coding: utf-8 -*

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from qgis.gui import *
from qgis.core import *

from PyPDF2 import PdfFileMerger, PdfFileReader


from apis_db_manager import *
from apis_printer import *
from apis_image_registry import *

from functools import partial

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

# --------------------------------------------------------
# Film - Eingabe, Pflege
# --------------------------------------------------------
from apis_film_selection_list_form import *
from functools import partial

class ApisFilmSelectionListDialog(QDialog, Ui_apisFilmSelectionListDialog):

    def __init__(self, iface, model, dbm, imageRegistry, parent):
        QDialog.__init__(self)
        self.iface = iface
        self.model = model
        self.dbm = dbm
        self.imageRegistry = imageRegistry
        self.setupUi(self)
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)

        self.uiDisplayFlightPathBtn.clicked.connect(lambda: parent.openViewFlightPathDialog(self.getFilmList(), self))
        self.uiExportListAsPdfBtn.clicked.connect(self.exportListAsPdf)
        self.uiExportDetailsAsPdfBtn.clicked.connect(self.exportDetailsAsPdf)

        self.accepted.connect(self.onAccepted)

        self.setupTable()

    def setupTable(self):
        self.uiFilmListTableV.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.uiFilmListTableV.setModel(self.model)
        self.uiFilmListTableV.setEditTriggers(QAbstractItemView.NoEditTriggers)

        #hide and sort Columns
        self.visibleColumns = ['filmnummer', 'flugdatum', 'anzahl_bilder', 'weise', 'art_ausarbeitung', 'militaernummer', 'militaernummer_alt']
        vCIdx = []
        for vC in self.visibleColumns:
            vCIdx.append(self.model.fieldIndex(vC))

        for c in range(self.model.columnCount()):
            if c not in vCIdx:
                self.uiFilmListTableV.hideColumn(c)

        hH = self.uiFilmListTableV.horizontalHeader()
        for i in range(len(vCIdx)):
            hH.moveSection(hH.visualIndex(vCIdx[i]), i)

        self.uiFilmListTableV.resizeColumnsToContents()
        self.uiFilmListTableV.resizeRowsToContents()
        self.uiFilmListTableV.horizontalHeader().setResizeMode(QHeaderView.Stretch)

        # signals
        self.uiFilmListTableV.doubleClicked.connect(self.viewFilm)
        #self.uiFilmListTableV.selectionModel().selectionChanged.connect(self.onSelectionChanged)

        self.uiFilmListTableV.sortByColumn(0, Qt.AscendingOrder)

    def getFilmList(self, getAll=False):
        filmList = []
        if self.uiFilmListTableV.selectionModel().hasSelection() and not getAll:
            rows = self.uiFilmListTableV.selectionModel().selectedRows()
            for row in rows:
                #get filmnummer
                filmList.append(self.model.data(self.model.createIndex(row.row(), self.model.fieldIndex("filmnummer"))))
        else:
            for row in  range(self.model.rowCount()):
                filmList.append(self.model.data(self.model.createIndex(row, self.model.fieldIndex("filmnummer"))))

        return filmList

    def getFilmListWithRows(self, getAll=False):
        filmList = []
        if self.uiFilmListTableV.selectionModel().hasSelection() and not getAll:
            rows = self.uiFilmListTableV.selectionModel().selectedRows()
            for row in rows:
                rowContent = []
                for col in self.visibleColumns:
                    rowContent.append(self.model.data(self.model.createIndex(row.row(), self.model.fieldIndex(col))))
                filmList.append(rowContent)
        else:
            for row in  range(self.model.rowCount()):
                rowContent = []
                for col in self.visibleColumns:
                    #QMessageBox.warning(None, "Bild", u"{0}".format(self.model.data(self.model.createIndex(row, col))))
                    rowContent.append(self.model.data(self.model.createIndex(row, self.model.fieldIndex(col))))
                filmList.append(rowContent)

        return filmList

    def viewFilm(self):
        # QMessageBox.warning(None, "FilmNumber", "Double")
        filmIdx = self.model.createIndex(self.uiFilmListTableV.currentIndex().row(), self.model.fieldIndex("filmnummer"))
        self.filmNumberToLoad = self.model.data(filmIdx)
        self.accept()
        #QMessageBox.warning(None, "FilmNumber", unicode(self.model.data(filmIdx)))

    def onSelectionChanged(self, current, previous):
        if self.uiFilmListTableV.selectionModel().hasSelection():
            self.uiDisplayFlightPathBtn.setEnabled(True)
        else:
            self.uiDisplayFlightPathBtn.setEnabled(False)
        #QMessageBox.warning(None, "FilmNumber", "selection Changed")

    def checkSelection(self):
        if self.uiFilmListTableV.selectionModel().hasSelection():
            # Export selected or all items
            msgBox = QMessageBox()
            msgBox.setWindowTitle(u'Filme als PDF speichern')
            msgBox.setText(u'Wollen Sie die ausgewählten Filme oder die gesamte Liste als PDF speichern?')
            msgBox.addButton(QPushButton(u'Auswahl'), QMessageBox.YesRole)
            msgBox.addButton(QPushButton(u'Gesamte Liste'), QMessageBox.NoRole)
            msgBox.addButton(QPushButton(u'Abbrechen'), QMessageBox.RejectRole)
            ret = msgBox.exec_()

            return ret
        else:
            return 1

    def _generateWeatherCode(self, weatherCode):
        categories = ["Low Cloud Amount", "Visibility Kilometres", "Low Cloud Height", "Weather", "Remarks Mission", "Remarks Weather"]
        query = QSqlQuery(self.dbm.db)
        pos = 0
        help = 0
        weatherDescription = ""
        for c in weatherCode:
            qryStr = "select description from wetter where category = '{0}' and code = '{1}' limit 1".format(categories[pos-help], c)
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

    def exportDetailsAsPdf(self):

        selection = self.checkSelection()
        query = QSqlQuery(self.dbm.db)


        if selection == 0:
            filmList = self.getFilmList(False)
        elif selection == 1:
            filmList = self.getFilmList(True)
        else:
            return

        if filmList:
            saveDir = self.settings.value("APIS/working_dir", QDir.home().dirName())
            fileNames = []
            if len(filmList) <= 1:
                fn = u"Filmdetails_{0}".format(filmList[0])
            else:
                fn = u"Filmdetails_Sammlung"

            fileName = QFileDialog.getSaveFileName(self, u"Filmdetails speichern", saveDir + "\\" + '{0}_{1}'.format(fn,QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")), '*.pdf')

            if not fileName:
                return

            #Query Film Details!

            qryStr = "select * from film where filmnummer in ({0})".format("'"+"','".join(filmList)+"'")
            query.exec_(qryStr)



        #filmId = filmList[0]
        #if fileName:
            tempFileNames = []
            while query.next():

                filmDict = {}
                rec = query.record()
                for col in range(rec.count()):
                    val = unicode(rec.value(col))
                    if val.replace(" ", "")=='' or val=='NULL':
                        val = u"---"

                    filmDict[unicode(rec.fieldName(col))] = val

                filmDict['wetter_description'] = self._generateWeatherCode(filmDict['wetter'])
                filmDict['datum_druck'] =  QDate.currentDate().toString("yyyy-MM-dd")


                #for filmId in filmList:
                #QMessageBox.warning(None, "Save", fileName)
                #FIXME template from Settings ':/plugins/APIS/icons/settings.png'
                template = os.path.dirname(__file__) + "/composer/templates/FilmDetails.qpt" #':/plugins/APIS/composer/templates/FilmDetails.gpt' #'C:/Users/Johannes/.qgis2/python/plugins/APIS/composer/templates/FilmDetails.qpt'
                #if os.path.isfile(template):
                templateDOM = QDomDocument()
                templateDOM.setContent(QFile(template), False)

                #FIXME load correct Flightpath; from Settings
                printLayers = []
                flightpathDir = self.settings.value("APIS/flightpath_dir")
                #uri = flightpathDir + "\\2014\\02140301_lin.shp"
                uri = flightpathDir + "\\" + filmDict['flugdatum'][:4] + "\\" + filmDict["filmnummer"] + "_lin.shp"
                if not os.path.isfile(uri):
                    uri = flightpathDir + "\\2014\\02140301_lin.shp"
                printLayer = QgsVectorLayer(uri, "FlightPath", "ogr")
                QgsMapLayerRegistry.instance().addMapLayer(printLayer, False) #False = don't add to Layers (TOC)
                printLayer.updateExtents()
                extent = printLayer.extent()

                #layerset.append(printLayer.id())
                printLayers.append(printLayer.id())

                #urlWithParams = ' '
                #urlWithParams = 'url=http://wms.jpl.nasa.gov/wms.cgi&layers=global_mosaic&styles=pseudo&format=image/jpeg&crs=EPSG:4326'
                #rlayer = QgsRasterLayer(urlWithParams, 'basemap', 'wms')
                #QgsMapLayerRegistry.instance().addMapLayer(rlayer)
                #printLayers.append(rlayer.id())

                ms = QgsMapSettings()
                ms.setExtent(extent)
                #mr.setLayerSet(layerset)

                #mapRectangle = QgsRectangle(140,-28,155,-15)
                #mr.setExtent(extent)

                comp = QgsComposition(ms)
                comp.setPlotStyle(QgsComposition.Print)
                comp.setPrintResolution(300)

                #m = self.mapper.model()
                #r = self.mapper.currentIndex()
                #filmDict = {'filmnummer':filmId}
               # for c in range(m.columnCount()):
                    #filmDict[m.headerData(c, Qt.Horizontal)] = unicode(m.data(m.createIndex(r, c)))
                    #QMessageBox.warning(None, "Save", "{0}:{1}".format(colName, value))


                comp.loadFromTemplate(templateDOM, filmDict)

                composerMap = comp.getComposerMapById(0)
                composerMap.setKeepLayerSet(True)
                composerMap.setLayerSet(printLayers)
                #composerMap.renderModeUpdateCachedImage()
                #ms.setLayers(printLayers)

                #if composerMap:
                    #QMessageBox.warning(None, "Save", composerMap)
               #composerMap.setKeepLayerSet(True)
                #composerMap.setLayerSet(layerset)


                if len(filmList) > 1:
                    tempFileName = fileName + "." + filmDict["filmnummer"] + ".pdf"
                    comp.exportAsPDF(tempFileName)
                    tempFileNames.append(tempFileName)
                else:
                    comp.exportAsPDF(fileName)
                #FIXME: Delete all alyers (array) not just one layer
                QgsMapLayerRegistry.instance().removeMapLayer(printLayer.id())
                #QgsMapLayerRegistry.instance().removeMapLayer(rlayer.id())

            if tempFileNames:
                #merge pdfs
                merger = PdfFileMerger()
                for filename in tempFileNames:
                    merger.append(PdfFileReader(file(filename, 'rb')))

                merger.write(fileName)

                for filename in tempFileNames:
                    try:
                        os.remove(filename)
                    except Exception, e:
                        continue

            try:
                if sys.platform == 'linux2':
                    subprocess.call(["xdg-open", fileName])
                else:
                    os.startfile(fileName)
            except Exception, e:
                pass

    def exportListAsPdf(self):

        selection = self.checkSelection()

        if selection == 0:
            filmList = self.getFilmListWithRows(False)
        elif selection == 1:
            filmList = self.getFilmListWithRows(True)
        else:
            return

        #fileName = 'C:\\apis\\temp\\BildListe.pdf'
        saveDir = self.settings.value("APIS/working_dir", QDir.home().dirName())
        fileName = QFileDialog.getSaveFileName(self, 'Filmliste Speichern', saveDir + "\\" + 'Filmliste_{0}'.format(QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")), '*.pdf')



        if fileName:

            ms = QgsMapSettings()
            comp = QgsComposition(ms)
            comp.setPlotStyle(QgsComposition.Print)
            comp.setPrintResolution(300)
            comp.setPaperSize(297.0, 210.0)

            #header
            hHight = 15
            fHight = 15
            margin = 15
            mTab = 5
            hWidth = comp.paperWidth()/2-margin
            fWidth = (comp.paperWidth()-(2*margin))/3

            page = 1
            prevPage = 0
            filmCount = 0
            filmCountTotal = 0
            pageBreak = 25
            for filmRow in filmList:
                filmCountTotal += 1
                filmCount += 1
                if filmCount > pageBreak:
                    filmCount = 1
                    page += 1
                if page > prevPage:
                    prevPage = page
                    #Header Left - Title
                    hLeft = QgsComposerLabel(comp)
                    hLeft.setItemPosition(margin, margin, hWidth , hHight, QgsComposerItem.UpperLeft, False, page)
                    hLeft.setBackgroundEnabled(True)
                    hLeft.setBackgroundColor(QColor("#CCCCCC"))
                    hLeft.setText(u"Filmliste")
                    hLeft.setVAlign(Qt.AlignVCenter)
                    hLeft.setMarginX(5)
                    hLeft.setFont(QFont("Arial", 16, 100))
                    comp.addItem(hLeft)
                    #Header Right - Stats
                    hRight = QgsComposerLabel(comp)
                    hRight.setItemPosition(comp.paperWidth()/2, margin, hWidth , hHight, QgsComposerItem.UpperLeft, False, page)
                    hRight.setBackgroundEnabled(True)
                    hRight.setBackgroundColor(QColor("#CCCCCC"))
                    hRight.setText(u"Anzahl:\t{0}".format(len(filmList)))
                    hRight.setVAlign(Qt.AlignVCenter)
                    hRight.setHAlign(Qt.AlignRight)
                    hRight.setMarginX(5)
                    hRight.setFont(QFont("Arial", 8))
                    comp.addItem(hRight)
                    #Footer Left - Institute
                    fLeft = QgsComposerLabel(comp)
                    fLeft.setItemPosition(margin, comp.paperHeight()-margin, fWidth, fHight, QgsComposerItem.LowerLeft, False, page)
                    fLeft.setBackgroundEnabled(True)
                    fLeft.setBackgroundColor(QColor("#CCCCCC"))
                    #FIXME get From Settings!
                    fLeft.setText(u"Luftbildarchiv,\nInstitut für Urgeschichte und Historische Archäologie,\nUniversität Wien")
                    fLeft.setVAlign(Qt.AlignVCenter)
                    fLeft.setMarginX(5)
                    fLeft.setFont(QFont("Arial", 8))
                    comp.addItem(fLeft)
                    #Footer Center - Date
                    fCenter = QgsComposerLabel(comp)
                    fCenter.setItemPosition(margin+fWidth, comp.paperHeight()-margin, fWidth, fHight, QgsComposerItem.LowerLeft, False, page)
                    fCenter.setBackgroundEnabled(True)
                    fCenter.setBackgroundColor(QColor("#CCCCCC"))
                    fCenter.setText(u"{0}".format(QDateTime.currentDateTime().toString("dd.MM.yyyy")))
                    fCenter.setVAlign(Qt.AlignVCenter)
                    fCenter.setHAlign(Qt.AlignHCenter)
                    fCenter.setMarginX(5)
                    fCenter.setFont(QFont("Arial", 8))
                    comp.addItem(fCenter)
                    #Footer Right - PageNumber
                    fRight = QgsComposerLabel(comp)
                    fRight.setItemPosition(margin+(2*fWidth), comp.paperHeight()-margin, fWidth, fHight, QgsComposerItem.LowerLeft, False, page)
                    fRight.setBackgroundEnabled(True)
                    fRight.setBackgroundColor(QColor("#CCCCCC"))
                    fRight.setText(u"Seite {0}".format(page))
                    fRight.setVAlign(Qt.AlignVCenter)
                    fRight.setHAlign(Qt.AlignRight)
                    fRight.setMarginX(5)
                    fRight.setFont(QFont("Arial", 8))
                    comp.addItem(fRight)

                    filmTab = QgsComposerTextTable(comp)
                    filmTab.setShowGrid(True)
                    filmTab.setGridStrokeWidth(0.2)
                    filmTab.setLineTextDistance(1.2)
                    filmTab.setHeaderFont(QFont("Arial",9,100))
                    #imageTab.setHeaderHAlignment(QgsComposerTable.HeaderCenter)
                    hLabels = [u"#", "Filmnummer", "Flugdatum", "Bildanzahl", "Weise", "Art", u"Militärnummer", u"Militärnummer Alt", "Kartiert", "Gescannt"]
                    hLabelsAdjust = []
                    for l in hLabels:
                        hLabelsAdjust.append(l.ljust(12))
                    # colProps = QgsComposerTableColumn()
                    # props = QDomElement()
                    # props.setAttribute("hAlignment", 4)
                    # props.setAttribute("vAlignment", 128)
                    # props.setAttribute("heading", "Nummer")
                    # props.setAttribute("attribute", "" )
                    # props.setAttribute("sortByRank", 0 )
                    # props.setAttribute("sortOrder", 0 )
                    # props.setAttribute("width", "100.0" )
                    # colProps.readXML(props)
                    # imageTab.setColumns([colProps])

                    filmTab.setHeaderLabels(hLabelsAdjust)
                    filmTab.setItemPosition(margin+mTab,margin+hHight+mTab, QgsComposerItem.UpperLeft, page)
                    comp.addItem(filmTab)

                if filmRow[3] == u"senk.":
                    fromTable = 'luftbild_senk_cp'
                    spatialIndicator = 'massstab'
                elif filmRow[3] == u"schräg":
                    fromTable = 'luftbild_schraeg_cp'
                filmid = filmRow[0]

                #QMessageBox.warning(None, "Bild", u"{0}, {1}".format(filmid, fromTable))

                query = QSqlQuery(self.dbm.db)
                qryStr = "select count(*) from {0} WHERE filmnummer = '{1}'".format(fromTable, filmid)
                query.exec_(qryStr)
                query.first()
                mappedImages = query.value(0)

                #imageDir = self.settings.value("APIS/image_dir")
                #filmDirName = imageDir + "\\{0}".format(self.filmToFilmLegacy(filmid))
                #filmDir = QDir(filmDirName)
                #scanns = len(filmDir.entryList([self.filmToFilmLegacy(filmid)+"_*.jpg"], QDir.Files))
                scanns = self.imageRegistry.hasImageRE(self.filmToFilmLegacy(filmid)+"_.+")

                #imageTab.addRow([str(imageCountTotal).zfill(len(str(len(imageList))))])
                filmTab.addRow([str(filmCountTotal).zfill(len(str(len(filmList))))] + [unicode(item) for item in filmRow] + [unicode(mappedImages), unicode(scanns)])

                # if imageCount == pageBreak or imageCount == len(imageList):
                #     w = imageTab.rect().width()
                #     QMessageBox.warning(None, "Bild", u"{0}".format(w))
                #     hLabels = [u"ABC", "Bildnummer", "Filmnummer", u"Maßstab", "Weise", "Art","Scan","HiRes","Ortho"]
                #     imageTab.setHeaderLabels(hLabels)

            comp.setNumPages(page)

            #header.setItemPosition(0,0,comp.paperWidth(), 20, QgsComposerItem.UpperLeft, False, 1)

            #footer
            # footer = QgsComposerItemGroup(comp)
            # left = QgsComposerLabel(comp)
            # left.setText(u"Luftbildarchiv - Institut für Urgeschichte und Historische Archäologie, Universität Wien")
            # footer.addItem(left)
            # footer.setBackgroundEnabled(True)
            # footer.setBackgroundColor(QColor('#ab23c9'))
            # footer.setItemPosition(0,comp.paperHeight(), comp.paperWidth(), 100, QgsComposerItem.LowerLeft,  False, 1)


            #comp.moveItemToTop(header)
            #comp.addItem(footer)
            #comp.moveItemToBottom(footer)

            comp.exportAsPDF(fileName)

            try:
                if sys.platform == 'linux2':
                    subprocess.call(["xdg-open", fileName])
                else:
                    os.startfile(fileName)
            except Exception, e:
                pass

    def filmToFilmLegacy(self, film):
        mil = ""
        if film[2:4] == "19":
            mil = "01"
        elif film[2:4] == "20":
            mil = "02"
        return mil + film[4:]

    def onAccepted(self):
        self.accept()