# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/apis_representative_image_form.ui'
#
# Created: Sat May 21 22:06:28 2016
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

class Ui_apisRepresentativeImageDialog(object):
    def setupUi(self, apisRepresentativeImageDialog):
        apisRepresentativeImageDialog.setObjectName(_fromUtf8("apisRepresentativeImageDialog"))
        apisRepresentativeImageDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        apisRepresentativeImageDialog.resize(500, 300)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/apis.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        apisRepresentativeImageDialog.setWindowIcon(icon)
        apisRepresentativeImageDialog.setLocale(QtCore.QLocale(QtCore.QLocale.German, QtCore.QLocale.Germany))
        apisRepresentativeImageDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(apisRepresentativeImageDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_3 = QtGui.QLabel(apisRepresentativeImageDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout.addWidget(self.label_3)
        self.uiImagePathLbl = QtGui.QLabel(apisRepresentativeImageDialog)
        self.uiImagePathLbl.setObjectName(_fromUtf8("uiImagePathLbl"))
        self.horizontalLayout.addWidget(self.uiImagePathLbl)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiSelectImageFromSystem = QtGui.QPushButton(apisRepresentativeImageDialog)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/APIS/icons/image.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiSelectImageFromSystem.setIcon(icon1)
        self.uiSelectImageFromSystem.setIconSize(QtCore.QSize(24, 24))
        self.uiSelectImageFromSystem.setAutoDefault(False)
        self.uiSelectImageFromSystem.setObjectName(_fromUtf8("uiSelectImageFromSystem"))
        self.gridLayout.addWidget(self.uiSelectImageFromSystem, 0, 0, 1, 1)
        self.line = QtGui.QFrame(apisRepresentativeImageDialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout.addWidget(self.line, 1, 0, 1, 1)
        self.label = QtGui.QLabel(apisRepresentativeImageDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.uiFilmNumberCombo = QtGui.QComboBox(apisRepresentativeImageDialog)
        self.uiFilmNumberCombo.setEditable(True)
        self.uiFilmNumberCombo.setObjectName(_fromUtf8("uiFilmNumberCombo"))
        self.gridLayout.addWidget(self.uiFilmNumberCombo, 3, 0, 1, 1)
        self.label_2 = QtGui.QLabel(apisRepresentativeImageDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 4, 0, 1, 1)
        self.uiAvailableImagesCombo = QtGui.QComboBox(apisRepresentativeImageDialog)
        self.uiAvailableImagesCombo.setEditable(True)
        self.uiAvailableImagesCombo.setObjectName(_fromUtf8("uiAvailableImagesCombo"))
        self.gridLayout.addWidget(self.uiAvailableImagesCombo, 5, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(apisRepresentativeImageDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 7, 0, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 6, 0, 1, 1)
        self.uiRepresentativeImageView = QtGui.QGraphicsView(apisRepresentativeImageDialog)
        self.uiRepresentativeImageView.setObjectName(_fromUtf8("uiRepresentativeImageView"))
        self.gridLayout.addWidget(self.uiRepresentativeImageView, 0, 1, 7, 1)
        self.verticalLayout.addLayout(self.gridLayout)

        self.retranslateUi(apisRepresentativeImageDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), apisRepresentativeImageDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), apisRepresentativeImageDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(apisRepresentativeImageDialog)
        apisRepresentativeImageDialog.setTabOrder(self.uiSelectImageFromSystem, self.uiFilmNumberCombo)
        apisRepresentativeImageDialog.setTabOrder(self.uiFilmNumberCombo, self.uiAvailableImagesCombo)
        apisRepresentativeImageDialog.setTabOrder(self.uiAvailableImagesCombo, self.buttonBox)
        apisRepresentativeImageDialog.setTabOrder(self.buttonBox, self.uiRepresentativeImageView)

    def retranslateUi(self, apisRepresentativeImageDialog):
        apisRepresentativeImageDialog.setWindowTitle(_translate("apisRepresentativeImageDialog", "APIS Repräsentatives Luftbild", None))
        self.label_3.setText(_translate("apisRepresentativeImageDialog", "Dateipfad:", None))
        self.uiImagePathLbl.setText(_translate("apisRepresentativeImageDialog", "--", None))
        self.uiSelectImageFromSystem.setText(_translate("apisRepresentativeImageDialog", "Luftbild auswählen ...", None))
        self.label.setText(_translate("apisRepresentativeImageDialog", "Film:", None))
        self.label_2.setText(_translate("apisRepresentativeImageDialog", "Verfügbare Bilder:", None))

import resource_rc
