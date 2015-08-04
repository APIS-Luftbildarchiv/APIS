# -*- coding: utf-8 -*

import os, re

from PyQt4.QtCore import QDate, Qt
from PyQt4.QtGui import *
# from PyQt4.QtSql import *

# from apis_db_manager import *

# from functools import partial

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

# --------------------------------------------------------
# Film - Suche
# --------------------------------------------------------
from apis_search_film_form import *

class ApisSearchFilmDialog(QDialog, Ui_apisSearchFilmDialog):

    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        #self.dbm = dbm
        self.setupUi(self)

        self.accepted.connect(self.onAccepted)

        now = QDate.currentDate()
        self.uiSearchDate.setDate(now)
        self.uiSearchDate.setMaximumDate(now)
        self.uiToDate.setDate(now)
        self.uiToDate.setMaximumDate(now)
        # FIXME next two lines into def => update on change of one of the two Date edits
        # FIXME next two lines into def => update on change of one of the two Date edits
        self.uiFromDate.setMaximumDate(self.uiToDate.date())
        self.uiToDate.setMinimumDate(self.uiFromDate.date())

        # Signals
        self.uiVerticalChk.stateChanged.connect(self.onFilmModeChange)
        self.uiObliqueChk.stateChanged.connect(self.onFilmModeChange)

        #self.uiSearchDate.dateChanged.connect()

        #self.uiMilitaryNumberEdit.textChanged()

        self.uiFromDate.dateChanged.connect(self.timeSpanChanged)
        self.uiToDate.dateChanged.connect(self.timeSpanChanged)
        self.uiFromChk.stateChanged.connect(self.timeSpanConstraints)
        self.uiToChk.stateChanged.connect(self.timeSpanConstraints)

    def timeSpanConstraints(self):
        # From Date isChecked => FromDate = 01.01.1900, disable FromDate; else enable FromDate
        if self.uiFromChk.isChecked():
            self.uiFromDate.setEnabled(True)
        else:
            self.uiFromDate.setDate(self.uiFromDate.minimumDate())
            self.uiFromDate.setDisabled(True)

        # ToDate isChecked => ToDate = Today, disable ToDate; else enable ToDate
        if self.uiToChk.isChecked():
            self.uiToDate.setEnabled(True)
        else:
            self.uiToDate.setDate(self.uiToDate.maximumDate())
            self.uiToDate.setDisabled(True)

    def timeSpanChanged(self):
        self.uiFromDate.setMaximumDate(self.uiToDate.date())
        self.uiToDate.setMinimumDate(self.uiFromDate.date())

    def generateSearchQuery(self):
        # Search Mode ? byFilmModeOnly, byDate,b yMilitaryNumber, byTimeSpan
        if self.uiVerticalChk.checkState() == Qt.Checked or self.uiObliqueChk.checkState() == Qt.Checked:
            filmModePart = ()
            if self.uiVerticalChk.checkState() == Qt.Checked:
                vertical = u"'senk.'"
            else:
                vertical = u""
            if self.uiObliqueChk.checkState() == Qt.Checked:
                oblique = u"'schräg'"
            else:
                oblique = u""

            if vertical != "" and oblique != "":
                separator = u","
            else:
                separator = u""

            #searchQuery = u"select * from film where weise in ({0}{1}{2})".format(vertical, separator, oblique)
            searchQuery = u"weise in ({0}{1}{2})".format(vertical, separator, oblique)

        else:
            # get search mode
            if self.uiSearchModeTBox.currentIndex() == 0:
                # byDate
                date = self.uiSearchDate.date()
                if self.uiDateRBtn.isChecked():
                    pattern = "%Y-%m-%d"
                    searchString = date.toString("yyyy-MM-dd")
                elif self.uiYearOnlyRBtn.isChecked():
                    pattern = "%Y"
                    searchString = date.toString("yyyy")
                elif self.uiYearMonthRBtn.isChecked():
                    pattern = "%Y-%m"
                    searchString = date.toString("yyyy-MM")
                elif self.uiMonthOnlyRBtn.isChecked():
                    pattern = "%m"
                    searchString = date.toString("MM")
                searchModePart = u"(strftime('{0}', flugdatum) = '{1}')".format(pattern, searchString)
            elif self.uiSearchModeTBox.currentIndex() == 1:
                # byMilitaryNumber
                milNum = self.uiMilitaryNumberEdit.text()
                milNum = ''.join(i for i in milNum if i not in '/() ')
                searchString = '%' + '%'.join(milNum[i:i+1] for i in range(0, len(milNum), 1)) + '%'
                searchModePart = u"(militaernummer like '{0}' or militaernummer_alt like '{0}')".format(searchString)
            elif self.uiSearchModeTBox.currentIndex() == 2:
                # byTimeSpan
                fromDate = self.uiFromDate.date()
                toDate = self.uiToDate.date()
                fromDate = fromDate.toString("yyyy-MM-dd")
                toDate = toDate.toString("yyyy-MM-dd")
                searchModePart = u"(strftime('%Y-%m-%d', flugdatum) between '{0}' and '{1}')".format(fromDate, toDate)

            #get film mode
            if self.uiVerticalChk.checkState() == Qt.PartiallyChecked and self.uiObliqueChk.checkState() == Qt.PartiallyChecked:
                filmModePart = u" and (weise in ('senk.', 'schräg'))"
            elif self.uiVerticalChk.checkState() == Qt.PartiallyChecked:
                filmModePart = u" and (weise = 'senk.')"
            elif self.uiObliqueChk.checkState() == Qt.PartiallyChecked:
                filmModePart = u" and (weise = 'schräg')"
            else:
                filmModePart = u""

            # searchQuery = u"select * from film where {0}{1}".format(searchModePart, filmModePart)
            searchQuery = u"{0}{1}".format(searchModePart, filmModePart)

        return searchQuery

    def onFilmModeChange(self):
        verticalState = self.uiVerticalChk.checkState()
        obliqueState = self.uiObliqueChk.checkState()

        if verticalState == Qt.Checked or obliqueState == Qt.Checked:
            self.uiSearchModeTBox.setEnabled(False)
            self.uiVerticalChk.setTristate(False)
            self.uiObliqueChk.setTristate(False)
            if verticalState == Qt.PartiallyChecked:
                self.uiVerticalChk.setCheckState(Qt.Checked)
            if obliqueState == Qt.PartiallyChecked:
                self.uiObliqueChk.setCheckState(Qt.Checked)
        else:
            self.uiSearchModeTBox.setEnabled(True)
            self.uiVerticalChk.setTristate(True)
            self.uiObliqueChk.setTristate(True)

    def onAccepted(self):
        self.accept()