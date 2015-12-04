# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_film_selection_list_form.ui'
#
# Created: Fri Nov 27 11:29:22 2015
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
        apisFilmSelectionListDialog.resize(720, 536)
        self.gridLayout = QtGui.QGridLayout(apisFilmSelectionListDialog)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.uiDisplayFlightPathBtn = QtGui.QPushButton(apisFilmSelectionListDialog)
        self.uiDisplayFlightPathBtn.setEnabled(True)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/flightpath.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiDisplayFlightPathBtn.setIcon(icon)
        self.uiDisplayFlightPathBtn.setIconSize(QtCore.QSize(30, 30))
        self.uiDisplayFlightPathBtn.setObjectName(_fromUtf8("uiDisplayFlightPathBtn"))
        self.horizontalLayout.addWidget(self.uiDisplayFlightPathBtn)
        self.uiExportDetailsAsPdfBtn = QtGui.QPushButton(apisFilmSelectionListDialog)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/print.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiExportDetailsAsPdfBtn.setIcon(icon1)
        self.uiExportDetailsAsPdfBtn.setIconSize(QtCore.QSize(30, 30))
        self.uiExportDetailsAsPdfBtn.setObjectName(_fromUtf8("uiExportDetailsAsPdfBtn"))
        self.horizontalLayout.addWidget(self.uiExportDetailsAsPdfBtn)
        self.uiExportListAsPdfBtn = QtGui.QPushButton(apisFilmSelectionListDialog)
        self.uiExportListAsPdfBtn.setIcon(icon1)
        self.uiExportListAsPdfBtn.setIconSize(QtCore.QSize(30, 30))
        self.uiExportListAsPdfBtn.setObjectName(_fromUtf8("uiExportListAsPdfBtn"))
        self.horizontalLayout.addWidget(self.uiExportListAsPdfBtn)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(apisFilmSelectionListDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.uiFilmListTableV = QtGui.QTableView(apisFilmSelectionListDialog)
        self.uiFilmListTableV.setObjectName(_fromUtf8("uiFilmListTableV"))
        self.gridLayout.addWidget(self.uiFilmListTableV, 1, 0, 1, 1)

        self.retranslateUi(apisFilmSelectionListDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), apisFilmSelectionListDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), apisFilmSelectionListDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(apisFilmSelectionListDialog)

    def retranslateUi(self, apisFilmSelectionListDialog):
        apisFilmSelectionListDialog.setWindowTitle(_translate("apisFilmSelectionListDialog", "Film Auswahl", None))
        self.uiDisplayFlightPathBtn.setText(_translate("apisFilmSelectionListDialog", "Flugwege anzeigen", None))
        self.uiExportDetailsAsPdfBtn.setText(_translate("apisFilmSelectionListDialog", "Details als PDF exportieren", None))
        self.uiExportListAsPdfBtn.setText(_translate("apisFilmSelectionListDialog", "Liste als PDF exportieren", None))

import resource_rc
