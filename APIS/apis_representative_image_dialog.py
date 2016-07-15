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
from apis_representative_image_form import *
from functools import partial

class ApisRepresentativeImageDialog(QDialog, Ui_apisRepresentativeImageDialog):
    def __init__(self, dbm, imageRegistry, currentPath, filmNumber):
        QDialog.__init__(self)
        self.setupUi(self)
        self.dbm = dbm
        self.imageRegistry = imageRegistry
        self.currentPath = currentPath
        self.filmNumber = filmNumber
        self.newPath = currentPath

        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)

        # Signals/Slot Connections
        self.rejected.connect(self.onReject)
        self.buttonBox.rejected.connect(self.onReject)
        self.buttonBox.accepted.connect(self.onAccept)
        self.uiSelectImageFromSystem.clicked.connect(self.selectImageFromSystem)

        self.graphicLoaded = False

        self.scene = QGraphicsScene()
        self.uiRepresentativeImageView.setScene(self.scene)


        # ist FilmProjekt ein FILM?
        if self.isFilm(self.filmNumber):
            self.populateFilmCombo(self.filmNumber)
        else:
            self.populateFilmCombo()
        # wenn nein self.populateFilmCombo()

        self.uiAvailableImagesCombo.currentIndexChanged.connect(self.loadNewImageByFilm)


    def populateFilmCombo(self, filmNumber=None):
        editor = self.uiFilmNumberCombo
        model = QSqlQueryModel(self)
        model.setQuery("SELECT DISTINCT {0} FROM {1} ORDER BY {2}".format('filmnummer', 'film', 'filmnummer'), self.dbm.db)

        tv = QTableView()
        editor.setView(tv)

        tv.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        tv.setSelectionMode(QAbstractItemView.SingleSelection)
        tv.setSelectionBehavior(QAbstractItemView.SelectRows)
        tv.setAutoScroll(False)

        editor.setModel(model)

        editor.setModelColumn(0)
        editor.setInsertPolicy(QComboBox.NoInsert)

        tv.resizeColumnsToContents()
        tv.resizeRowsToContents()
        tv.verticalHeader().setVisible(False)
        tv.horizontalHeader().setVisible(True)
        # tv.setMinimumWidth(tv.horizontalHeader().length())
        tv.horizontalHeader().setResizeMode(QHeaderView.Stretch)

        editor.setAutoCompletion(True)

        if filmNumber:
            editor.setCurrentIndex(editor.findText(filmNumber))
            self.populateAvailableImagesCombo()
        else:
            editor.setCurrentIndex(-1)

        editor.currentIndexChanged.connect(self.populateAvailableImagesCombo)

    def populateAvailableImagesCombo(self, idx=None):
        self.filmNumber = self.uiFilmNumberCombo.currentText()
        # query image registry
        #TODO RM availableImages = self.imageRegistry.getImageRegistryForFilm(IdToIdLegacy(self.filmNumber))
        availableImages = self.imageRegistry.getImageRegistryForFilm(self.filmNumber)
        self.uiAvailableImagesCombo.clear()
        self.uiAvailableImagesCombo.addItems(availableImages)
        self.uiAvailableImagesCombo.setCurrentIndex(-1)


    def isFilm(self, filmNumber):
        # check if filmNumber is a filmNumber in film Table
        qryStr = "SELECT COUNT(*) FROM film WHERE filmnummer = '{0}'".format(filmNumber)
        query = QSqlQuery(self.dbm.db)
        query.exec_(qryStr)
        query.first()
        return query.value(0)

    def showEvent(self, event):
        if self.currentPath:
            self.uiImagePathLbl.setText(self.currentPath)
            self.loadImage(self.currentPath)
        else:
            self.uiImagePathLbl.setText("--")
            self.loadText()

        self.graphicLoaded = True

    def loadText(self):
        self.scene.clear()
        noImageTxt = QGraphicsTextItem()
        noImageTxt.setPlainText(u"Wählen Sie ein repräsentatives Luftbild aus ...")
        self.rect = noImageTxt.boundingRect()
        self.scene.addItem(noImageTxt)
        self.scene.setSceneRect(self.rect)
        self.uiRepresentativeImageView.fitInView(self.rect, Qt.KeepAspectRatio)

    def loadImage(self, path):
        self.scene.clear()
        image = QImage(path)
        size = image.size()
        self.rect = QRectF(0, 0, size.width(), size.height())
        self.scene.addPixmap(QPixmap.fromImage(image))
        self.scene.setSceneRect(self.rect)
        self.uiRepresentativeImageView.fitInView(self.rect, Qt.KeepAspectRatio)

    def loadNewImageByFilm(self):
        # generatePath
        imgDir = self.settings.value("APIS/image_dir")
        #TODO RM filmDir = IdToIdLegacy(self.filmNumber)
        filmDir = self.filmNumber
        self.newPath = os.path.normpath(imgDir +  "\\" + filmDir + "\\" + self.uiAvailableImagesCombo.currentText().replace('.','_') + ".jpg")
        self.uiImagePathLbl.setText(self.newPath)
        self.loadImage(self.newPath)

    def resizeEvent(self, event):
        if self.graphicLoaded:
            self.uiRepresentativeImageView.fitInView(self.rect, Qt.KeepAspectRatio)

    def selectImageFromSystem(self):
        dir = self.settings.value("APIS/image_dir")
        fileName = QFileDialog.getOpenFileName(self, u"Repräsentatives Luftbild auswählen", dir, "Bild Dateien (*.jpg)")
        if fileName:
            self.uiFilmNumberCombo.setCurrentIndex(-1)
            self.newPath = fileName
            self.uiImagePathLbl.setText(self.newPath)
            self.loadImage(self.newPath)

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