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
from apis_text_editor_form import *
from functools import partial

class ApisTextEditorDialog(QDialog, Ui_apisTextEditorDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)


        # Signals/Slot Connections
        self.rejected.connect(self.onReject)
        self.buttonBox.rejected.connect(self.onReject)
        self.buttonBox.accepted.connect(self.onAccept)

    def setText(self, text):
        self.uiTextPTxt.setPlainText(text)

    def getText(self):
        return self.uiTextPTxt.toPlainText()

    def onAccept(self):
        '''
        Check DB
        Save options when pressing OK button
        Update Plugin Status
        '''

        self.accept()

    def onReject(self):
        '''
        Run some actions when
        the user closes the dialog
        '''
        self.close()



