# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_site_edit_findspot_handling_form.ui'
#
# Created: Thu Jul 07 17:04:01 2016
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

class Ui_apisSiteEditFindSpotHandlingDialog(object):
    def setupUi(self, apisSiteEditFindSpotHandlingDialog):
        apisSiteEditFindSpotHandlingDialog.setObjectName(_fromUtf8("apisSiteEditFindSpotHandlingDialog"))
        apisSiteEditFindSpotHandlingDialog.resize(452, 311)
        self.verticalLayout = QtGui.QVBoxLayout(apisSiteEditFindSpotHandlingDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(apisSiteEditFindSpotHandlingDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.uiFindSpotAssessmentTable = QtGui.QTableWidget(apisSiteEditFindSpotHandlingDialog)
        self.uiFindSpotAssessmentTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.uiFindSpotAssessmentTable.setAlternatingRowColors(True)
        self.uiFindSpotAssessmentTable.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.uiFindSpotAssessmentTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.uiFindSpotAssessmentTable.setCornerButtonEnabled(False)
        self.uiFindSpotAssessmentTable.setObjectName(_fromUtf8("uiFindSpotAssessmentTable"))
        self.uiFindSpotAssessmentTable.setColumnCount(3)
        self.uiFindSpotAssessmentTable.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.uiFindSpotAssessmentTable.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.uiFindSpotAssessmentTable.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.uiFindSpotAssessmentTable.setHorizontalHeaderItem(2, item)
        self.uiFindSpotAssessmentTable.horizontalHeader().setCascadingSectionResizes(True)
        self.uiFindSpotAssessmentTable.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout.addWidget(self.uiFindSpotAssessmentTable)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.uiCancelEditBtn = QtGui.QPushButton(apisSiteEditFindSpotHandlingDialog)
        self.uiCancelEditBtn.setObjectName(_fromUtf8("uiCancelEditBtn"))
        self.horizontalLayout.addWidget(self.uiCancelEditBtn)
        self.uiResumeEditBtn = QtGui.QPushButton(apisSiteEditFindSpotHandlingDialog)
        self.uiResumeEditBtn.setAutoDefault(False)
        self.uiResumeEditBtn.setObjectName(_fromUtf8("uiResumeEditBtn"))
        self.horizontalLayout.addWidget(self.uiResumeEditBtn)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(apisSiteEditFindSpotHandlingDialog)
        QtCore.QMetaObject.connectSlotsByName(apisSiteEditFindSpotHandlingDialog)

    def retranslateUi(self, apisSiteEditFindSpotHandlingDialog):
        apisSiteEditFindSpotHandlingDialog.setWindowTitle(_translate("apisSiteEditFindSpotHandlingDialog", "APIS Auswirkung auf Fundstellen", None))
        self.label.setText(_translate("apisSiteEditFindSpotHandlingDialog", "Die Veränderungen von Fundort  Geometrie hat Auswirkung auf die folgenden Fundstellen:", None))
        item = self.uiFindSpotAssessmentTable.horizontalHeaderItem(0)
        item.setText(_translate("apisSiteEditFindSpotHandlingDialog", "Fundstelle", None))
        item = self.uiFindSpotAssessmentTable.horizontalHeaderItem(1)
        item.setText(_translate("apisSiteEditFindSpotHandlingDialog", "Befund", None))
        item = self.uiFindSpotAssessmentTable.horizontalHeaderItem(2)
        item.setText(_translate("apisSiteEditFindSpotHandlingDialog", "Aktion", None))
        self.uiCancelEditBtn.setText(_translate("apisSiteEditFindSpotHandlingDialog", "Abbrechen", None))
        self.uiResumeEditBtn.setText(_translate("apisSiteEditFindSpotHandlingDialog", "Fortfahren", None))

