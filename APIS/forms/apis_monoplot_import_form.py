# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_monoplot_import_form.ui'
#
# Created: Wed Apr 27 09:52:16 2016
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
        apisMonoplotImportDialog.resize(338, 159)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/apis.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        apisMonoplotImportDialog.setWindowIcon(icon)
        apisMonoplotImportDialog.setModal(True)
        self.formLayout = QtGui.QFormLayout(apisMonoplotImportDialog)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(apisMonoplotImportDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.SpanningRole, self.label)
        self.label_2 = QtGui.QLabel(apisMonoplotImportDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.SpanningRole, self.label_2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.formLayout.setItem(4, QtGui.QFormLayout.SpanningRole, spacerItem)
        self.uiImportBtn = QtGui.QPushButton(apisMonoplotImportDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiImportBtn.sizePolicy().hasHeightForWidth())
        self.uiImportBtn.setSizePolicy(sizePolicy)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/monoplot.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiImportBtn.setIcon(icon1)
        self.uiImportBtn.setIconSize(QtCore.QSize(16, 16))
        self.uiImportBtn.setAutoDefault(False)
        self.uiImportBtn.setObjectName(_fromUtf8("uiImportBtn"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.LabelRole, self.uiImportBtn)
        self.progressBar = QtGui.QProgressBar(apisMonoplotImportDialog)
        self.progressBar.setMaximum(0)
        self.progressBar.setProperty("value", -1)
        self.progressBar.setTextVisible(False)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.progressBar)
        self.uiCenterPointMLCombo = QgsMapLayerComboBox(apisMonoplotImportDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiCenterPointMLCombo.sizePolicy().hasHeightForWidth())
        self.uiCenterPointMLCombo.setSizePolicy(sizePolicy)
        self.uiCenterPointMLCombo.setObjectName(_fromUtf8("uiCenterPointMLCombo"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.SpanningRole, self.uiCenterPointMLCombo)
        self.uiFootPrintMLCombo = QgsMapLayerComboBox(apisMonoplotImportDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiFootPrintMLCombo.sizePolicy().hasHeightForWidth())
        self.uiFootPrintMLCombo.setSizePolicy(sizePolicy)
        self.uiFootPrintMLCombo.setObjectName(_fromUtf8("uiFootPrintMLCombo"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.SpanningRole, self.uiFootPrintMLCombo)

        self.retranslateUi(apisMonoplotImportDialog)
        QtCore.QMetaObject.connectSlotsByName(apisMonoplotImportDialog)

    def retranslateUi(self, apisMonoplotImportDialog):
        apisMonoplotImportDialog.setWindowTitle(_translate("apisMonoplotImportDialog", "APIS MONOPLOT Import", None))
        self.label.setText(_translate("apisMonoplotImportDialog", "Layer für Bildmittelpunkte:", None))
        self.label_2.setText(_translate("apisMonoplotImportDialog", "Layer für Footprints:", None))
        self.uiImportBtn.setText(_translate("apisMonoplotImportDialog", "Importieren", None))

from qgis.gui import QgsMapLayerComboBox
import resource_rc
