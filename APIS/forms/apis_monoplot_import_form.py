# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_monoplot_import_form.ui'
#
# Created: Wed Sep 23 11:27:05 2015
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
        apisMonoplotImportDialog.resize(314, 139)
        apisMonoplotImportDialog.setModal(True)
        self.uiCenterPointMLCombo = QgsMapLayerComboBox(apisMonoplotImportDialog)
        self.uiCenterPointMLCombo.setGeometry(QtCore.QRect(10, 30, 201, 27))
        self.uiCenterPointMLCombo.setObjectName(_fromUtf8("uiCenterPointMLCombo"))
        self.uiFootPrintMLCombo = QgsMapLayerComboBox(apisMonoplotImportDialog)
        self.uiFootPrintMLCombo.setGeometry(QtCore.QRect(10, 90, 201, 27))
        self.uiFootPrintMLCombo.setObjectName(_fromUtf8("uiFootPrintMLCombo"))
        self.uiImportBtn = QtGui.QPushButton(apisMonoplotImportDialog)
        self.uiImportBtn.setGeometry(QtCore.QRect(230, 20, 75, 23))
        self.uiImportBtn.setAutoDefault(False)
        self.uiImportBtn.setObjectName(_fromUtf8("uiImportBtn"))
        self.label = QtGui.QLabel(apisMonoplotImportDialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 201, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(apisMonoplotImportDialog)
        self.label_2.setGeometry(QtCore.QRect(10, 70, 201, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))

        self.retranslateUi(apisMonoplotImportDialog)
        QtCore.QMetaObject.connectSlotsByName(apisMonoplotImportDialog)

    def retranslateUi(self, apisMonoplotImportDialog):
        apisMonoplotImportDialog.setWindowTitle(_translate("apisMonoplotImportDialog", "Dialog", None))
        self.uiImportBtn.setText(_translate("apisMonoplotImportDialog", "Importieren", None))
        self.label.setText(_translate("apisMonoplotImportDialog", "Layer für Bildmittelpunkte:", None))
        self.label_2.setText(_translate("apisMonoplotImportDialog", "Layer für Footprints:", None))

from qgis.gui import QgsMapLayerComboBox
