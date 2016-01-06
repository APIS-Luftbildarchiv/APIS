# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_site_selection_list_form.ui'
#
# Created: Sun Jan 03 17:01:46 2016
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
        apisSiteSelectionListDialog.resize(821, 524)
        self.verticalLayout = QtGui.QVBoxLayout(apisSiteSelectionListDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.uiViewSitesBtn = QtGui.QPushButton(apisSiteSelectionListDialog)
        self.uiViewSitesBtn.setEnabled(True)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/images.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiViewSitesBtn.setIcon(icon)
        self.uiViewSitesBtn.setIconSize(QtCore.QSize(24, 24))
        self.uiViewSitesBtn.setAutoDefault(False)
        self.uiViewSitesBtn.setObjectName(_fromUtf8("uiViewSitesBtn"))
        self.horizontalLayout.addWidget(self.uiViewSitesBtn)
        self.uiExportSitesBtn = QtGui.QPushButton(apisSiteSelectionListDialog)
        self.uiExportSitesBtn.setEnabled(True)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/extractgps.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiExportSitesBtn.setIcon(icon1)
        self.uiExportSitesBtn.setIconSize(QtCore.QSize(24, 24))
        self.uiExportSitesBtn.setAutoDefault(False)
        self.uiExportSitesBtn.setObjectName(_fromUtf8("uiExportSitesBtn"))
        self.horizontalLayout.addWidget(self.uiExportSitesBtn)
        self.uiViewInterpretationBtn = QtGui.QPushButton(apisSiteSelectionListDialog)
        self.uiViewInterpretationBtn.setEnabled(True)
        self.uiViewInterpretationBtn.setIcon(icon1)
        self.uiViewInterpretationBtn.setIconSize(QtCore.QSize(24, 24))
        self.uiViewInterpretationBtn.setAutoDefault(False)
        self.uiViewInterpretationBtn.setObjectName(_fromUtf8("uiViewInterpretationBtn"))
        self.horizontalLayout.addWidget(self.uiViewInterpretationBtn)
        self.uiExportListAsPdfBtn = QtGui.QPushButton(apisSiteSelectionListDialog)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/print.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiExportListAsPdfBtn.setIcon(icon2)
        self.uiExportListAsPdfBtn.setIconSize(QtCore.QSize(24, 24))
        self.uiExportListAsPdfBtn.setAutoDefault(False)
        self.uiExportListAsPdfBtn.setObjectName(_fromUtf8("uiExportListAsPdfBtn"))
        self.horizontalLayout.addWidget(self.uiExportListAsPdfBtn)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.uiSiteListTableV = QtGui.QTableView(apisSiteSelectionListDialog)
        self.uiSiteListTableV.setObjectName(_fromUtf8("uiSiteListTableV"))
        self.verticalLayout.addWidget(self.uiSiteListTableV)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label = QtGui.QLabel(apisSiteSelectionListDialog)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_2.addWidget(self.label)
        self.uiImageCountLbl = QtGui.QLabel(apisSiteSelectionListDialog)
        self.uiImageCountLbl.setAlignment(QtCore.Qt.AlignCenter)
        self.uiImageCountLbl.setObjectName(_fromUtf8("uiImageCountLbl"))
        self.horizontalLayout_2.addWidget(self.uiImageCountLbl)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(apisSiteSelectionListDialog)
        QtCore.QMetaObject.connectSlotsByName(apisSiteSelectionListDialog)

    def retranslateUi(self, apisSiteSelectionListDialog):
        apisSiteSelectionListDialog.setWindowTitle(_translate("apisSiteSelectionListDialog", "APIS Fundorte Auswahl", None))
        self.uiViewSitesBtn.setText(_translate("apisSiteSelectionListDialog", "Fundorte Anzeigen", None))
        self.uiExportSitesBtn.setText(_translate("apisSiteSelectionListDialog", "Fundorte Export", None))
        self.uiViewInterpretationBtn.setText(_translate("apisSiteSelectionListDialog", "Interpretation Anzeigen", None))
        self.uiExportListAsPdfBtn.setText(_translate("apisSiteSelectionListDialog", "PDF Export", None))
        self.label.setText(_translate("apisSiteSelectionListDialog", "Fundorte:", None))
        self.uiImageCountLbl.setText(_translate("apisSiteSelectionListDialog", "0", None))

import resource_rc
