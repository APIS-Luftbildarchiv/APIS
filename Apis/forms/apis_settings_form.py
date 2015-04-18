# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_settings_form.ui'
#
# Created: Sat Apr 18 11:39:04 2015
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

class Ui_apisSettingsDialog(object):
    def setupUi(self, apisSettingsDialog):
        apisSettingsDialog.setObjectName(_fromUtf8("apisSettingsDialog"))
        apisSettingsDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        apisSettingsDialog.resize(300, 500)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(apisSettingsDialog.sizePolicy().hasHeightForWidth())
        apisSettingsDialog.setSizePolicy(sizePolicy)
        apisSettingsDialog.setLocale(QtCore.QLocale(QtCore.QLocale.German, QtCore.QLocale.Austria))
        apisSettingsDialog.setSizeGripEnabled(False)
        apisSettingsDialog.setModal(True)
        self.groupBox = QtGui.QGroupBox(apisSettingsDialog)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 281, 71))
        self.groupBox.setStyleSheet(_fromUtf8(""))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayoutWidget = QtGui.QWidget(self.groupBox)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 20, 261, 41))
        self.horizontalLayoutWidget.setObjectName(_fromUtf8("horizontalLayoutWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.comboBox_2 = QtGui.QComboBox(self.horizontalLayoutWidget)
        self.comboBox_2.setObjectName(_fromUtf8("comboBox_2"))
        self.horizontalLayout.addWidget(self.comboBox_2)
        self.toolButton = QtGui.QToolButton(self.horizontalLayoutWidget)
        self.toolButton.setObjectName(_fromUtf8("toolButton"))
        self.horizontalLayout.addWidget(self.toolButton)
        self.groupBox_2 = QtGui.QGroupBox(apisSettingsDialog)
        self.groupBox_2.setEnabled(False)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 90, 281, 371))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayoutWidget = QtGui.QWidget(self.groupBox_2)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 20, 261, 41))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout_2 = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.toolButton_2 = QtGui.QToolButton(self.gridLayoutWidget)
        self.toolButton_2.setObjectName(_fromUtf8("toolButton_2"))
        self.gridLayout_2.addWidget(self.toolButton_2, 1, 1, 1, 1)
        self.label = QtGui.QLabel(self.gridLayoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.lineEdit = QtGui.QLineEdit(self.gridLayoutWidget)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.gridLayout_2.addWidget(self.lineEdit, 1, 0, 1, 1)
        self.gridLayoutWidget_2 = QtGui.QWidget(self.groupBox_2)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(10, 70, 261, 41))
        self.gridLayoutWidget_2.setObjectName(_fromUtf8("gridLayoutWidget_2"))
        self.gridLayout_3 = QtGui.QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_3.setMargin(0)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.toolButton_3 = QtGui.QToolButton(self.gridLayoutWidget_2)
        self.toolButton_3.setObjectName(_fromUtf8("toolButton_3"))
        self.gridLayout_3.addWidget(self.toolButton_3, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.gridLayoutWidget_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_3.addWidget(self.label_2, 0, 0, 1, 1)
        self.lineEdit_2 = QtGui.QLineEdit(self.gridLayoutWidget_2)
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))
        self.gridLayout_3.addWidget(self.lineEdit_2, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(apisSettingsDialog)
        self.buttonBox.setGeometry(QtCore.QRect(140, 470, 156, 23))
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))

        self.retranslateUi(apisSettingsDialog)
        QtCore.QMetaObject.connectSlotsByName(apisSettingsDialog)

    def retranslateUi(self, apisSettingsDialog):
        apisSettingsDialog.setWindowTitle(_translate("apisSettingsDialog", "APIS Einstellungen", None))
        self.groupBox.setTitle(_translate("apisSettingsDialog", "APIS Spatialite Datenbank", None))
        self.toolButton.setText(_translate("apisSettingsDialog", "...", None))
        self.groupBox_2.setTitle(_translate("apisSettingsDialog", "Pfade", None))
        self.toolButton_2.setText(_translate("apisSettingsDialog", "...", None))
        self.label.setText(_translate("apisSettingsDialog", "TextLabel", None))
        self.toolButton_3.setText(_translate("apisSettingsDialog", "...", None))
        self.label_2.setText(_translate("apisSettingsDialog", "TextLabel", None))

import resource_rc
