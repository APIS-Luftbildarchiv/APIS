# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_view_flight_path_form.ui'
#
# Created: Fri Dec 18 09:53:41 2015
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

class Ui_apisViewFlightPathDialog(object):
    def setupUi(self, apisViewFlightPathDialog):
        apisViewFlightPathDialog.setObjectName(_fromUtf8("apisViewFlightPathDialog"))
        apisViewFlightPathDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        apisViewFlightPathDialog.resize(635, 333)
        apisViewFlightPathDialog.setModal(True)
        self.buttonBox = QtGui.QDialogButtonBox(apisViewFlightPathDialog)
        self.buttonBox.setGeometry(QtCore.QRect(460, 300, 156, 23))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.uiFlightPathAvailabilityTable = QtGui.QTableWidget(apisViewFlightPathDialog)
        self.uiFlightPathAvailabilityTable.setGeometry(QtCore.QRect(10, 70, 611, 221))
        self.uiFlightPathAvailabilityTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.uiFlightPathAvailabilityTable.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.uiFlightPathAvailabilityTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.uiFlightPathAvailabilityTable.setObjectName(_fromUtf8("uiFlightPathAvailabilityTable"))
        self.uiFlightPathAvailabilityTable.setColumnCount(5)
        self.uiFlightPathAvailabilityTable.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.uiFlightPathAvailabilityTable.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.uiFlightPathAvailabilityTable.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.uiFlightPathAvailabilityTable.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.uiFlightPathAvailabilityTable.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.uiFlightPathAvailabilityTable.setHorizontalHeaderItem(4, item)
        self.horizontalLayoutWidget = QtGui.QWidget(apisViewFlightPathDialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(11, 10, 611, 31))
        self.horizontalLayoutWidget.setObjectName(_fromUtf8("horizontalLayoutWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.uiGpsFlightLbl = QtGui.QLabel(self.horizontalLayoutWidget)
        self.uiGpsFlightLbl.setObjectName(_fromUtf8("uiGpsFlightLbl"))
        self.horizontalLayout.addWidget(self.uiGpsFlightLbl)
        self.uiGpsFlightPointChk = QtGui.QCheckBox(self.horizontalLayoutWidget)
        self.uiGpsFlightPointChk.setObjectName(_fromUtf8("uiGpsFlightPointChk"))
        self.horizontalLayout.addWidget(self.uiGpsFlightPointChk)
        self.uiGpsFlightLineChk = QtGui.QCheckBox(self.horizontalLayoutWidget)
        self.uiGpsFlightLineChk.setObjectName(_fromUtf8("uiGpsFlightLineChk"))
        self.horizontalLayout.addWidget(self.uiGpsFlightLineChk)
        self.line_3 = QtGui.QFrame(self.horizontalLayoutWidget)
        self.line_3.setFrameShape(QtGui.QFrame.VLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName(_fromUtf8("line_3"))
        self.horizontalLayout.addWidget(self.line_3)
        self.uiGpsCameraLbl = QtGui.QLabel(self.horizontalLayoutWidget)
        self.uiGpsCameraLbl.setObjectName(_fromUtf8("uiGpsCameraLbl"))
        self.horizontalLayout.addWidget(self.uiGpsCameraLbl)
        self.uiGpsCameraPointChk = QtGui.QCheckBox(self.horizontalLayoutWidget)
        self.uiGpsCameraPointChk.setObjectName(_fromUtf8("uiGpsCameraPointChk"))
        self.horizontalLayout.addWidget(self.uiGpsCameraPointChk)
        self.uiGpsCameraLineChk = QtGui.QCheckBox(self.horizontalLayoutWidget)
        self.uiGpsCameraLineChk.setObjectName(_fromUtf8("uiGpsCameraLineChk"))
        self.horizontalLayout.addWidget(self.uiGpsCameraLineChk)
        self.line_4 = QtGui.QFrame(self.horizontalLayoutWidget)
        self.line_4.setFrameShape(QtGui.QFrame.VLine)
        self.line_4.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_4.setObjectName(_fromUtf8("line_4"))
        self.horizontalLayout.addWidget(self.line_4)
        self.uiMappingLbl = QtGui.QLabel(self.horizontalLayoutWidget)
        self.uiMappingLbl.setObjectName(_fromUtf8("uiMappingLbl"))
        self.horizontalLayout.addWidget(self.uiMappingLbl)
        self.uiMappingPointChk = QtGui.QCheckBox(self.horizontalLayoutWidget)
        self.uiMappingPointChk.setObjectName(_fromUtf8("uiMappingPointChk"))
        self.horizontalLayout.addWidget(self.uiMappingPointChk)
        self.uiMappingLineChk = QtGui.QCheckBox(self.horizontalLayoutWidget)
        self.uiMappingLineChk.setObjectName(_fromUtf8("uiMappingLineChk"))
        self.horizontalLayout.addWidget(self.uiMappingLineChk)
        self.label = QtGui.QLabel(apisViewFlightPathDialog)
        self.label.setGeometry(QtCore.QRect(10, 50, 71, 16))
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(apisViewFlightPathDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), apisViewFlightPathDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), apisViewFlightPathDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(apisViewFlightPathDialog)

    def retranslateUi(self, apisViewFlightPathDialog):
        apisViewFlightPathDialog.setWindowTitle(_translate("apisViewFlightPathDialog", "APIS Flugwege anzeigen", None))
        item = self.uiFlightPathAvailabilityTable.horizontalHeaderItem(0)
        item.setText(_translate("apisViewFlightPathDialog", "Film", None))
        item = self.uiFlightPathAvailabilityTable.horizontalHeaderItem(1)
        item.setText(_translate("apisViewFlightPathDialog", "GPS Film Punkte", None))
        item = self.uiFlightPathAvailabilityTable.horizontalHeaderItem(2)
        item.setText(_translate("apisViewFlightPathDialog", "GPS Film Linien", None))
        item = self.uiFlightPathAvailabilityTable.horizontalHeaderItem(3)
        item.setText(_translate("apisViewFlightPathDialog", "GPS Kamera", None))
        item = self.uiFlightPathAvailabilityTable.horizontalHeaderItem(4)
        item.setText(_translate("apisViewFlightPathDialog", "Kartierung", None))
        self.uiGpsFlightLbl.setText(_translate("apisViewFlightPathDialog", "GPS Flug:", None))
        self.uiGpsFlightPointChk.setText(_translate("apisViewFlightPathDialog", "Punkte", None))
        self.uiGpsFlightLineChk.setText(_translate("apisViewFlightPathDialog", "Linie(n)", None))
        self.uiGpsCameraLbl.setText(_translate("apisViewFlightPathDialog", "GPS Kamera:", None))
        self.uiGpsCameraPointChk.setText(_translate("apisViewFlightPathDialog", "Punkte", None))
        self.uiGpsCameraLineChk.setText(_translate("apisViewFlightPathDialog", "Linie(n)", None))
        self.uiMappingLbl.setText(_translate("apisViewFlightPathDialog", "Kartierung:", None))
        self.uiMappingPointChk.setText(_translate("apisViewFlightPathDialog", "Punkte", None))
        self.uiMappingLineChk.setText(_translate("apisViewFlightPathDialog", "Linie(n)", None))
        self.label.setText(_translate("apisViewFlightPathDialog", "Verfügbarkeit:", None))

