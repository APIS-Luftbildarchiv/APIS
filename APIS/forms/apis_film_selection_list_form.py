# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_film_selection_list_form.ui'
#
# Created: Mon Sep 07 18:36:41 2015
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
        apisFilmSelectionListDialog.resize(750, 550)
        self.uiFilmListTableV = QtGui.QTableView(apisFilmSelectionListDialog)
        self.uiFilmListTableV.setGeometry(QtCore.QRect(10, 60, 731, 481))
        self.uiFilmListTableV.setObjectName(_fromUtf8("uiFilmListTableV"))
        self.horizontalLayoutWidget = QtGui.QWidget(apisFilmSelectionListDialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 731, 40))
        self.horizontalLayoutWidget.setObjectName(_fromUtf8("horizontalLayoutWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.uiDisplayFlightPathBtn = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.uiDisplayFlightPathBtn.setEnabled(True)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/flightpath.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiDisplayFlightPathBtn.setIcon(icon)
        self.uiDisplayFlightPathBtn.setIconSize(QtCore.QSize(30, 30))
        self.uiDisplayFlightPathBtn.setObjectName(_fromUtf8("uiDisplayFlightPathBtn"))
        self.horizontalLayout.addWidget(self.uiDisplayFlightPathBtn)
        self.uiExportDetailsAsPdfBtn = QtGui.QPushButton(self.horizontalLayoutWidget)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/print.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiExportDetailsAsPdfBtn.setIcon(icon1)
        self.uiExportDetailsAsPdfBtn.setIconSize(QtCore.QSize(30, 30))
        self.uiExportDetailsAsPdfBtn.setObjectName(_fromUtf8("uiExportDetailsAsPdfBtn"))
        self.horizontalLayout.addWidget(self.uiExportDetailsAsPdfBtn)
        self.uiExportListAsPdfBtn = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.uiExportListAsPdfBtn.setIcon(icon1)
        self.uiExportListAsPdfBtn.setIconSize(QtCore.QSize(30, 30))
        self.uiExportListAsPdfBtn.setObjectName(_fromUtf8("uiExportListAsPdfBtn"))
        self.horizontalLayout.addWidget(self.uiExportListAsPdfBtn)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(self.horizontalLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)

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
