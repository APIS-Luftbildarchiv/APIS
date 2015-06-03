# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_settings_form.ui'
#
# Created: Wed Jun 03 08:31:34 2015
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
        apisSettingsDialog.resize(300, 120)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(apisSettingsDialog.sizePolicy().hasHeightForWidth())
        apisSettingsDialog.setSizePolicy(sizePolicy)
        apisSettingsDialog.setMinimumSize(QtCore.QSize(300, 120))
        apisSettingsDialog.setMaximumSize(QtCore.QSize(300, 120))
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
        self.uiDatabaseFileEdit = QtGui.QLineEdit(self.horizontalLayoutWidget)
        self.uiDatabaseFileEdit.setReadOnly(True)
        self.uiDatabaseFileEdit.setObjectName(_fromUtf8("uiDatabaseFileEdit"))
        self.horizontalLayout.addWidget(self.uiDatabaseFileEdit)
        self.uiDatabaseFileTBtn = QtGui.QToolButton(self.horizontalLayoutWidget)
        self.uiDatabaseFileTBtn.setObjectName(_fromUtf8("uiDatabaseFileTBtn"))
        self.horizontalLayout.addWidget(self.uiDatabaseFileTBtn)
        self.buttonBox = QtGui.QDialogButtonBox(apisSettingsDialog)
        self.buttonBox.setGeometry(QtCore.QRect(75, 90, 211, 23))
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Reset)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))

        self.retranslateUi(apisSettingsDialog)
        QtCore.QMetaObject.connectSlotsByName(apisSettingsDialog)

    def retranslateUi(self, apisSettingsDialog):
        apisSettingsDialog.setWindowTitle(_translate("apisSettingsDialog", "APIS Einstellungen", None))
        self.groupBox.setTitle(_translate("apisSettingsDialog", "APIS Spatialite Datenbank", None))
        self.uiDatabaseFileEdit.setPlaceholderText(_translate("apisSettingsDialog", "Wählen Sie die APIS Datenbank aus ...", None))
        self.uiDatabaseFileTBtn.setText(_translate("apisSettingsDialog", "...", None))

import resource_rc
