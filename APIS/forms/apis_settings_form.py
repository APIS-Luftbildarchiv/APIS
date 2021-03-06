# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_settings_form.ui'
#
# Created: Fri Dec 16 17:29:15 2016
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
        apisSettingsDialog.resize(635, 390)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(apisSettingsDialog.sizePolicy().hasHeightForWidth())
        apisSettingsDialog.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/apis.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        apisSettingsDialog.setWindowIcon(icon)
        apisSettingsDialog.setLocale(QtCore.QLocale(QtCore.QLocale.German, QtCore.QLocale.Austria))
        apisSettingsDialog.setSizeGripEnabled(False)
        apisSettingsDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(apisSettingsDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox_2 = QtGui.QGroupBox(apisSettingsDialog)
        self.groupBox_2.setStyleSheet(_fromUtf8(""))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.uiConfigIniFileEdit = QtGui.QLineEdit(self.groupBox_2)
        self.uiConfigIniFileEdit.setReadOnly(True)
        self.uiConfigIniFileEdit.setObjectName(_fromUtf8("uiConfigIniFileEdit"))
        self.horizontalLayout_2.addWidget(self.uiConfigIniFileEdit)
        self.uiConfigIniFileTBtn = QtGui.QToolButton(self.groupBox_2)
        self.uiConfigIniFileTBtn.setObjectName(_fromUtf8("uiConfigIniFileTBtn"))
        self.horizontalLayout_2.addWidget(self.uiConfigIniFileTBtn)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox = QtGui.QGroupBox(apisSettingsDialog)
        self.groupBox.setMinimumSize(QtCore.QSize(0, 80))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.uiUpdateImageRegistryBtn = QtGui.QPushButton(self.groupBox)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/update.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiUpdateImageRegistryBtn.setIcon(icon1)
        self.uiUpdateImageRegistryBtn.setIconSize(QtCore.QSize(30, 30))
        self.uiUpdateImageRegistryBtn.setAutoDefault(False)
        self.uiUpdateImageRegistryBtn.setFlat(False)
        self.uiUpdateImageRegistryBtn.setObjectName(_fromUtf8("uiUpdateImageRegistryBtn"))
        self.verticalLayout_2.addWidget(self.uiUpdateImageRegistryBtn)
        self.verticalLayout.addWidget(self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(apisSettingsDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Reset)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(apisSettingsDialog)
        QtCore.QMetaObject.connectSlotsByName(apisSettingsDialog)

    def retranslateUi(self, apisSettingsDialog):
        apisSettingsDialog.setWindowTitle(_translate("apisSettingsDialog", "APIS Einstellungen", None))
        self.groupBox_2.setTitle(_translate("apisSettingsDialog", "APIS Konfiguration (INI Datei)", None))
        self.uiConfigIniFileEdit.setPlaceholderText(_translate("apisSettingsDialog", "Wählen Sie eine APIS INI Datei aus ...", None))
        self.uiConfigIniFileTBtn.setText(_translate("apisSettingsDialog", "...", None))
        self.groupBox.setToolTip(_translate("apisSettingsDialog", "<html><head/><body><p><span style=\" font-weight:600;\">APIS Image Registry</span></p><p>Die APIS Image Registry beinhaltet Informationen über die Verfügbarkeit von Luftbildern, hochauflösende Luftbildern und Orthofotos am Server/im angegbenen Verzeichnis.</p><p>Wenn neue Daten (Luftbilder etc.) hinzugefügt werden in den entsprechenden Verzeichnissen (Server oder Lokal) muss die Image Registry aktualisiert werden.</p></body></html>", None))
        self.groupBox.setTitle(_translate("apisSettingsDialog", "APIS Image Registry", None))
        self.uiUpdateImageRegistryBtn.setText(_translate("apisSettingsDialog", "Lokale Image Registry aktualisieren", None))

import resource_rc
