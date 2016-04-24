# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_findspot_selection_list_form.ui'
#
# Created: Sat Apr 16 09:36:59 2016
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

class Ui_apisFindSpotSelectionListDialog(object):
    def setupUi(self, apisFindSpotSelectionListDialog):
        apisFindSpotSelectionListDialog.setObjectName(_fromUtf8("apisFindSpotSelectionListDialog"))
        apisFindSpotSelectionListDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        apisFindSpotSelectionListDialog.resize(800, 500)
        apisFindSpotSelectionListDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(apisFindSpotSelectionListDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.uiViewFindSpotsBtn = QtGui.QPushButton(apisFindSpotSelectionListDialog)
        self.uiViewFindSpotsBtn.setEnabled(False)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/images.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiViewFindSpotsBtn.setIcon(icon)
        self.uiViewFindSpotsBtn.setIconSize(QtCore.QSize(24, 24))
        self.uiViewFindSpotsBtn.setAutoDefault(False)
        self.uiViewFindSpotsBtn.setObjectName(_fromUtf8("uiViewFindSpotsBtn"))
        self.horizontalLayout.addWidget(self.uiViewFindSpotsBtn)
        self.uiExportFindSpotsBtn = QtGui.QPushButton(apisFindSpotSelectionListDialog)
        self.uiExportFindSpotsBtn.setEnabled(False)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/extractgps.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiExportFindSpotsBtn.setIcon(icon1)
        self.uiExportFindSpotsBtn.setIconSize(QtCore.QSize(24, 24))
        self.uiExportFindSpotsBtn.setAutoDefault(False)
        self.uiExportFindSpotsBtn.setObjectName(_fromUtf8("uiExportFindSpotsBtn"))
        self.horizontalLayout.addWidget(self.uiExportFindSpotsBtn)
        self.uiExportListAsPdfBtn = QtGui.QPushButton(apisFindSpotSelectionListDialog)
        self.uiExportListAsPdfBtn.setEnabled(False)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/print.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiExportListAsPdfBtn.setIcon(icon2)
        self.uiExportListAsPdfBtn.setIconSize(QtCore.QSize(24, 24))
        self.uiExportListAsPdfBtn.setAutoDefault(False)
        self.uiExportListAsPdfBtn.setObjectName(_fromUtf8("uiExportListAsPdfBtn"))
        self.horizontalLayout.addWidget(self.uiExportListAsPdfBtn)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.uiFindSpotListTableV = QtGui.QTableView(apisFindSpotSelectionListDialog)
        self.uiFindSpotListTableV.setFrameShadow(QtGui.QFrame.Sunken)
        self.uiFindSpotListTableV.setGridStyle(QtCore.Qt.DotLine)
        self.uiFindSpotListTableV.setObjectName(_fromUtf8("uiFindSpotListTableV"))
        self.verticalLayout.addWidget(self.uiFindSpotListTableV)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.uiFindSpotCountLbl = QtGui.QLabel(apisFindSpotSelectionListDialog)
        self.uiFindSpotCountLbl.setAlignment(QtCore.Qt.AlignCenter)
        self.uiFindSpotCountLbl.setObjectName(_fromUtf8("uiFindSpotCountLbl"))
        self.horizontalLayout_2.addWidget(self.uiFindSpotCountLbl)
        self.label = QtGui.QLabel(apisFindSpotSelectionListDialog)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_2.addWidget(self.label)
        self.uiInfoLbl = QtGui.QLabel(apisFindSpotSelectionListDialog)
        self.uiInfoLbl.setText(_fromUtf8(""))
        self.uiInfoLbl.setObjectName(_fromUtf8("uiInfoLbl"))
        self.horizontalLayout_2.addWidget(self.uiInfoLbl)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(apisFindSpotSelectionListDialog)
        QtCore.QMetaObject.connectSlotsByName(apisFindSpotSelectionListDialog)

    def retranslateUi(self, apisFindSpotSelectionListDialog):
        apisFindSpotSelectionListDialog.setWindowTitle(_translate("apisFindSpotSelectionListDialog", "APIS Fundstelle Auswahl", None))
        self.uiViewFindSpotsBtn.setText(_translate("apisFindSpotSelectionListDialog", "Fundstellen in QGIS laden", None))
        self.uiExportFindSpotsBtn.setText(_translate("apisFindSpotSelectionListDialog", "Fundstellen Export", None))
        self.uiExportListAsPdfBtn.setText(_translate("apisFindSpotSelectionListDialog", "PDF Export", None))
        self.uiFindSpotCountLbl.setText(_translate("apisFindSpotSelectionListDialog", "0", None))
        self.label.setText(_translate("apisFindSpotSelectionListDialog", "Fundstellen", None))

import resource_rc
