# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_weather_form.ui'
#
# Created: Mon Jun 15 22:13:43 2015
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

class Ui_apisWeatherDialog(object):
    def setupUi(self, apisWeatherDialog):
        apisWeatherDialog.setObjectName(_fromUtf8("apisWeatherDialog"))
        apisWeatherDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        apisWeatherDialog.resize(610, 310)
        apisWeatherDialog.setMinimumSize(QtCore.QSize(610, 290))
        apisWeatherDialog.setMaximumSize(QtCore.QSize(800, 500))
        apisWeatherDialog.setModal(True)
        self.gridLayoutWidget = QtGui.QWidget(apisWeatherDialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 591, 293))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiLowCloudHeightLbl = QtGui.QLabel(self.gridLayoutWidget)
        self.uiLowCloudHeightLbl.setObjectName(_fromUtf8("uiLowCloudHeightLbl"))
        self.gridLayout.addWidget(self.uiLowCloudHeightLbl, 2, 0, 1, 1)
        self.uiWeatherLbl = QtGui.QLabel(self.gridLayoutWidget)
        self.uiWeatherLbl.setObjectName(_fromUtf8("uiWeatherLbl"))
        self.gridLayout.addWidget(self.uiWeatherLbl, 3, 0, 1, 1)
        self.line = QtGui.QFrame(self.gridLayoutWidget)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout.addWidget(self.line, 5, 0, 1, 2)
        self.uiDescriptionLbl = QtGui.QLabel(self.gridLayoutWidget)
        self.uiDescriptionLbl.setObjectName(_fromUtf8("uiDescriptionLbl"))
        self.gridLayout.addWidget(self.uiDescriptionLbl, 6, 0, 1, 1)
        self.uiCodeEdit = QtGui.QLineEdit(self.gridLayoutWidget)
        self.uiCodeEdit.setStyleSheet(_fromUtf8("background-color: rgb(218, 218, 218);"))
        self.uiCodeEdit.setReadOnly(True)
        self.uiCodeEdit.setObjectName(_fromUtf8("uiCodeEdit"))
        self.gridLayout.addWidget(self.uiCodeEdit, 6, 1, 1, 1)
        self.uiLowCloudHeightCombo = QtGui.QComboBox(self.gridLayoutWidget)
        self.uiLowCloudHeightCombo.setObjectName(_fromUtf8("uiLowCloudHeightCombo"))
        self.gridLayout.addWidget(self.uiLowCloudHeightCombo, 2, 1, 1, 1)
        self.uiRemarksMissionLbl = QtGui.QLabel(self.gridLayoutWidget)
        self.uiRemarksMissionLbl.setObjectName(_fromUtf8("uiRemarksMissionLbl"))
        self.gridLayout.addWidget(self.uiRemarksMissionLbl, 4, 0, 1, 1)
        self.uiVisibilityCombo = QtGui.QComboBox(self.gridLayoutWidget)
        self.uiVisibilityCombo.setObjectName(_fromUtf8("uiVisibilityCombo"))
        self.gridLayout.addWidget(self.uiVisibilityCombo, 1, 1, 1, 1)
        self.uiRemarksMissionCombo = QtGui.QComboBox(self.gridLayoutWidget)
        self.uiRemarksMissionCombo.setObjectName(_fromUtf8("uiRemarksMissionCombo"))
        self.gridLayout.addWidget(self.uiRemarksMissionCombo, 4, 1, 1, 1)
        self.uiVisibilityLbl = QtGui.QLabel(self.gridLayoutWidget)
        self.uiVisibilityLbl.setObjectName(_fromUtf8("uiVisibilityLbl"))
        self.gridLayout.addWidget(self.uiVisibilityLbl, 1, 0, 1, 1)
        self.uiLowCloudAmountCombo = QtGui.QComboBox(self.gridLayoutWidget)
        self.uiLowCloudAmountCombo.setObjectName(_fromUtf8("uiLowCloudAmountCombo"))
        self.gridLayout.addWidget(self.uiLowCloudAmountCombo, 0, 1, 1, 1)
        self.uiLowCloudAmountLbl = QtGui.QLabel(self.gridLayoutWidget)
        self.uiLowCloudAmountLbl.setObjectName(_fromUtf8("uiLowCloudAmountLbl"))
        self.gridLayout.addWidget(self.uiLowCloudAmountLbl, 0, 0, 1, 1)
        self.uiDescriptionPTxt = QtGui.QPlainTextEdit(self.gridLayoutWidget)
        self.uiDescriptionPTxt.setStyleSheet(_fromUtf8("background-color: rgb(218, 218, 218);"))
        self.uiDescriptionPTxt.setReadOnly(True)
        self.uiDescriptionPTxt.setObjectName(_fromUtf8("uiDescriptionPTxt"))
        self.gridLayout.addWidget(self.uiDescriptionPTxt, 7, 0, 2, 2)
        self.uiButtonBox = QtGui.QDialogButtonBox(self.gridLayoutWidget)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName(_fromUtf8("uiButtonBox"))
        self.gridLayout.addWidget(self.uiButtonBox, 8, 3, 1, 2)
        self.uiWeatherCombo = QtGui.QComboBox(self.gridLayoutWidget)
        self.uiWeatherCombo.setObjectName(_fromUtf8("uiWeatherCombo"))
        self.gridLayout.addWidget(self.uiWeatherCombo, 3, 1, 1, 1)
        self.line_2 = QtGui.QFrame(self.gridLayoutWidget)
        self.line_2.setFrameShape(QtGui.QFrame.VLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.gridLayout.addWidget(self.line_2, 0, 2, 9, 1)
        self.uiRemarksTableV = QtGui.QTableView(self.gridLayoutWidget)
        self.uiRemarksTableV.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.uiRemarksTableV.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.uiRemarksTableV.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.uiRemarksTableV.setObjectName(_fromUtf8("uiRemarksTableV"))
        self.gridLayout.addWidget(self.uiRemarksTableV, 1, 3, 7, 2)
        self.uiRemarksLbl = QtGui.QLabel(self.gridLayoutWidget)
        self.uiRemarksLbl.setObjectName(_fromUtf8("uiRemarksLbl"))
        self.gridLayout.addWidget(self.uiRemarksLbl, 0, 3, 1, 2)

        self.retranslateUi(apisWeatherDialog)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), apisWeatherDialog.accept)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), apisWeatherDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(apisWeatherDialog)

    def retranslateUi(self, apisWeatherDialog):
        apisWeatherDialog.setWindowTitle(_translate("apisWeatherDialog", "Wetter Auswahl", None))
        self.uiLowCloudHeightLbl.setText(_translate("apisWeatherDialog", "Low Cloud Height:", None))
        self.uiWeatherLbl.setText(_translate("apisWeatherDialog", "Weather:", None))
        self.uiDescriptionLbl.setText(_translate("apisWeatherDialog", "Beschreibung:", None))
        self.uiRemarksMissionLbl.setText(_translate("apisWeatherDialog", "Remarks Mission:", None))
        self.uiVisibilityLbl.setText(_translate("apisWeatherDialog", "Visibility (km):", None))
        self.uiLowCloudAmountLbl.setText(_translate("apisWeatherDialog", "Low Cloud Amount:", None))
        self.uiRemarksLbl.setText(_translate("apisWeatherDialog", "Remarks:", None))

import resource_rc
