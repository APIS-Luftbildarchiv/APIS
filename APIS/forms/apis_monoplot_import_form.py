# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_monoplot_import_form.ui'
#
# Created: Sat Jul 16 19:24:14 2016
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

class Ui_apisMonoplotImportDialog(object):
    def setupUi(self, apisMonoplotImportDialog):
        apisMonoplotImportDialog.setObjectName(_fromUtf8("apisMonoplotImportDialog"))
        apisMonoplotImportDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        apisMonoplotImportDialog.resize(400, 250)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/apis.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        apisMonoplotImportDialog.setWindowIcon(icon)
        apisMonoplotImportDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(apisMonoplotImportDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.uiReportPTxt = QtGui.QPlainTextEdit(apisMonoplotImportDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiReportPTxt.sizePolicy().hasHeightForWidth())
        self.uiReportPTxt.setSizePolicy(sizePolicy)
        self.uiReportPTxt.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.uiReportPTxt.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.uiReportPTxt.setPlainText(_fromUtf8(""))
        self.uiReportPTxt.setObjectName(_fromUtf8("uiReportPTxt"))
        self.verticalLayout.addWidget(self.uiReportPTxt)
        self.uiImportBtn = QtGui.QPushButton(apisMonoplotImportDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiImportBtn.sizePolicy().hasHeightForWidth())
        self.uiImportBtn.setSizePolicy(sizePolicy)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/monoplot.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiImportBtn.setIcon(icon1)
        self.uiImportBtn.setIconSize(QtCore.QSize(24, 24))
        self.uiImportBtn.setAutoDefault(False)
        self.uiImportBtn.setObjectName(_fromUtf8("uiImportBtn"))
        self.verticalLayout.addWidget(self.uiImportBtn)

        self.retranslateUi(apisMonoplotImportDialog)
        QtCore.QMetaObject.connectSlotsByName(apisMonoplotImportDialog)

    def retranslateUi(self, apisMonoplotImportDialog):
        apisMonoplotImportDialog.setWindowTitle(_translate("apisMonoplotImportDialog", "APIS MONOPLOT Import", None))
        self.uiImportBtn.setText(_translate("apisMonoplotImportDialog", "Importieren", None))

import resource_rc
