# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_findingtype_detail_form.ui'
#
# Created: Mon May 16 16:04:19 2016
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

class Ui_apisFindingTypeDetailDialog(object):
    def setupUi(self, apisFindingTypeDetailDialog):
        apisFindingTypeDetailDialog.setObjectName(_fromUtf8("apisFindingTypeDetailDialog"))
        apisFindingTypeDetailDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        apisFindingTypeDetailDialog.resize(350, 425)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/apis.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        apisFindingTypeDetailDialog.setWindowIcon(icon)
        apisFindingTypeDetailDialog.setModal(True)
        self.formLayout = QtGui.QFormLayout(apisFindingTypeDetailDialog)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(apisFindingTypeDetailDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.uiFindingTypeEdit = QtGui.QLineEdit(apisFindingTypeDetailDialog)
        self.uiFindingTypeEdit.setStyleSheet(_fromUtf8("background-color: rgb(218, 218, 218);"))
        self.uiFindingTypeEdit.setReadOnly(True)
        self.uiFindingTypeEdit.setObjectName(_fromUtf8("uiFindingTypeEdit"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.uiFindingTypeEdit)
        self.label_2 = QtGui.QLabel(apisFindingTypeDetailDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.uiFindingTypeDetailEdit = QtGui.QLineEdit(apisFindingTypeDetailDialog)
        self.uiFindingTypeDetailEdit.setStyleSheet(_fromUtf8("background-color: rgb(218, 218, 218);"))
        self.uiFindingTypeDetailEdit.setReadOnly(True)
        self.uiFindingTypeDetailEdit.setObjectName(_fromUtf8("uiFindingTypeDetailEdit"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.uiFindingTypeDetailEdit)
        self.label_3 = QtGui.QLabel(apisFindingTypeDetailDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self.uiFindingTypeDetailNewEdit = QtGui.QLineEdit(apisFindingTypeDetailDialog)
        self.uiFindingTypeDetailNewEdit.setStyleSheet(_fromUtf8("background-color: rgb(218, 218, 218);"))
        self.uiFindingTypeDetailNewEdit.setReadOnly(True)
        self.uiFindingTypeDetailNewEdit.setObjectName(_fromUtf8("uiFindingTypeDetailNewEdit"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.uiFindingTypeDetailNewEdit)
        self.uiFindingTypeDetailTableV = QtGui.QTableView(apisFindingTypeDetailDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiFindingTypeDetailTableV.sizePolicy().hasHeightForWidth())
        self.uiFindingTypeDetailTableV.setSizePolicy(sizePolicy)
        self.uiFindingTypeDetailTableV.setMinimumSize(QtCore.QSize(0, 300))
        self.uiFindingTypeDetailTableV.setStyleSheet(_fromUtf8("selection-background-color: rgb(152, 202, 255);\n"
"selection-color: rgb(0, 0, 0);"))
        self.uiFindingTypeDetailTableV.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.uiFindingTypeDetailTableV.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.uiFindingTypeDetailTableV.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.uiFindingTypeDetailTableV.setObjectName(_fromUtf8("uiFindingTypeDetailTableV"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.SpanningRole, self.uiFindingTypeDetailTableV)
        self.uiButtonBox = QtGui.QDialogButtonBox(apisFindingTypeDetailDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.uiButtonBox.setCenterButtons(False)
        self.uiButtonBox.setObjectName(_fromUtf8("uiButtonBox"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.SpanningRole, self.uiButtonBox)

        self.retranslateUi(apisFindingTypeDetailDialog)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), apisFindingTypeDetailDialog.accept)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), apisFindingTypeDetailDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(apisFindingTypeDetailDialog)

    def retranslateUi(self, apisFindingTypeDetailDialog):
        apisFindingTypeDetailDialog.setWindowTitle(_translate("apisFindingTypeDetailDialog", "APIS Fundart Detail", None))
        self.label.setText(_translate("apisFindingTypeDetailDialog", "Fundart:", None))
        self.label_2.setText(_translate("apisFindingTypeDetailDialog", "Fundart Detail:", None))
        self.label_3.setText(_translate("apisFindingTypeDetailDialog", "Auswahl:", None))

import resource_rc
