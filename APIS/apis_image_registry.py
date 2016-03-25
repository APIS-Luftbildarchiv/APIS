# -*- coding: utf-8 -*

from PyQt4.QtCore import QSettings, QDir, Qt, QThread, QObject, pyqtSignal
from PyQt4.QtGui import QMessageBox, QPushButton, QProgressBar, QWidget
from qgis.core import QgsMessageLog
from qgis.gui import QgsMessageBar, QgsMessageBarItem

import re, json, os, datetime, sys
import traceback


class ApisImageRegistry(QObject):

    loaded = pyqtSignal(object)

    def __init__(self, pluginDir, iface):

        QObject.__init__(self)

        self.iface = iface
        self.registryFile = pluginDir + "\\" + "apis_image_registry.json" #self.settings.value("APIS/image_registry_file", None)

        self.__imageRegistryNE = None
        self.__hiResRegistryNE = None
        self.__orthoRegistryNE = None
        self.__imageRegistry = None
        self.__hiResRegistry = None
        self.__orthoRegistry = None

        self.isLoaded = False
        self.isSetup = False

        self.worker = None

    def setupSettings(self):
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)

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

        self.isSetup = True

    def registryIsSetup(self):
        return self.isSetup

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
            else:
                self.isLoaded = False

    def registryIsLoaded(self):
        return self.isLoaded

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
            self.isLoaded = True
            self.loaded.emit(True)
        else:
            self.isLoaded = False

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
            modificationDate = datetime.datetime.fromtimestamp(os.path.getmtime(self.registryFile))
            if modificationDate > creationDate:
                fileAge = today - modificationDate
            else:
                fileAge = today - creationDate
            #QMessageBox.warning(None, "Zeit", "{0}".format(fileAge.days))
            if fileAge.days > 30:
                return True
            else:
                return False
            # Registry is Outdated > if local File is older than one month!

    def updateRegistries(self):
        self.startWorker()

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

    def startWorker(self):
        # create a new worker instance

        if self.worker is None:

            worker = UpdateRegistryWorker()

            # configure the QgsMessageBar
            messageBar = self.iface.messageBar().createMessage(u"Update Image Registry", u"Dieser Vorgang kann einige Minute dauern, bitte haben Sie geduld!")
            progressBar = QProgressBar()
            progressBar.setMinimum(0)
            progressBar.setMaximum(0)
            progressBar.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            cancelButton = QPushButton()
            cancelButton.setText('Cancel')
            cancelButton.clicked.connect(self.killWorker)
            messageBar.layout().addWidget(progressBar)
            self.progressBar = progressBar
            messageBar.layout().addWidget(cancelButton)
            self.iface.messageBar().pushWidget(messageBar, self.iface.messageBar().INFO)
            #self.iface.messageBar().widgetRemoved
            # messageBar

            self.messageBar = messageBar

            # start the worker in a new thread
            thread = QThread()
            worker.moveToThread(thread)
            worker.finished.connect(self.workerFinished)
            worker.error.connect(self.workerError)
            #worker.progress.connect(progressBar.setValue)
            thread.started.connect(worker.run)
            thread.start()
            self.thread = thread
            self.worker = worker

    def killWorker(self):
        self.worker.kill()
        #self.progressBar.setMaximum(100)
        #self.progressBar.setValue(100)

    def workerFinished(self, ret):
        # clean up the worker and thread
        self.worker.deleteLater()
        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()
        # remove widget from message bar
        self.iface.messageBar().popWidget(self.messageBar)
        if ret is not None:
            #report the result
            if not self.worker.killed:
                self.__imageRegistryNE = ret["imageRegistryNE"]
                self.__hiResRegistryNE = ret["hiResRegistryNE"]
                self.__orthoRegistryNE = ret["orthoRegistryNE"]
                self.__imageRegistry = ret["imageRegistry"]
                self.__hiResRegistry = ret["hiResRegistry"]
                self.__orthoRegistry = ret["orthoRegistry"]
                self.writeRegistryToFile()

                self.iface.messageBar().pushMessage(u"Update Image Registry", u"Das Update wurde erfolgreich abgeschloßen!", level=QgsMessageBar.SUCCESS, duration=5)
                self.isLoaded = True
                self.loaded.emit(True)
            else:
                self.iface.messageBar().pushMessage(u"Update Image Registry", u"Das Update wurde abgebrochen!", level=QgsMessageBar.WARNING, duration=5)
                if os.path.isfile(self.registryFile):
                    os.remove(self.registryFile)
                self.isLoaded = False
                self.loaded.emit(False)
            #self.iface.messageBar().pushMessage('Result')
        else:
            # notify the user that something went wrong
            self.iface.messageBar().pushMessage('Something went wrong! See the message log for more information.', level=QgsMessageBar.CRITICAL, duration=3)
            self.isLoaded = False
        self.worker = None

    def workerError(self, e, exception_string):
        QgsMessageLog.logMessage('APIS UpdateRegistryWorker thread raised an exception:\n'.format(exception_string), level=QgsMessageLog.CRITICAL)

class UpdateRegistryWorker(QObject):
    '''Background worker for updating Image Registry'''

    def __init__(self):
        QObject.__init__(self)
        self.killed = False
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)

        #self.registryFile = pluginDir + "\\" + "apis_image_registry.json" #self.settings.value("APIS/image_registry_file", None)

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

    def run(self):
        try:
            self.updateImageRegistries()
            self.updateOrthoRegistry()
            #import time
            #for i in range(5000):
                #if self.killed is True:
                    # kill request received, exit loop early
                    #break
                #time.sleep(0.001)

            if self.killed is False:
                ret = True
                ret = {
                    "imageRegistryNE": self.imageRegistryNE,
                    "hiResRegistryNE" : self.hiResRegistryNE,
                    "orthoRegistryNE" : self.orthoRegistryNE,
                    "imageRegistry" : self.imageRegistry,
                    "hiResRegistry" : self.hiResRegistry,
                    "orthoRegistry" : self.orthoRegistry
                }
            else:
                ret = False
        except Exception, e:
            # forward the exception upstream
            self.error.emit(e, traceback.format_exc())
        self.finished.emit(ret)

    def kill(self):
        self.killed = True

    def updateImageRegistries(self):
        self.imageRegistry = []
        self.hiResRegistry = []
        self.imageEntryList = self.imageDir.entryList(['????????'], QDir.Dirs)
        for i in self.imageEntryList:
            if self.killed is True:
                # kill request received, exit loop early
                break
            iDir = QDir(self.imageDir.path() + '\\' + i)
            #FIXME implement solution for not just jpg but values from ini
            iEntryList = iDir.entryList([i + '_???.jpg'], QDir.Files)
            self.imageRegistry = self.imageRegistry + iEntryList

            hiResEntryList = iDir.entryList(["highres*", "mrsid", "raw"], QDir.Dirs)
            hiResFilters = [i + '_???.' + ext for ext in self.hiResFormats]
            for hr in hiResEntryList:
                if self.killed is True:
                    # kill request received, exit loop early
                    break
                hrDir = QDir(iDir.path() + '\\' + hr)
                hrEntryList = hrDir.entryList(hiResFilters, QDir.Files)
                self.hiResRegistry = self.hiResRegistry + hrEntryList

        if self.killed is False:
            self.imageRegistryNE = [img[:12].replace('_','.') for img in self.imageRegistry]
            self.hiResRegistryNE = [img[:12].replace('_','.') for img in self.hiResRegistry]

    def updateOrthoRegistry(self):
        import glob, os
        self.orthoRegistryNE = []
        self.orthoRegistry = []
        self.orthoEntryList = self.orthoDir.entryList(['????????'], QDir.Dirs)
        for o in self.orthoEntryList:
            if self.killed is True:
                # kill request received, exit loop early
                break
            orthoFilters = [o + '_???_op*.' + ext for ext in self.orthoFormats]
            oDir = QDir(self.orthoDir.path() +'\\' + o)
            oEntryList = oDir.entryList(orthoFilters, QDir.Files)
            self.orthoRegistry = self.orthoRegistry + oEntryList
        if self.killed is False:
            self.orthoRegistryNE = [img[:12].replace('_','.')  for img in self.orthoRegistry]

    finished = pyqtSignal(object)
    error = pyqtSignal(Exception, basestring)