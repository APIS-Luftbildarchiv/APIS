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

from PyQt4.QtGui import *
# from PyQt4 import uic

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

#FORM_CLASS, _ = uic.loadUiType(os.path.join(
    #  os.path.dirname(__file__), 'apis_dialog_base.ui'))


# class ApisDialog(QDialog, FORM_CLASS):
    # def __init__(self, parent=None):
        # """Constructor."""
        # super(ApisDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        # self.setupUi(self)

from apis_settings_form import *

class ApisSettingsDialog(QDialog, Ui_apisSettingsDialog):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

from apis_film_form import *

class ApisFilmDialog(QDialog, Ui_apisFilmDialog):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
