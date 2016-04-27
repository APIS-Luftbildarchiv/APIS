# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_film_selection_list_form.ui'
#
# Created: Wed Apr 27 09:52:15 2016
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_apisFilmSelectionListDialog(object):
    def setupUi(self, apisFilmSelectionListDialog):
        apisFilmSelectionListDialog.setObjectName(_fromUtf8("apisFilmSelectionListDialog"))
        apisFilmSelectionListDialog.resize(725, 571)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/apis.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        apisFilmSelectionListDialog.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(apisFilmSelectionListDialog)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.uiDisplayFlightPathBtn = QtGui.QPushButton(apisFilmSelectionListDialog)
        self.uiDisplayFlightPathBtn.setEnabled(True)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/flightpath.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiDisplayFlightPathBtn.setIcon(icon1)
        self.uiDisplayFlightPathBtn.setIconSize(QtCore.QSize(24, 24))
        self.uiDisplayFlightPathBtn.setObjectName(_fromUtf8("uiDisplayFlightPathBtn"))
        self.horizontalLayout.addWidget(self.uiDisplayFlightPathBtn)
        self.uiExportDetailsAsPdfBtn = QtGui.QPushButton(apisFilmSelectionListDialog)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/pdf_export.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiExportDetailsAsPdfBtn.setIcon(icon2)
        self.uiExportDetailsAsPdfBtn.setIconSize(QtCore.QSize(24, 24))
        self.uiExportDetailsAsPdfBtn.setObjectName(_fromUtf8("uiExportDetailsAsPdfBtn"))
        self.horizontalLayout.addWidget(self.uiExportDetailsAsPdfBtn)
        self.uiExportListAsPdfBtn = QtGui.QPushButton(apisFilmSelectionListDialog)
        self.uiExportListAsPdfBtn.setIcon(icon2)
        self.uiExportListAsPdfBtn.setIconSize(QtCore.QSize(24, 24))
        self.uiExportListAsPdfBtn.setObjectName(_fromUtf8("uiExportListAsPdfBtn"))
        self.horizontalLayout.addWidget(self.uiExportListAsPdfBtn)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.uiFilmListTableV = QtGui.QTableView(apisFilmSelectionListDialog)
        self.uiFilmListTableV.setObjectName(_fromUtf8("uiFilmListTableV"))
        self.gridLayout.addWidget(self.uiFilmListTableV, 1, 0, 1, 1)

        self.retranslateUi(apisFilmSelectionListDialog)
        QtCore.QMetaObject.connectSlotsByName(apisFilmSelectionListDialog)

    def retranslateUi(self, apisFilmSelectionListDialog):
        apisFilmSelectionListDialog.setWindowTitle(_translate("apisFilmSelectionListDialog", "APIS Film Auswahl", None))
        self.uiDisplayFlightPathBtn.setText(_translate("apisFilmSelectionListDialog", "Flugwege anzeigen", None))
        self.uiExportDetailsAsPdfBtn.setText(_translate("apisFilmSelectionListDialog", "Details als PDF exportieren", None))
        self.uiExportListAsPdfBtn.setText(_translate("apisFilmSelectionListDialog", "Liste als PDF exportieren", None))

import resource_rc
