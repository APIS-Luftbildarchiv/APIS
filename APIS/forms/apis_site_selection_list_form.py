# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_site_selection_list_form.ui'
#
# Created: Wed Apr 27 09:52:16 2016
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

class Ui_apisSiteSelectionListDialog(object):
    def setupUi(self, apisSiteSelectionListDialog):
        apisSiteSelectionListDialog.setObjectName(_fromUtf8("apisSiteSelectionListDialog"))
        apisSiteSelectionListDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        apisSiteSelectionListDialog.resize(800, 500)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/apis.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        apisSiteSelectionListDialog.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(apisSiteSelectionListDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.uiViewSitesBtn = QtGui.QPushButton(apisSiteSelectionListDialog)
        self.uiViewSitesBtn.setEnabled(False)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/layer.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiViewSitesBtn.setIcon(icon1)
        self.uiViewSitesBtn.setIconSize(QtCore.QSize(24, 24))
        self.uiViewSitesBtn.setAutoDefault(False)
        self.uiViewSitesBtn.setObjectName(_fromUtf8("uiViewSitesBtn"))
        self.horizontalLayout.addWidget(self.uiViewSitesBtn)
        self.uiViewInterpretationBtn = QtGui.QPushButton(apisSiteSelectionListDialog)
        self.uiViewInterpretationBtn.setEnabled(False)
        self.uiViewInterpretationBtn.setIcon(icon1)
        self.uiViewInterpretationBtn.setIconSize(QtCore.QSize(24, 24))
        self.uiViewInterpretationBtn.setAutoDefault(False)
        self.uiViewInterpretationBtn.setObjectName(_fromUtf8("uiViewInterpretationBtn"))
        self.horizontalLayout.addWidget(self.uiViewInterpretationBtn)
        self.uiExportSitesBtn = QtGui.QPushButton(apisSiteSelectionListDialog)
        self.uiExportSitesBtn.setEnabled(False)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/shp_export.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiExportSitesBtn.setIcon(icon2)
        self.uiExportSitesBtn.setIconSize(QtCore.QSize(24, 24))
        self.uiExportSitesBtn.setAutoDefault(False)
        self.uiExportSitesBtn.setObjectName(_fromUtf8("uiExportSitesBtn"))
        self.horizontalLayout.addWidget(self.uiExportSitesBtn)
        self.uiExportListAsPdfBtn = QtGui.QPushButton(apisSiteSelectionListDialog)
        self.uiExportListAsPdfBtn.setEnabled(False)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/pdf_export.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiExportListAsPdfBtn.setIcon(icon3)
        self.uiExportListAsPdfBtn.setIconSize(QtCore.QSize(24, 24))
        self.uiExportListAsPdfBtn.setAutoDefault(False)
        self.uiExportListAsPdfBtn.setObjectName(_fromUtf8("uiExportListAsPdfBtn"))
        self.horizontalLayout.addWidget(self.uiExportListAsPdfBtn)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.uiSiteListTableV = QtGui.QTableView(apisSiteSelectionListDialog)
        self.uiSiteListTableV.setGridStyle(QtCore.Qt.DotLine)
        self.uiSiteListTableV.setSortingEnabled(False)
        self.uiSiteListTableV.setObjectName(_fromUtf8("uiSiteListTableV"))
        self.verticalLayout.addWidget(self.uiSiteListTableV)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.uiImageCountLbl = QtGui.QLabel(apisSiteSelectionListDialog)
        self.uiImageCountLbl.setAlignment(QtCore.Qt.AlignCenter)
        self.uiImageCountLbl.setObjectName(_fromUtf8("uiImageCountLbl"))
        self.horizontalLayout_2.addWidget(self.uiImageCountLbl)
        self.label = QtGui.QLabel(apisSiteSelectionListDialog)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_2.addWidget(self.label)
        self.uiInfoLbl = QtGui.QLabel(apisSiteSelectionListDialog)
        self.uiInfoLbl.setText(_fromUtf8(""))
        self.uiInfoLbl.setObjectName(_fromUtf8("uiInfoLbl"))
        self.horizontalLayout_2.addWidget(self.uiInfoLbl)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(apisSiteSelectionListDialog)
        QtCore.QMetaObject.connectSlotsByName(apisSiteSelectionListDialog)
        apisSiteSelectionListDialog.setTabOrder(self.uiSiteListTableV, self.uiViewSitesBtn)
        apisSiteSelectionListDialog.setTabOrder(self.uiViewSitesBtn, self.uiViewInterpretationBtn)
        apisSiteSelectionListDialog.setTabOrder(self.uiViewInterpretationBtn, self.uiExportSitesBtn)
        apisSiteSelectionListDialog.setTabOrder(self.uiExportSitesBtn, self.uiExportListAsPdfBtn)

    def retranslateUi(self, apisSiteSelectionListDialog):
        apisSiteSelectionListDialog.setWindowTitle(_translate("apisSiteSelectionListDialog", "APIS Fundorte Auswahl", None))
        self.uiViewSitesBtn.setText(_translate("apisSiteSelectionListDialog", "Fundorte in QGIS laden", None))
        self.uiViewInterpretationBtn.setText(_translate("apisSiteSelectionListDialog", "Interpretation in QGIS laden", None))
        self.uiExportSitesBtn.setText(_translate("apisSiteSelectionListDialog", "Fundorte Export", None))
        self.uiExportListAsPdfBtn.setText(_translate("apisSiteSelectionListDialog", "PDF Export", None))
        self.uiImageCountLbl.setText(_translate("apisSiteSelectionListDialog", "0", None))
        self.label.setText(_translate("apisSiteSelectionListDialog", "Fundorte", None))

import resource_rc
