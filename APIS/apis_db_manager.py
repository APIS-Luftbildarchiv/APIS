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
from PyQt4.QtCore import *
from PyQt4.QtGui import QMessageBox
from PyQt4.QtSql import *

class ApisDbManager:
    def __init__(self, path):
        self.connectToDb("QSPATIALITE", path)

    def connectToDb(self, type, path):
        self.__db = QSqlDatabase.addDatabase(type)
        self.__db.setDatabaseName(path)
        if not self.__db.open():
            #QMessageBox.warning(None, "Combo Box Example", "Database Error: {0}".format(self.__db.lastError().text())
            #sys.exit(1)
            pass

    @property
    def db(self):
        return self.__db