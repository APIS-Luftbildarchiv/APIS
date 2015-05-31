# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_new_film_form.ui'
#
# Created: Sun May 31 20:44:16 2015
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
        apisNewFilmDialog.resize(320, 90)
        apisNewFilmDialog.setMinimumSize(QtCore.QSize(320, 90))
        apisNewFilmDialog.setMaximumSize(QtCore.QSize(320, 90))
        apisNewFilmDialog.setLocale(QtCore.QLocale(QtCore.QLocale.German, QtCore.QLocale.Austria))
        apisNewFilmDialog.setModal(True)
        self.uiButtonBox = QtGui.QDialogButtonBox(apisNewFilmDialog)
        self.uiButtonBox.setGeometry(QtCore.QRect(240, 10, 75, 52))
        self.uiButtonBox.setOrientation(QtCore.Qt.Vertical)
        self.uiButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName(_fromUtf8("uiButtonBox"))
        self.gridLayoutWidget = QtGui.QWidget(apisNewFilmDialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 221, 71))
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
        self.uiUseLastEntryChk.setChecked(False)
        self.uiUseLastEntryChk.setObjectName(_fromUtf8("uiUseLastEntryChk"))
        self.gridLayout.addWidget(self.uiUseLastEntryChk, 1, 0, 1, 2)
        self.uiProducerCombo = QtGui.QComboBox(self.gridLayoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiProducerCombo.sizePolicy().hasHeightForWidth())
        self.uiProducerCombo.setSizePolicy(sizePolicy)
        self.uiProducerCombo.setStyleSheet(_fromUtf8(""))
        self.uiProducerCombo.setEditable(True)
        self.uiProducerCombo.setModelColumn(0)
        self.uiProducerCombo.setObjectName(_fromUtf8("uiProducerCombo"))
        self.gridLayout.addWidget(self.uiProducerCombo, 2, 1, 1, 1)
        self.uiProducerLbl = QtGui.QLabel(self.gridLayoutWidget)
        self.uiProducerLbl.setObjectName(_fromUtf8("uiProducerLbl"))
        self.gridLayout.addWidget(self.uiProducerLbl, 2, 0, 1, 1)

        self.retranslateUi(apisNewFilmDialog)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), apisNewFilmDialog.accept)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), apisNewFilmDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(apisNewFilmDialog)

    def retranslateUi(self, apisNewFilmDialog):
        apisNewFilmDialog.setWindowTitle(_translate("apisNewFilmDialog", "Neuer Film", None))
        self.uiFlightDateLbl.setText(_translate("apisNewFilmDialog", "Flugdatum:", None))
        self.uiFlightDate.setDisplayFormat(_translate("apisNewFilmDialog", "dd.MM.yyyy", None))
        self.uiUseLastEntryChk.setText(_translate("apisNewFilmDialog", "Daten von letztem Eintrag übernehmen", None))
        self.uiProducerLbl.setText(_translate("apisNewFilmDialog", "Hersteller:", None))

