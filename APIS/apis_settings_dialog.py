# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ApisDialog
                                 A QGIS plugin
 QGIS Plugin for APIS
                             -------------------
        begin                : 2015-04-10
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Johannes Liem/Luftbildarchiv Uni Wien
        email                : johannes.liem@digitalcartography.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4.QtCore import * #QSettings, QTranslator, QString
from PyQt4.QtGui import *
from PyQt4.QtSql import *
# from PyQt4 import uic

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

from apis_utils import *
from apis_image_registry import *

# --------------------------------------------------------
# Settings - Basis Einstellungen für Plugin
# --------------------------------------------------------
from apis_settings_form import *
from functools import partial

class ApisSettingsDialog(QDialog, Ui_apisSettingsDialog):
    def __init__(self, iface, imageRegistry):
        QDialog.__init__(self)
        self.iface = iface
        self.imageRegistry = imageRegistry
        self.setupUi(self)

        s = QSettings()

        # APIS Utils methods
        # self.au = ApisUtils(self)

        # Signals/Slot Connections
        self.rejected.connect(self.onReject)
        self.buttonBox.rejected.connect(self.onReject)
        self.buttonBox.accepted.connect(self.onAccept)

        self.buttonBox.button(QDialogButtonBox.Reset).clicked.connect(self.onReset)

        self.uiUpdateImageRegistryBtn.clicked.connect(self.updateImageRegistry)

        # Selectors for getFileOpenDialogs
        # paths chosen by user
        self.fileSelectors = {
            # "uiDatabaseFile" : {
            #     "button" : self.uiDatabaseFileTBtn,
            #     "infotext" : self.tr(u"Wählen Sie eine APIS Spatialite Datenbank aus ..."),
            #     "input" : self.uiDatabaseFileEdit,
            #     "path" : s.value("APIS/database_file", ""),
            #     "filter" : None
            # },
            "uiConfigIniFile" : {
                "button" : self.uiConfigIniFileTBtn,
                "infotext" : self.tr(u"Wählen Sie eine APIS INI Datei aus ..."),
                "input" : self.uiConfigIniFileEdit,
                "path" : s.value("APIS/config_ini", ""),
                "filter" : self.tr("Config INI (*.ini)")
            }
        }
        for key, item in self.fileSelectors.items():
            input = item['input']
            input.setText(unicode(item['path']))
            control = item['button']
            slot = partial(self.callOpenFileDialog, key)
            control.clicked.connect(slot)

        # Selectors for ExistPathDialogs
        # paths chosen by user
        # self.directorySelectors = {
        #     "aerialImageDir" : {
        #         "button" : self.uiAerialImageDirTBtn,
        #         "infotext" : self.tr(u"Wählen Sie den Pfad zu den Luftbildern aus ..."),
        #         "input" : self.uiAerialImageDirEdit
        #     },
        #     "orthoPhotoDir" : {
        #         "button" : self.uiOrthoPhotoDirTBtn,
        #         "infotext" : self.tr(u"Wählen Sie den Pfad zu den Orthofotos aus .."),
        #         "input" : self.uiOrthoPhotoDirEdit
        #     }
        # }
        # for key, item in self.directorySelectors.items():
        #     control = item['button']
        #     slot = partial(self.callOpenDirectoryDialog, key)
        #     control.clicked.connect(slot)

        #Load Settings from QSettings

    def setImageRegistry(self, imageRegistry):
        self.imageRegistry = imageRegistry

    def updateImageRegistry(self):
        self.imageRegistry.updateRegistries()

    def callOpenFileDialog(self, key):
        """
        Ask the user to select a file
        and write down the path to appropriate field
        """
        inPath = QFileDialog.getOpenFileName(
            None,
            self.fileSelectors[key]['infotext'],
            str(self.fileSelectors[key]['input'].text().encode('utf-8')).strip(' \t'),
            self.fileSelectors[key]['filter'],

        )
        if os.path.exists(unicode(inPath)):
            self.fileSelectors[key]['input'].setText(unicode(inPath))

    # def callOpenDirectoryDialog(self, key):
    #     """
    #     Ask the user to select a folder
    #     and write down the path to appropriate field
    #     """
    #     inPath = QFileDialog.getExistingDirectory(
    #         None,
    #         self.directorySelectors[key]['infotext'],
    #         str(self.directorySelectors[key]['input'].text().encode('utf-8')).strip(' \t')
    #     )
    #     if os.path.exists(unicode(inPath)):
    #         self.directorySelectors[key]['input'].setText(unicode(inPath))

    def onAccept(self):
        '''
        Check DB
        Save options when pressing OK button
        Update Plugin Status
        '''

        # Save Settings
        s = QSettings()
        if len(self.uiConfigIniFileEdit.text()) > 0:
            s.setValue("APIS/config_ini", self.uiConfigIniFileEdit.text())
        #
        # sApis = QSettings(s.value("APIS/config_ini"),  QSettings.IniFormat)
        # #keys = sApis.allKeys()
        # requiredKeysIsFile = ['database_file']
        # requiredKeysIsDir = ['flightpath_dir', 'image_dir', 'ortho_image_dir', 'repr_image_dir', 'insp_image_dir', 'site_image_dir', 'oek50_bmn_dir', 'oek50_utm_dir']
        # requiredKeys = ['hires_vertical', 'hires_oblique_digital', 'hires_oblique_analog']
        #
        # requiredKeysStatus = True
        # errorKeys = []
        # for k in requiredKeysIsFile:
        #     key = "APIS/"+k
        #     if not sApis.contains(key)or not os.path.isfile(sApis.value(key)):
        #         requiredKeysStatus = False
        #         errorKeys.append(k)
        #
        # for k in requiredKeysIsDir:
        #     key = "APIS/"+k
        #     if not sApis.contains(key) or not os.path.isdir(sApis.value(key)):
        #         requiredKeysStatus = False
        #         errorKeys.append(k)
        #
        # for k in requiredKeys:
        #      key = "APIS/"+k
        #      if not sApis.contains(key):
        #          requiredKeysStatus = False
        #          errorKeys.append(k)
        #
        # if not requiredKeysStatus:
        #     QMessageBox.warning(None, self.tr(u"Konfiguration"), u"Folgende Schlüssel in der INI Datei sind nicht korrekt oder nicht vorhanden: {0}".format(', '.join(errorKeys)))
        #     self.callOpenFileDialog("uiConfigIniFile")
        #     return
            #Warnung INI FIle passt nicht

        #QMessageBox.warning(None, self.tr(u"config"), sApis.applicationName() + ' ' + ', '.join(keys))
        #QMessageBox.warning(None, self.tr(u"config"), "test")

        #check if all required settings are set in ini file

        self.accept()

    def onReject(self):
        '''
        Run some actions when
        the user closes the dialog
        '''
        self.close()

    def onReset(self):
        '''
        Delte Settings
        '''
        s = QSettings()
        s.remove("APIS/config_ini")
        self.uiConfigIniFileEdit.clear()


