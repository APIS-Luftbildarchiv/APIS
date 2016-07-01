# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_findspot_selection_list_form.ui'
#
# Created: Fri May 20 18:15:23 2016
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
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/apis.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        apisFindSpotSelectionListDialog.setWindowIcon(icon)
        apisFindSpotSelectionListDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(apisFindSpotSelectionListDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.uiViewFindSpotsBtn = QtGui.QPushButton(apisFindSpotSelectionListDialog)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/layer.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiViewFindSpotsBtn.setIcon(icon1)
        self.uiViewFindSpotsBtn.setIconSize(QtCore.QSize(24, 24))
        self.uiViewFindSpotsBtn.setAutoDefault(False)
        self.uiViewFindSpotsBtn.setObjectName(_fromUtf8("uiViewFindSpotsBtn"))
        self.horizontalLayout.addWidget(self.uiViewFindSpotsBtn)
        self.uiExportFindSpotsAsShpBtn = QtGui.QPushButton(apisFindSpotSelectionListDialog)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/shp_export.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiExportFindSpotsAsShpBtn.setIcon(icon2)
        self.uiExportFindSpotsAsShpBtn.setIconSize(QtCore.QSize(24, 24))
        self.uiExportFindSpotsAsShpBtn.setAutoDefault(False)
        self.uiExportFindSpotsAsShpBtn.setObjectName(_fromUtf8("uiExportFindSpotsAsShpBtn"))
        self.horizontalLayout.addWidget(self.uiExportFindSpotsAsShpBtn)
        self.uiExportFindSpotAsPdfBtn = QtGui.QPushButton(apisFindSpotSelectionListDialog)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/pdf_export.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiExportFindSpotAsPdfBtn.setIcon(icon3)
        self.uiExportFindSpotAsPdfBtn.setIconSize(QtCore.QSize(24, 24))
        self.uiExportFindSpotAsPdfBtn.setAutoDefault(False)
        self.uiExportFindSpotAsPdfBtn.setObjectName(_fromUtf8("uiExportFindSpotAsPdfBtn"))
        self.horizontalLayout.addWidget(self.uiExportFindSpotAsPdfBtn)
        self.uiExportListAsPdfBtn = QtGui.QPushButton(apisFindSpotSelectionListDialog)
        self.uiExportListAsPdfBtn.setIcon(icon3)
        self.uiExportListAsPdfBtn.setIconSize(QtCore.QSize(24, 24))
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
        self.uiExportFindSpotsAsShpBtn.setText(_translate("apisFindSpotSelectionListDialog", "Fundstellen Export", None))
        self.uiExportFindSpotAsPdfBtn.setText(_translate("apisFindSpotSelectionListDialog", "PDF Export Fundstellen", None))
        self.uiExportListAsPdfBtn.setText(_translate("apisFindSpotSelectionListDialog", "PDF Export Liste", None))
        self.uiFindSpotCountLbl.setText(_translate("apisFindSpotSelectionListDialog", "0", None))
        self.label.setText(_translate("apisFindSpotSelectionListDialog", "Fundstellen", None))

import resource_rc
