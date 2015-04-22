# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_settings_form.ui'
#
# Created: Tue Apr 21 12:21:26 2015
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
        apisSettingsDialog.setMinimumSize(QtCore.QSize(300, 500))
        apisSettingsDialog.setMaximumSize(QtCore.QSize(300, 500))
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
        self.inDbPath = QtGui.QLineEdit(self.horizontalLayoutWidget)
        self.inDbPath.setObjectName(_fromUtf8("inDbPath"))
        self.horizontalLayout.addWidget(self.inDbPath)
        self.btDbPath = QtGui.QToolButton(self.horizontalLayoutWidget)
        self.btDbPath.setObjectName(_fromUtf8("btDbPath"))
        self.horizontalLayout.addWidget(self.btDbPath)
        self.groupBox_2 = QtGui.QGroupBox(apisSettingsDialog)
        self.groupBox_2.setEnabled(True)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 90, 281, 371))
        self.groupBox_2.setFlat(False)
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
        self.gridLayoutWidget_3 = QtGui.QWidget(self.groupBox_2)
        self.gridLayoutWidget_3.setGeometry(QtCore.QRect(10, 120, 261, 41))
        self.gridLayoutWidget_3.setObjectName(_fromUtf8("gridLayoutWidget_3"))
        self.gridLayout_4 = QtGui.QGridLayout(self.gridLayoutWidget_3)
        self.gridLayout_4.setMargin(0)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.toolButton_4 = QtGui.QToolButton(self.gridLayoutWidget_3)
        self.toolButton_4.setObjectName(_fromUtf8("toolButton_4"))
        self.gridLayout_4.addWidget(self.toolButton_4, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.gridLayoutWidget_3)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_4.addWidget(self.label_3, 0, 0, 1, 1)
        self.lineEdit_3 = QtGui.QLineEdit(self.gridLayoutWidget_3)
        self.lineEdit_3.setObjectName(_fromUtf8("lineEdit_3"))
        self.gridLayout_4.addWidget(self.lineEdit_3, 1, 0, 1, 1)
        self.gridLayoutWidget_4 = QtGui.QWidget(self.groupBox_2)
        self.gridLayoutWidget_4.setGeometry(QtCore.QRect(10, 170, 261, 41))
        self.gridLayoutWidget_4.setObjectName(_fromUtf8("gridLayoutWidget_4"))
        self.gridLayout_6 = QtGui.QGridLayout(self.gridLayoutWidget_4)
        self.gridLayout_6.setMargin(0)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.toolButton_6 = QtGui.QToolButton(self.gridLayoutWidget_4)
        self.toolButton_6.setObjectName(_fromUtf8("toolButton_6"))
        self.gridLayout_6.addWidget(self.toolButton_6, 1, 1, 1, 1)
        self.label_5 = QtGui.QLabel(self.gridLayoutWidget_4)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_6.addWidget(self.label_5, 0, 0, 1, 1)
        self.lineEdit_5 = QtGui.QLineEdit(self.gridLayoutWidget_4)
        self.lineEdit_5.setObjectName(_fromUtf8("lineEdit_5"))
        self.gridLayout_6.addWidget(self.lineEdit_5, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(apisSettingsDialog)
        self.buttonBox.setGeometry(QtCore.QRect(130, 470, 156, 23))
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))

        self.retranslateUi(apisSettingsDialog)
        QtCore.QMetaObject.connectSlotsByName(apisSettingsDialog)

    def retranslateUi(self, apisSettingsDialog):
        apisSettingsDialog.setWindowTitle(_translate("apisSettingsDialog", "APIS Einstellungen", None))
        self.groupBox.setTitle(_translate("apisSettingsDialog", "APIS Spatialite Datenbank", None))
        self.btDbPath.setText(_translate("apisSettingsDialog", "...", None))
        self.groupBox_2.setTitle(_translate("apisSettingsDialog", "Pfade", None))
        self.toolButton_2.setText(_translate("apisSettingsDialog", "...", None))
        self.label.setText(_translate("apisSettingsDialog", "Luftbilder", None))
        self.toolButton_3.setText(_translate("apisSettingsDialog", "...", None))
        self.label_2.setText(_translate("apisSettingsDialog", "Orthofotos", None))
        self.toolButton_4.setText(_translate("apisSettingsDialog", "...", None))
        self.label_3.setText(_translate("apisSettingsDialog", "Flugwege", None))
        self.toolButton_6.setText(_translate("apisSettingsDialog", "...", None))
        self.label_5.setText(_translate("apisSettingsDialog", "Bilder", None))

import resource_rc
