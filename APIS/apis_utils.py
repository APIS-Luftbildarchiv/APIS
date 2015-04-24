# -*- coding: utf-8 -*-
"""
/***************************************************************************
 APIS
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

from PyQt4.QtCore import QSettings, QTranslator
from PyQt4.QtGui import *
import os.path

class ApisUtils:
    def __init__(self, dialog):
        self.dialog = dialog

    def checkConfigStatus(self):
        s = QSettings()
        return s.value("APIS/plugin_config_status", True)

    def callOpenFileDialog(self, key):
        """
        Ask the user to select a file
        and write down the path to appropriate field
        """
        inPath = QFileDialog.getOpenFileName(
            None,
            self.dialog.fileSelectors[key]['infotext'],
            str(self.dialog.fileSelectors[key]['input'].text().encode('utf-8')).strip(' \t')
        )
        if os.path.exists(unicode(inPath)):
            self.dialog.fileSelectors[key]['input'].setText(unicode(inPath))

    def callOpenDirectoryDialog(self, key):
        """
        Ask the user to select a folder
        and write down the path to appropriate field
        """
        inPath = QFileDialog.getExistingDirectory(
            None,
            self.dialog.directorySelectors[key]['infotext'],
            str(self.dialog.directorySelectors[key]['input'].text().encode('utf-8')).strip(' \t')
        )
        if os.path.exists(unicode(inPath)):
            self.dialog.directorySelectors[key]['input'].setText(unicode(inPath))

