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

from PyQt4.QtCore import QSettings, QTranslator
from PyQt4.QtGui import *
# from PyQt4 import uic

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

from apis_utils import ApisUtils

# --------------------------------------------------------
# Settings - Basis Einstellungen für Plugin
# --------------------------------------------------------
from apis_settings_form import *
from functools import partial

class ApisSettingsDialog(QDialog, Ui_apisSettingsDialog):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        # APIS Utils methods
        self.au = ApisUtils(self)

        # Signals/Slot Connections
        self.rejected.connect(self.onReject)
        self.buttonBox.rejected.connect(self.onReject)
        self.buttonBox.accepted.connect(self.onAccept)

        # Selectors for getFileOpenDialogs
        # paths chosen by user
        self.fileSelectors = {
            "uiDatabaseFile" : {
                "button" : self.uiDatabaseFileTBtn,
                "infotext": self.tr(u"Wählen Sie eine APIS Spatialite Datenbank aus ..."),
                "input" : self.uiDatabaseFileEdit
            }
        }
        for key, item in self.fileSelectors.items():
            control = item['button']
            slot = partial(self.au.callOpenFileDialog, key)
            control.clicked.connect(slot)

        # Selectors for ExistPathDialogs
        # paths chosen by user
        self.directorySelectors = {
            "aerialImageDir" : {
                "button" : self.uiAerialImageDirTBtn,
                "infotext": self.tr(u"Wählen Sie den Pfad zu den Luftbildern aus ..."),
                "input" : self.uiAerialImageDirEdit
            },
            "orthoPhotoDir" : {
                "button" : self.uiOrthoPhotoDirTBtn,
                "infotext": self.tr(u"Wählen Sie den Pfad zu den Orthofotos aus .."),
                "input" : self.uiOrthoPhotoDirEdit
            }
        }
        for key, item in self.directorySelectors.items():
            control = item['button']
            slot = partial(self.au.callOpenDirectoryDialog, key)
            control.clicked.connect(slot)

    def onAccept(self):
        '''
        Check DB
        Save options when pressing OK button
        Update Plugin Status
        '''

        # Save Settings
        s = QSettings()



        self.accept()

    def onReject(self):
        '''
        Run some actions when
        the user closes the dialog
        '''
        self.close()


# --------------------------------------------------------
# Film - Eingabe, Pflege
# --------------------------------------------------------
from apis_film_form import *

class ApisFilmDialog(QDialog, Ui_apisFilmDialog):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
