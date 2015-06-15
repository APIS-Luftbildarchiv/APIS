# -*- coding: utf-8 -*

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

from apis_db_manager import *

from functools import partial

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

# --------------------------------------------------------
# Film - Eingabe, Pflege
# --------------------------------------------------------
from apis_film_selection_list_form import *

class ApisFilmSelectionListDialog(QDialog, Ui_apisFilmSelectionListDialog):

    def __init__(self, iface, model):
        QDialog.__init__(self)
        self.iface = iface
        self.model = model
        self.setupUi(self)

        self.accepted.connect(self.onAccepted)

        self.setupTable()

    def setupTable(self):
        self.uiFilmListTableV.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.uiFilmListTableV.setModel(self.model)
        self.uiFilmListTableV.setEditTriggers(QAbstractItemView.NoEditTriggers)

        #hide and sort Columns
        visibleColumns = ['filmnummer', 'flugdatum', 'anzahl_bilder', 'weise', 'art_ausarbeitung', 'militaernummer', 'militaernummer_alt']
        vCIdx = []
        for vC in visibleColumns:
            vCIdx.append(self.model.fieldIndex(vC))

        for c in range(self.model.columnCount()):
            if c not in vCIdx:
                self.uiFilmListTableV.hideColumn(c)

        hH = self.uiFilmListTableV.horizontalHeader()
        for i in range(len(vCIdx)):
            hH.moveSection(hH.visualIndex(vCIdx[i]), i)

        self.uiFilmListTableV.resizeColumnsToContents()
        self.uiFilmListTableV.resizeRowsToContents()

        # signals
        self.uiFilmListTableV.doubleClicked.connect(self.viewFilm)
        #self.uiFilmListTableV.selectionModel().selectionChanged.connect(self.onSelectionChanged)

    def viewFilm(self):
        # QMessageBox.warning(None, "FilmNumber", "Double")
        filmIdx = self.model.createIndex(self.uiFilmListTableV.currentIndex().row(), self.model.fieldIndex("filmnummer"))
        self.filmNumberToLoad = self.model.data(filmIdx)
        self.accept()
        #QMessageBox.warning(None, "FilmNumber", unicode(self.model.data(filmIdx)))

    def onSelectionChanged(self, current, previous):
        if self.uiFilmListTableV.selectionModel().hasSelection():
            self.uiDisplayFlightPathBtn.setEnabled(True)
        else:
            self.uiDisplayFlightPathBtn.setEnabled(False)
        #QMessageBox.warning(None, "FilmNumber", "selection Changed")

    def onAccepted(self):
        self.accept()