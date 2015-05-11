# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_new_film_form.ui'
#
# Created: Sun May 10 23:09:32 2015
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

class Ui_apisNewFilmDialog(object):
    def setupUi(self, apisNewFilmDialog):
        apisNewFilmDialog.setObjectName(_fromUtf8("apisNewFilmDialog"))
        apisNewFilmDialog.resize(320, 70)
        apisNewFilmDialog.setMinimumSize(QtCore.QSize(320, 70))
        apisNewFilmDialog.setMaximumSize(QtCore.QSize(320, 70))
        apisNewFilmDialog.setModal(True)
        self.uiButtonBox = QtGui.QDialogButtonBox(apisNewFilmDialog)
        self.uiButtonBox.setGeometry(QtCore.QRect(240, 10, 75, 52))
        self.uiButtonBox.setOrientation(QtCore.Qt.Vertical)
        self.uiButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName(_fromUtf8("uiButtonBox"))
        self.gridLayoutWidget = QtGui.QWidget(apisNewFilmDialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 221, 51))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiFlightDateLbl = QtGui.QLabel(self.gridLayoutWidget)
        self.uiFlightDateLbl.setObjectName(_fromUtf8("uiFlightDateLbl"))
        self.gridLayout.addWidget(self.uiFlightDateLbl, 0, 0, 1, 1)
        self.uiFlightDate = QtGui.QDateEdit(self.gridLayoutWidget)
        self.uiFlightDate.setCalendarPopup(True)
        self.uiFlightDate.setObjectName(_fromUtf8("uiFlightDate"))
        self.gridLayout.addWidget(self.uiFlightDate, 0, 1, 1, 1)
        self.uiUseLastEntryChk = QtGui.QCheckBox(self.gridLayoutWidget)
        self.uiUseLastEntryChk.setChecked(True)
        self.uiUseLastEntryChk.setObjectName(_fromUtf8("uiUseLastEntryChk"))
        self.gridLayout.addWidget(self.uiUseLastEntryChk, 1, 0, 1, 2)

        self.retranslateUi(apisNewFilmDialog)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), apisNewFilmDialog.accept)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), apisNewFilmDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(apisNewFilmDialog)

    def retranslateUi(self, apisNewFilmDialog):
        apisNewFilmDialog.setWindowTitle(_translate("apisNewFilmDialog", "Neuer Film", None))
        self.uiFlightDateLbl.setText(_translate("apisNewFilmDialog", "Flugdatum:", None))
        self.uiFlightDate.setDisplayFormat(_translate("apisNewFilmDialog", "dd.MM.yyyy", None))
        self.uiUseLastEntryChk.setText(_translate("apisNewFilmDialog", "Daten von letztem Eintrag übernehmen", None))

