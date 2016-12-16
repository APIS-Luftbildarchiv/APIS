# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_overpass_request_form.ui'
#
# Created: Thu Sep 29 19:53:08 2016
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

class Ui_apisOverpassRequestDialog(object):
    def setupUi(self, apisOverpassRequestDialog):
        apisOverpassRequestDialog.setObjectName(_fromUtf8("apisOverpassRequestDialog"))
        apisOverpassRequestDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        apisOverpassRequestDialog.resize(343, 279)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/apis.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        apisOverpassRequestDialog.setWindowIcon(icon)
        apisOverpassRequestDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(apisOverpassRequestDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(apisOverpassRequestDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.uiLonLbl = QtGui.QLabel(apisOverpassRequestDialog)
        self.uiLonLbl.setObjectName(_fromUtf8("uiLonLbl"))
        self.horizontalLayout.addWidget(self.uiLonLbl)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_3 = QtGui.QLabel(apisOverpassRequestDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_2.addWidget(self.label_3)
        self.uiLatLbl = QtGui.QLabel(apisOverpassRequestDialog)
        self.uiLatLbl.setObjectName(_fromUtf8("uiLatLbl"))
        self.horizontalLayout_2.addWidget(self.uiLatLbl)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.uiRequestBtn = QtGui.QPushButton(apisOverpassRequestDialog)
        self.uiRequestBtn.setEnabled(False)
        self.uiRequestBtn.setAutoDefault(False)
        self.uiRequestBtn.setObjectName(_fromUtf8("uiRequestBtn"))
        self.verticalLayout.addWidget(self.uiRequestBtn)
        self.uiAdminLevelList = QtGui.QListWidget(apisOverpassRequestDialog)
        self.uiAdminLevelList.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.uiAdminLevelList.setProperty("showDropIndicator", False)
        self.uiAdminLevelList.setAlternatingRowColors(False)
        self.uiAdminLevelList.setObjectName(_fromUtf8("uiAdminLevelList"))
        self.verticalLayout.addWidget(self.uiAdminLevelList)
        self.label_2 = QtGui.QLabel(apisOverpassRequestDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)

        self.retranslateUi(apisOverpassRequestDialog)
        QtCore.QMetaObject.connectSlotsByName(apisOverpassRequestDialog)

    def retranslateUi(self, apisOverpassRequestDialog):
        apisOverpassRequestDialog.setWindowTitle(_translate("apisOverpassRequestDialog", "APIS Overpass Request", None))
        self.label.setText(_translate("apisOverpassRequestDialog", "Geogr. Länge:", None))
        self.uiLonLbl.setText(_translate("apisOverpassRequestDialog", "---", None))
        self.label_3.setText(_translate("apisOverpassRequestDialog", "Geogr. Breite:", None))
        self.uiLatLbl.setText(_translate("apisOverpassRequestDialog", "---", None))
        self.uiRequestBtn.setText(_translate("apisOverpassRequestDialog", "OSM Admin Levels Abfrage via Overpass API", None))
        self.label_2.setText(_translate("apisOverpassRequestDialog", "Mit Doppelklick übernehmen.", None))

import resource_rc
