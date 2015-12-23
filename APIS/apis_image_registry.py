# -*- coding: utf-8 -*

from PyQt4.QtCore import *
from PyQt4.QtGui import QMessageBox, QPushButton, QProgressBar
from qgis.gui import QgsMessageBar
import re, json, os, datetime

class ApisImageRegistry():

    def __init__(self, pluginDir, iface):

        self.iface = iface

        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)

        self.registryFile = pluginDir + "\\" + "apis_image_registry.json" #self.settings.value("APIS/image_registry_file", None)

        self.imageDirName = self.settings.value("APIS/image_dir")
        self.orthoDirName = self.settings.value("APIS/ortho_image_dir")
        self.imageDir = QDir(self.imageDirName)
        self.orthoDir = QDir(self.orthoDirName)

        self.imageFormats = self.settings.value("APIS/image_formats", [u'jpg'])
        self.hiResFormats = self.settings.value("APIS/hires_formats", [u'jpg', u'tif', u'sid', u'nef', u'raf', u'cr2', u'dng'])
        self.orthoFormats = self.settings.value("APIS/ortho_formats", [u'jpg', u'tif', u'sid'])

        self.imageFormatsStr = u"|".join(self.imageFormats)
        self.hiResFormatsStr = u"|".join(self.hiResFormats)
        self.orthoFormatsStr = u"|".join(self.orthoFormats)

        self.__imageRegistryNE = None
        self.__hiResRegistryNE = None
        self.__orthoRegistryNE = None
        self.__imageRegistry = None
        self.__hiResRegistry = None
        self.__orthoRegistry = None

        self.loaded = False

    def setupRegistry(self):
        if self.registryFile and os.path.isfile(self.registryFile):
            if self.isOutdated():
                # If isOutdated > PopUp > Info: Local Image Registry is outdated > Please Update Image Registry
                # ask if update ImageRegistry
                msgBox = QMessageBox()
                msgBox.setWindowTitle(u'Image Registry')
                msgBox.setText(u'Die APIS Image Registry ist älter als ein Monat. Bitte führen Sie ein Update durch!')
                msgBox.addButton(QPushButton(u'Update'), QMessageBox.YesRole)
                msgBox.addButton(QPushButton(u'Abbrechen'), QMessageBox.NoRole)
                ret = msgBox.exec_()

                if ret == 0:
                    self.updateRegistries()
                    self.writeRegistryToFile()
                else:
                    self.loadRegistryFromFile()
            else:
                self.loadRegistryFromFile()
        else:
            # ask if generate ImageRegistry
            msgBox = QMessageBox()
            msgBox.setWindowTitle(u'Image Registry')
            msgBox.setText(u'Für die Verwendung von APIS muss eine Image Registry erstellt werden!')
            msgBox.addButton(QPushButton(u'Jetzt erstellen'), QMessageBox.YesRole)
            msgBox.addButton(QPushButton(u'Abbrechen'), QMessageBox.NoRole)
            ret = msgBox.exec_()
            if ret == 0:
                self.updateRegistries()
                self.writeRegistryToFile()
            else:
                self.loaded = False

    def isLoaded(self):
        return self.loaded

    def loadRegistryFromFile(self):
        #load self.__imageRegistry, self.__hiResRegistry, self.__orthoRegistry from JSON File
        if os.path.isfile(self.registryFile):
            with open(self.registryFile,'rU') as registry:
                registryDict = json.load(registry)
                self.__imageRegistryNE = registryDict["imageRegistryNE"]
                self.__hiResRegistryNE = registryDict["hiResRegistryNE"]
                self.__orthoRegistryNE = registryDict["orthoRegistryNE"]
                self.__imageRegistry = registryDict["imageRegistry"]
                self.__hiResRegistry = registryDict["hiResRegistry"]
                self.__orthoRegistry = registryDict["orthoRegistry"]
            self.loaded = True
        else:
            self.loaded = False

    def writeRegistryToFile(self):
        # write self.__imageRegistry, self.__hiResRegistry, self.__orthoRegistry to JSON File
        # does registry file exist
        if os.path.isfile(self.registryFile):
            os.remove(self.registryFile)

        with open(self.registryFile, 'w') as f:
            registryDict = {
                "imageRegistryNE": self.__imageRegistryNE,
                "hiResRegistryNE" : self.__hiResRegistryNE,
                "orthoRegistryNE" : self.__orthoRegistryNE,
                "imageRegistry" : self.__imageRegistry,
                "hiResRegistry" : self.__hiResRegistry,
                "orthoRegistry" : self.__orthoRegistry
            }
            json.dump(registryDict, f)

    def isOutdated(self):
        if os.path.isfile(self.registryFile):
            today = datetime.datetime.today()
            creationDate = datetime.datetime.fromtimestamp(os.path.getctime(self.registryFile))
            fileAge = today - creationDate
            #QMessageBox.warning(None, "Zeit", "{0}".format(fileAge.days))
            if fileAge.days > 30:
                return True
            else:
                return False
            # Registry is Outdated > if local File is older than one month!

    def updateRegistries(self):
        # messageBar!
        mb = self.iface.messageBar().createMessage("Update Image Registry", "Dieser Vorgang kann einige Minute dauern, bitte haben Sie geduld!")
        progress = QProgressBar()
        progress.setMinimum(0)
        progress.setMaximum(0)
        progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        mb.layout().addWidget(progress)
        self.iface.messageBar().pushWidget(mb, QgsMessageBar.INFO)

        self.updateImageRegistries()
        self.updateOrthoRegistry()
        self.iface.messageBar().clearWidgets()
        self.iface.messageBar().pushMessage(u"Update Image Registry", u"Das Update wurde erfolgreich abgeschloßen!", level=QgsMessageBar.SUCCESS, duration=10)
        self.loaded = True
        # This will take about a minute, please be patient!

    def updateImageRegistries(self):
        self.__imageRegistry = []
        self.__hiResRegistry = []
        self.imageEntryList = self.imageDir.entryList(['????????'], QDir.Dirs)
        for i in self.imageEntryList:
            iDir = QDir(self.imageDir.path() + '\\' + i)
            #FIXME implement solution for not just jpg but values from ini
            iEntryList = iDir.entryList([i + '_???.jpg'], QDir.Files)
            self.__imageRegistry = self.__imageRegistry + iEntryList

            hiResEntryList = iDir.entryList(["highres*", "mrsid", "raw"], QDir.Dirs)
            hiResFilters = [i + '_???.' + ext for ext in self.hiResFormats]
            for hr in hiResEntryList:
                hrDir = QDir(iDir.path() + '\\' + hr)
                hrEntryList = hrDir.entryList(hiResFilters, QDir.Files)
                self.__hiResRegistry = self.__hiResRegistry + hrEntryList


        self.__imageRegistryNE = [img[:12].replace('_','.') for img in self.__imageRegistry]

        self.__hiResRegistryNE = [img[:12].replace('_','.') for img in self.__hiResRegistry]

    def updateOrthoRegistry(self):
        import glob, os
        self.__orthoRegistryNE = []
        self.__orthoRegistry = []
        self.orthoEntryList = self.orthoDir.entryList(['????????'], QDir.Dirs)
        for o in self.orthoEntryList:
            orthoFilters = [o + '_???_op*.' + ext for ext in self.orthoFormats]
            oDir = QDir(self.orthoDir.path() +'\\' + o)
            oEntryList = oDir.entryList(orthoFilters, QDir.Files)
            self.__orthoRegistry = self.__orthoRegistry + oEntryList

        self.__orthoRegistryNE = [img[:12].replace('_','.')  for img in self.__orthoRegistry]

    def hasImage(self, imageNumber):
        return True if imageNumber in self.__imageRegistryNE else False

    def hasHiRes(self, imageNumber):
        return True if imageNumber in self.__hiResRegistryNE else False

    def hasOrtho(self, imageNumber):
        return True if imageNumber in self.__orthoRegistryNE else False

    def hasImageRE(self, imageNumber):
        r = re.compile(ur"^{0}\.({1})$".format(imageNumber, self.imageFormatsStr), re.IGNORECASE)
        r = filter(r.match, self.__imageRegistry)
        return len(r)

    def hasHiResRE(self, imageNumber):
        r = re.compile(ur"^{0}\.({1})$".format(imageNumber, self.hiResFormatsStr), re.IGNORECASE)
        r = filter(r.match, self.__hiResRegistry)
        return len(r)

    def hasOrthoRE(self, imageNumber):
        r = re.compile(ur"^{0}_op.+\.({1})$".format(imageNumber, self.orthoFormatsStr), re.IGNORECASE)
        r = filter(r.match, self.__orthoRegistry)
        return len(r)