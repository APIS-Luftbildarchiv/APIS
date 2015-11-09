# -*- coding: utf-8 -*

from PyQt4.QtCore import *
import re, json

class ApisImageRegistry():

    def __init__(self):

        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)

        self.registryFile = self.settings.value("APIS/image_registry_file", None)

        self.imageDirName = self.settings.value("APIS/image_dir")
        self.orthoDirName = self.settings.value("APIS/ortho_image_dir")
        self.imageDir = QDir(self.imageDirName)
        self.orthoDir = QDir(self.orthoDirName)

        self.hiResFormats = self.settings.value("APIS/hires_formats", [u'jpg', u'tif', u'sid', u'nef', u'raf', u'cr2', u'dng'])
        self.orthoFormats = self.settings.value("APIS/ortho_formats", [u'jpg', u'tif', u'sid'])

        if self.registryFile:
            self.loadRegistryFromFile()
        else:
            self.updateRegistries()
            self.writeRegistryToFile()

    def loadRegistryFromFile(self):
        #load self.__imageRegistry, self.__hiResRegistry, self.__orthoRegistry from JSON File
        pass

    def writeRegistryToFile(self):
        # write self.__imageRegistry, self.__hiResRegistry, self.__orthoRegistry to JSON File
        # does registry file exist

        with open('C:\\apis\\image_registry.json', 'w') as f:
            registryDict = {
                "imageRegistry" : self.__imageRegistry,
                "hiResRegistry" : self.__hiResRegistry,
                "orthoRegistry" : self.__orthoRegistry
            }
            json.dump(registryDict, f)

    def isOutdated(self):
        # Registry is Outdated > if local File is older than one month!
        # If isOutdated > PopUp > Info: Local Image Registry is outdated > Please Update Image Registry
        # This will take about a minute, please be patient!
        pass

    def updateRegistries(self):
        self.updateImageRegistries()
        self.updateOrthoRegistry()

    def updateImageRegistries(self):
        self.__imageRegistry = []
        self.__hiResRegistry = []
        self.imageEntryList = self.imageDir.entryList(['????????'], QDir.Dirs)
        for i in self.imageEntryList:
            iDir = QDir(self.imageDir.path() + '\\' + i)
            iEntryList = iDir.entryList([i + '_???.jpg'], QDir.Files)
            self.__imageRegistry = self.__imageRegistry + iEntryList

            hiResEntryList = iDir.entryList(["highres*", "mrsid", "raw"], QDir.Dirs)
            hiResFilters = [i + '_???.' + ext for ext in self.hiResFormats]
            for hr in hiResEntryList:
                hrDir = QDir(iDir.path() + '\\' + hr)
                hrEntryList = hrDir.entryList(hiResFilters, QDir.Files)
                self.__hiResRegistry = self.__hiResRegistry + hrEntryList

    def updateOrthoRegistry(self):
        import glob, os
        self.__orthoRegistry = []
        self.orthoEntryList = self.orthoDir.entryList(['????????'], QDir.Dirs)
        for o in self.orthoEntryList:
            orthoFilters = [o + '_???_op*.' + ext for ext in self.orthoFormats]
            oDir = QDir(self.orthoDir.path() +'\\' + o)
            oEntryList = oDir.entryList(orthoFilters, QDir.Files)
            self.__orthoRegistry = self.__orthoRegistry + oEntryList

    def hasImage(self, imageNumber):
        r = re.compile(ur'^02140301_050\.jpg$', re.IGNORECASE)
        r = filter(r.match, self.__imageRegistry)
        if r:
            return True
        else:
            return False

    def hasHiRes(self, imageNumber):
        pass

    def hasOrtho(self, imageNumber):
        pass
