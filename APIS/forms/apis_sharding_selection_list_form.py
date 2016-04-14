# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_sharding_selection_list_form.ui'
#
# Created: Wed Apr 13 14:46:24 2016
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

class Ui_apisShardingSelectionListDialog(object):
    def setupUi(self, apisShardingSelectionListDialog):
        apisShardingSelectionListDialog.setObjectName(_fromUtf8("apisShardingSelectionListDialog"))
        apisShardingSelectionListDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        apisShardingSelectionListDialog.resize(800, 500)
        self.verticalLayout = QtGui.QVBoxLayout(apisShardingSelectionListDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(apisShardingSelectionListDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.uiSiteNumberLbl = QtGui.QLabel(apisShardingSelectionListDialog)
        self.uiSiteNumberLbl.setObjectName(_fromUtf8("uiSiteNumberLbl"))
        self.horizontalLayout.addWidget(self.uiSiteNumberLbl)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.uiNewShardingBtn = QtGui.QPushButton(apisShardingSelectionListDialog)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/add.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiNewShardingBtn.setIcon(icon)
        self.uiNewShardingBtn.setIconSize(QtCore.QSize(24, 24))
        self.uiNewShardingBtn.setAutoDefault(False)
        self.uiNewShardingBtn.setObjectName(_fromUtf8("uiNewShardingBtn"))
        self.horizontalLayout.addWidget(self.uiNewShardingBtn)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.uiShardingListTableV = QtGui.QTableView(apisShardingSelectionListDialog)
        self.uiShardingListTableV.setObjectName(_fromUtf8("uiShardingListTableV"))
        self.verticalLayout.addWidget(self.uiShardingListTableV)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_2 = QtGui.QLabel(apisShardingSelectionListDialog)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.uiShardingCountLbl = QtGui.QLabel(apisShardingSelectionListDialog)
        self.uiShardingCountLbl.setAlignment(QtCore.Qt.AlignCenter)
        self.uiShardingCountLbl.setObjectName(_fromUtf8("uiShardingCountLbl"))
        self.horizontalLayout_2.addWidget(self.uiShardingCountLbl)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(apisShardingSelectionListDialog)
        QtCore.QMetaObject.connectSlotsByName(apisShardingSelectionListDialog)

    def retranslateUi(self, apisShardingSelectionListDialog):
        apisShardingSelectionListDialog.setWindowTitle(_translate("apisShardingSelectionListDialog", "APIS Begehung Auswahl", None))
        self.label.setText(_translate("apisShardingSelectionListDialog", "Fundort Nummer: ", None))
        self.uiSiteNumberLbl.setText(_translate("apisShardingSelectionListDialog", "---", None))
        self.uiNewShardingBtn.setText(_translate("apisShardingSelectionListDialog", "Neue Begehung", None))
        self.label_2.setText(_translate("apisShardingSelectionListDialog", "Begehungen:", None))
        self.uiShardingCountLbl.setText(_translate("apisShardingSelectionListDialog", "0", None))

import resource_rc
