# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'apis_dialog_base.ui'
#
# Created: Mon Apr 13 17:00:05 2015
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

class Ui_ApisDialogBase(object):
    def setupUi(self, ApisDialogBase):
        ApisDialogBase.setObjectName(_fromUtf8("ApisDialogBase"))
        ApisDialogBase.resize(803, 615)
        self.button_box = QtGui.QDialogButtonBox(ApisDialogBase)
        self.button_box.setGeometry(QtCore.QRect(270, 400, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.button_box.setObjectName(_fromUtf8("button_box"))
        self.verticalLayoutWidget = QtGui.QWidget(ApisDialogBase)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(150, 50, 401, 181))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(ApisDialogBase)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("accepted()")), ApisDialogBase.accept)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("rejected()")), ApisDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(ApisDialogBase)

    def retranslateUi(self, ApisDialogBase):
        ApisDialogBase.setWindowTitle(_translate("ApisDialogBase", "APIS - Filmeingabe", None))

