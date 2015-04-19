# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_film_form.ui'
#
# Created: Sat Apr 18 15:39:05 2015
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

class Ui_apisFilmDialog(object):
    def setupUi(self, apisFilmDialog):
        apisFilmDialog.setObjectName(_fromUtf8("apisFilmDialog"))
        apisFilmDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        apisFilmDialog.resize(400, 300)
        apisFilmDialog.setLocale(QtCore.QLocale(QtCore.QLocale.German, QtCore.QLocale.Austria))
        apisFilmDialog.setModal(True)
        self.buttonBox = QtGui.QDialogButtonBox(apisFilmDialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))

        self.retranslateUi(apisFilmDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), apisFilmDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), apisFilmDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(apisFilmDialog)

    def retranslateUi(self, apisFilmDialog):
        apisFilmDialog.setWindowTitle(_translate("apisFilmDialog", "APIS Film", None))

