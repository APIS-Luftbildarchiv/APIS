# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_film_number_selection_form.ui'
#
# Created: Tue Jun 02 14:12:12 2015
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

class Ui_apisFilmNumberSelectionDialog(object):
    def setupUi(self, apisFilmNumberSelectionDialog):
        apisFilmNumberSelectionDialog.setObjectName(_fromUtf8("apisFilmNumberSelectionDialog"))
        apisFilmNumberSelectionDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        apisFilmNumberSelectionDialog.resize(300, 70)
        apisFilmNumberSelectionDialog.setFocusPolicy(QtCore.Qt.TabFocus)
        apisFilmNumberSelectionDialog.setModal(True)
        self.uiButtonBox = QtGui.QDialogButtonBox(apisFilmNumberSelectionDialog)
        self.uiButtonBox.setGeometry(QtCore.QRect(220, 10, 75, 52))
        self.uiButtonBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.uiButtonBox.setOrientation(QtCore.Qt.Vertical)
        self.uiButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName(_fromUtf8("uiButtonBox"))
        self.gridLayoutWidget = QtGui.QWidget(apisFilmNumberSelectionDialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 201, 51))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiFilmNumberEdit = QtGui.QLineEdit(self.gridLayoutWidget)
        self.uiFilmNumberEdit.setMaxLength(8)
        self.uiFilmNumberEdit.setObjectName(_fromUtf8("uiFilmNumberEdit"))
        self.gridLayout.addWidget(self.uiFilmNumberEdit, 0, 1, 1, 1)
        self.uiFilmNumberLbl = QtGui.QLabel(self.gridLayoutWidget)
        self.uiFilmNumberLbl.setObjectName(_fromUtf8("uiFilmNumberLbl"))
        self.gridLayout.addWidget(self.uiFilmNumberLbl, 0, 0, 1, 1)

        self.retranslateUi(apisFilmNumberSelectionDialog)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), apisFilmNumberSelectionDialog.accept)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), apisFilmNumberSelectionDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(apisFilmNumberSelectionDialog)
        apisFilmNumberSelectionDialog.setTabOrder(self.uiFilmNumberEdit, self.uiButtonBox)

    def retranslateUi(self, apisFilmNumberSelectionDialog):
        apisFilmNumberSelectionDialog.setWindowTitle(_translate("apisFilmNumberSelectionDialog", "Film Nummer Auswahl", None))
        self.uiFilmNumberLbl.setText(_translate("apisFilmNumberSelectionDialog", "Filmnummer:", None))

