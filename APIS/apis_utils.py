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
        value = s.value("APIS/plugin_config_status", False)
        if isinstance(value, (bool)):
            return value
        else:
            return value.lower() in ("yes", "true", "t", "1")


