# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_weather_form.ui'
#
# Created: Fri Dec 18 09:53:40 2015
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
        self.gridLayout_2 = QtGui.QGridLayout(apisWeatherDialog)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiWeatherValueLbl = QtGui.QLabel(apisWeatherDialog)
        self.uiWeatherValueLbl.setObjectName(_fromUtf8("uiWeatherValueLbl"))
        self.gridLayout.addWidget(self.uiWeatherValueLbl, 3, 2, 1, 1)
        self.uiLowCloudHeightLbl = QtGui.QLabel(apisWeatherDialog)
        self.uiLowCloudHeightLbl.setObjectName(_fromUtf8("uiLowCloudHeightLbl"))
        self.gridLayout.addWidget(self.uiLowCloudHeightLbl, 2, 0, 1, 1)
        self.uiWeatherLbl = QtGui.QLabel(apisWeatherDialog)
        self.uiWeatherLbl.setObjectName(_fromUtf8("uiWeatherLbl"))
        self.gridLayout.addWidget(self.uiWeatherLbl, 3, 0, 1, 1)
        self.line = QtGui.QFrame(apisWeatherDialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout.addWidget(self.line, 5, 0, 1, 2)
        self.uiDescriptionLbl = QtGui.QLabel(apisWeatherDialog)
        self.uiDescriptionLbl.setObjectName(_fromUtf8("uiDescriptionLbl"))
        self.gridLayout.addWidget(self.uiDescriptionLbl, 6, 0, 1, 1)
        self.uiCodeEdit = QtGui.QLineEdit(apisWeatherDialog)
        self.uiCodeEdit.setStyleSheet(_fromUtf8("background-color: rgb(218, 218, 218);"))
        self.uiCodeEdit.setReadOnly(True)
        self.uiCodeEdit.setObjectName(_fromUtf8("uiCodeEdit"))
        self.gridLayout.addWidget(self.uiCodeEdit, 6, 1, 1, 1)
        self.uiLowCloudHeightCombo = QtGui.QComboBox(apisWeatherDialog)
        self.uiLowCloudHeightCombo.setObjectName(_fromUtf8("uiLowCloudHeightCombo"))
        self.gridLayout.addWidget(self.uiLowCloudHeightCombo, 2, 1, 1, 1)
        self.uiRemarksMissionLbl = QtGui.QLabel(apisWeatherDialog)
        self.uiRemarksMissionLbl.setObjectName(_fromUtf8("uiRemarksMissionLbl"))
        self.gridLayout.addWidget(self.uiRemarksMissionLbl, 4, 0, 1, 1)
        self.uiVisibilityCombo = QtGui.QComboBox(apisWeatherDialog)
        self.uiVisibilityCombo.setObjectName(_fromUtf8("uiVisibilityCombo"))
        self.gridLayout.addWidget(self.uiVisibilityCombo, 1, 1, 1, 1)
        self.uiRemarksMissionCombo = QtGui.QComboBox(apisWeatherDialog)
        self.uiRemarksMissionCombo.setObjectName(_fromUtf8("uiRemarksMissionCombo"))
        self.gridLayout.addWidget(self.uiRemarksMissionCombo, 4, 1, 1, 1)
        self.uiVisibilityLbl = QtGui.QLabel(apisWeatherDialog)
        self.uiVisibilityLbl.setObjectName(_fromUtf8("uiVisibilityLbl"))
        self.gridLayout.addWidget(self.uiVisibilityLbl, 1, 0, 1, 1)
        self.uiLowCloudAmountCombo = QtGui.QComboBox(apisWeatherDialog)
        self.uiLowCloudAmountCombo.setObjectName(_fromUtf8("uiLowCloudAmountCombo"))
        self.gridLayout.addWidget(self.uiLowCloudAmountCombo, 0, 1, 1, 1)
        self.uiLowCloudAmountLbl = QtGui.QLabel(apisWeatherDialog)
        self.uiLowCloudAmountLbl.setObjectName(_fromUtf8("uiLowCloudAmountLbl"))
        self.gridLayout.addWidget(self.uiLowCloudAmountLbl, 0, 0, 1, 1)
        self.uiDescriptionPTxt = QtGui.QPlainTextEdit(apisWeatherDialog)
        self.uiDescriptionPTxt.setStyleSheet(_fromUtf8("background-color: rgb(218, 218, 218);"))
        self.uiDescriptionPTxt.setReadOnly(True)
        self.uiDescriptionPTxt.setObjectName(_fromUtf8("uiDescriptionPTxt"))
        self.gridLayout.addWidget(self.uiDescriptionPTxt, 7, 0, 2, 2)
        self.uiButtonBox = QtGui.QDialogButtonBox(apisWeatherDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName(_fromUtf8("uiButtonBox"))
        self.gridLayout.addWidget(self.uiButtonBox, 8, 4, 1, 2)
        self.uiWeatherCombo = QtGui.QComboBox(apisWeatherDialog)
        self.uiWeatherCombo.setObjectName(_fromUtf8("uiWeatherCombo"))
        self.gridLayout.addWidget(self.uiWeatherCombo, 3, 1, 1, 1)
        self.uiRemarksTableV = QtGui.QTableView(apisWeatherDialog)
        self.uiRemarksTableV.setStyleSheet(_fromUtf8("selection-background-color: rgb(152, 202, 255);\n"
"selection-color: rgb(0, 0, 0);"))
        self.uiRemarksTableV.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.uiRemarksTableV.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.uiRemarksTableV.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.uiRemarksTableV.setObjectName(_fromUtf8("uiRemarksTableV"))
        self.gridLayout.addWidget(self.uiRemarksTableV, 1, 4, 7, 2)
        self.uiLowCloudHeightValueLbl = QtGui.QLabel(apisWeatherDialog)
        self.uiLowCloudHeightValueLbl.setObjectName(_fromUtf8("uiLowCloudHeightValueLbl"))
        self.gridLayout.addWidget(self.uiLowCloudHeightValueLbl, 2, 2, 1, 1)
        self.uiRemarksMissionValueLbl = QtGui.QLabel(apisWeatherDialog)
        self.uiRemarksMissionValueLbl.setObjectName(_fromUtf8("uiRemarksMissionValueLbl"))
        self.gridLayout.addWidget(self.uiRemarksMissionValueLbl, 4, 2, 1, 1)
        self.uiLowCloudAmountValueLbl = QtGui.QLabel(apisWeatherDialog)
        self.uiLowCloudAmountValueLbl.setObjectName(_fromUtf8("uiLowCloudAmountValueLbl"))
        self.gridLayout.addWidget(self.uiLowCloudAmountValueLbl, 0, 2, 1, 1)
        self.uiRemarksLbl = QtGui.QLabel(apisWeatherDialog)
        self.uiRemarksLbl.setObjectName(_fromUtf8("uiRemarksLbl"))
        self.gridLayout.addWidget(self.uiRemarksLbl, 0, 4, 1, 1)
        self.uiVisibilityValueLbl = QtGui.QLabel(apisWeatherDialog)
        self.uiVisibilityValueLbl.setObjectName(_fromUtf8("uiVisibilityValueLbl"))
        self.gridLayout.addWidget(self.uiVisibilityValueLbl, 1, 2, 1, 1)
        self.uiRemarksValueLbl = QtGui.QLabel(apisWeatherDialog)
        self.uiRemarksValueLbl.setObjectName(_fromUtf8("uiRemarksValueLbl"))
        self.gridLayout.addWidget(self.uiRemarksValueLbl, 0, 5, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 9, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(apisWeatherDialog)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), apisWeatherDialog.accept)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), apisWeatherDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(apisWeatherDialog)

    def retranslateUi(self, apisWeatherDialog):
        apisWeatherDialog.setWindowTitle(_translate("apisWeatherDialog", "APIS Wetter Auswahl", None))
        self.uiWeatherValueLbl.setText(_translate("apisWeatherDialog", "-", None))
        self.uiLowCloudHeightLbl.setText(_translate("apisWeatherDialog", "Low Cloud Height:", None))
        self.uiWeatherLbl.setText(_translate("apisWeatherDialog", "Weather:", None))
        self.uiDescriptionLbl.setText(_translate("apisWeatherDialog", "Beschreibung:", None))
        self.uiRemarksMissionLbl.setText(_translate("apisWeatherDialog", "Remarks Mission:", None))
        self.uiVisibilityLbl.setText(_translate("apisWeatherDialog", "Visibility (km):", None))
        self.uiLowCloudAmountLbl.setText(_translate("apisWeatherDialog", "Low Cloud Amount:", None))
        self.uiLowCloudHeightValueLbl.setText(_translate("apisWeatherDialog", "-", None))
        self.uiRemarksMissionValueLbl.setText(_translate("apisWeatherDialog", "-", None))
        self.uiLowCloudAmountValueLbl.setText(_translate("apisWeatherDialog", "-", None))
        self.uiRemarksLbl.setText(_translate("apisWeatherDialog", "Remarks:", None))
        self.uiVisibilityValueLbl.setText(_translate("apisWeatherDialog", "-", None))
        self.uiRemarksValueLbl.setText(_translate("apisWeatherDialog", "-", None))

import resource_rc
