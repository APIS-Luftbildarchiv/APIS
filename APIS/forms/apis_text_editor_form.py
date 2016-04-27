# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_text_editor_form.ui'
#
# Created: Wed Apr 27 09:52:17 2016
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

class Ui_apisTextEditorDialog(object):
    def setupUi(self, apisTextEditorDialog):
        apisTextEditorDialog.setObjectName(_fromUtf8("apisTextEditorDialog"))
        apisTextEditorDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        apisTextEditorDialog.resize(400, 300)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/apis.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        apisTextEditorDialog.setWindowIcon(icon)
        apisTextEditorDialog.setLocale(QtCore.QLocale(QtCore.QLocale.German, QtCore.QLocale.Austria))
        apisTextEditorDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(apisTextEditorDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.uiTextPTxt = QtGui.QPlainTextEdit(apisTextEditorDialog)
        self.uiTextPTxt.setObjectName(_fromUtf8("uiTextPTxt"))
        self.verticalLayout.addWidget(self.uiTextPTxt)
        self.buttonBox = QtGui.QDialogButtonBox(apisTextEditorDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(apisTextEditorDialog)
        QtCore.QMetaObject.connectSlotsByName(apisTextEditorDialog)

    def retranslateUi(self, apisTextEditorDialog):
        apisTextEditorDialog.setWindowTitle(_translate("apisTextEditorDialog", "APIS Text Editor", None))

import resource_rc
