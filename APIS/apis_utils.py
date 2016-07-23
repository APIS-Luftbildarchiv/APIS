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
from PyQt4.QtSql import QSqlQuery
from qgis.core import QgsGeometry, QgsCoordinateTransform
import os.path, sys, subprocess

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

def apisPluginSettings():
    s = QSettings()
    if s.contains("APIS/config_ini"):
        if os.path.isfile(s.value("APIS/config_ini")):
            return isApisIni(s.value("APIS/config_ini"))
        else:
            #Settings INI as stored does not exist
            return False, u"Ausgewählte APIS INI Datei ({0}) ist nicht vorhanden!".format(s.value("APIS/config_ini"))
    else:
        #Settings INI is not stored
        return False, u"Keine APIS INI Datei ausgewählt! "

def isApisIni(ini):
    s = QSettings(ini, QSettings.IniFormat)
    requiredKeysIsFile = ['database_file']
    requiredKeysIsDir = ['flightpath_dir', 'image_dir', 'ortho_image_dir', 'repr_image_dir', 'insp_image_dir']
    requiredKeys = ['hires_vertical', 'hires_oblique_digital', 'hires_oblique_analog']

    isIni = True
    errorKeys = []
    for k in requiredKeysIsFile:
        key = "APIS/"+k
        if not s.contains(key)or not os.path.isfile(s.value(key)):
            isIni = False
            errorKeys.append(k)

    for k in requiredKeysIsDir:
        key = "APIS/"+k
        if not s.contains(key) or not os.path.isdir(s.value(key)):
            isIni = False
            errorKeys.append(k)

    for k in requiredKeys:
         key = "APIS/"+k
         if not s.contains(key):
             isIni = False
             errorKeys.append(k)

    return isIni, s if isIni else u"Folgende Schlüssel in der INI Datei sind nicht korrekt oder nicht vorhanden: " + u", ".join(errorKeys)

# ---------------------------------------------------------------------------
# Open Files or Folder
# ---------------------------------------------------------------------------

def OpenFileOrFolder(fileOrFolder):
    if os.path.exists(fileOrFolder):
        if sys.platform == 'linux2':
            subprocess.call(["xdg-open", fileOrFolder])
        else:
            os.startfile(fileOrFolder)

# ---------------------------------------------------------------------------
# Common Calculations
# ---------------------------------------------------------------------------

def GetMeridianAndEpsgGK(lon):
    '''
    :param lon: float Longitude in Grad
    :return meridian, epsg: int/long Meridian Streifen, int/long epsg Gauß-Krüger Österreich
    '''
    if lon < 11.8333333333:
        return 28, 31254
    elif lon > 14.8333333333:
        return 34, 31256
    else:
        return 31, 31255


def TransformGeometry(geom, srcCrs, destCrs):
    '''
    :param geom: QgsGeometry Punktgeometrie
    :param srcCrs: QgsCoordinateReferenceSystem Source CRS
    :param destCrs: QgsCoordinateReferenceSystem Destination CRS
    :return:
    '''
    geom.transform(QgsCoordinateTransform(srcCrs, destCrs))
    return geom

# ---------------------------------------------------------------------------
# Common Legacy convertions
# ---------------------------------------------------------------------------

def IdToIdLegacy(id):
    millennium = ""
    if id[2:4] == "19":
        millennium = "01"
    elif id[2:4] == "20":
        millennium = "02"
    return millennium + id[4:]

# ---------------------------------------------------------------------------
# Common DB Checks / Geometry Checks
# ---------------------------------------------------------------------------

# FIXME : relocate to apis_site_dialog.py if only usage is apis_site_dialog:showEvent()
def SiteHasFindSpot(db, siteNumber):
    query = QSqlQuery(db)
    query.prepare(u"SELECT COUNT(*) FROM fundstelle WHERE fundortnummer = '{0}'".format(siteNumber))
    query.exec_()
    query.first()
    return query.value(0)

def SitesHaveFindSpots(db, siteNumbers):
    sites = u", ".join(u"'{0}'".format(siteNumber) for siteNumber in siteNumbers)
    query = QSqlQuery(db)
    query.prepare(u"SELECT COUNT(*) FROM fundstelle WHERE fundortnummer IN ({0})".format(sites)   )
    query.exec_()
    query.first()
    return query.value(0)


def IsFilm(db, filmNumber):
    """
    Checks if filmNumber is a filmNumber in film Table
    :param db: Database
    :param filmNumber: 10 digit filmNumber
    :return:
    """
    query = QSqlQuery(db)
    query.prepare(u"SELECT COUNT(*) FROM film WHERE filmnummer = '{0}'".format(filmNumber))
    query.exec_()
    query.first()
    return query.value(0)
