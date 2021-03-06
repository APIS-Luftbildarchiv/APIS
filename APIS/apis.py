# -*- coding: utf-8 -*-
"""
/***************************************************************************
 APIS
 A QGIS plugin for APIS - Luftbildarchiv
                              -------------------
        begin                : 2015-04-10
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Johannes Liem (digitalcartography.org) und Luftbildarchiv Uni Wien
        email                : johannes.liem@digitalcartography.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
from qgis.core import QgsPluginLayerRegistry, QgsLayerDefinition, QgsProject
from qgis.gui import QgsMessageBar

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialogs
# from apis_dialog import ApisDialog
from apis_settings_dialog import *
from apis_film_dialog import *
from apis_image_mapping_dialog import *
from apis_site_mapping_dialog import *
from apis_search_dialog import *
from apis_image_registry import *
from apis_layer_manager import *

from py_tiled_layer.tilelayer import TileLayer, TileLayerType

from apis_utils import *
from apis_db_manager import *

import os.path

class APIS:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'APIS_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&APIS')
        self.toolbar = self.iface.addToolBar(u'APIS')
        self.toolbar.setObjectName(u'APIS')

        self.dbm = None
        self.apisLayer = None
        self.areDialogsInit = False
        self.areDialogsActive = False
        self.imageMappingMode = False
        self.imageMappingDlg = None
        self.siteMappingDlg = None
        self.searchDlg = None
        self.openDialogButtons = None

        #check Settings
        #self.au = ApisUtils(self)

        #self.configStatus = self.au.checkConfigStatus()
        self.configStatus, self.settings = apisPluginSettings()
        #QMessageBox.warning(None, self.tr(u"Konfiguration"), u"{0}, {1}".format(self.configStatus, self.settings))

        self.imageRegistry = ApisImageRegistry(self.plugin_dir, self.iface)
        self.imageRegistry.loaded.connect(self.enableApis)

        if self.configStatus:
            self.imageRegistry.setupSettings()
            self.imageRegistry.setupRegistry()

        # Create the dialog (after translation) and keep reference
        self.settingsDlg = ApisSettingsDialog(self.iface, self.imageRegistry)




    def enableApis(self):
        #QMessageBox.warning(None, self.tr(u"ApisEnabled"), u"ImageRegistry is now loaded!")
        if(self.configStatus and self.imageRegistry.registryIsLoaded()):
            self.dbm = ApisDbManager(self.settings.value("APIS/database_file"))
            self.initDialogs()
            if self.openDialogButtons is not None:
                self.activateDialogs(True)

            # TODO: Prepare ApisLayerTree
            self.apisLayer = ApisLayerManager(self.plugin_dir, self.iface, self.dbm)

        else:
            QMessageBox.warning(None, self.tr(u"Konfiguration"), u"{0}, {1}".format(self.configStatus, self.settings))
            if self.openDialogButtons is not None:
                self.activateDialogs(False)


    def addApisAction(
        self,
        iconPath,
        text,
        callback,
        enabledFlag=True,
        addToMenu=True,
        addToToolbar=True,
        statusTip=None,
        whatsThis=None,
        parent=None,
        checkable=False):
        """
        Add a toolbar icon to the toolbar.

        :param iconPath: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type iconPath: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabledFlag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabledFlag: bool

        :param addToMenu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type addToMenu: bool

        :param addToToolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type addToToolbar: bool

        :param statusTip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type statusTip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whatsThis: Optional text to show in the status bar when the
            mouse pointer hovers over the action.
        :type whatsThis: str

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(iconPath)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabledFlag)

        if checkable:
            action.setCheckable(checkable)

        if statusTip is not None:
            action.setStatusTip(statusTip)

        if whatsThis is not None:
            action.setWhatsThis(whatsThis)

        if addToToolbar:
            self.toolbar.addAction(action)

        if addToMenu:
            self.iface.addPluginToDatabaseMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initDialogs(self):
        self.filmDlg = ApisFilmDialog(self.iface, self.dbm, self.imageRegistry, self.apisLayer)
        self.imageMappingDlg = None
        self.siteMappingDlg = None
        self.searchDlg = None
        #self.imageMappingDlg = ApisImageMappingDialog(self.iface, self.dbm)
        self.areDialogsInit = True
        self.areDialogsActive = True
        #self.imageMappingDlg.visibilityChanged.connect(self.mappingActionBtn.setChecked)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        # Settings Dialog
        if self.configStatus and self.imageRegistry.registryIsLoaded():
            iconPath = ':/plugins/APIS/icons/settings.png'
        else:
            iconPath = ':/plugins/APIS/icons/settings_alert.png'

        self.openSettingsButton = self.addApisAction(
            iconPath,
            text=self.tr(u'Einstellungen'),
            callback=self.openSettingsDialog,
            parent=self.iface.mainWindow()
        )

        #self.openSettingsButton.setIcon(QIcon(':/plugins/Apis/icons/settings.png'))

        self.openDialogButtons = []

        # (Re)Load Apis Layers
        iconPath = ':/plugins/APIS/icons/layer.png'
        self.openDialogButtons.append(self.addApisAction(
            iconPath,
            text=self.tr(u'APIS Layers'),
            callback=self.loadApisLayerTree,
            enabledFlag=self.configStatus and self.imageRegistry.registryIsLoaded(),
            parent=self.iface.mainWindow())
        )

        #Film Dialog
        iconPath = ':/plugins/APIS/icons/film.png'
        self.openDialogButtons.append(self.addApisAction(
            iconPath,
            text=self.tr(u'Film'),
            callback=self.openFilmDialog,
            enabledFlag=self.configStatus and self.imageRegistry.registryIsLoaded(),
            parent=self.iface.mainWindow())
        )

        #Kartieren Dialog
        iconPath = ':/plugins/APIS/icons/mapping_vertical.png'
        self.mappingActionBtn = self.addApisAction(
            iconPath,
            text=self.tr(u'Bilder kartieren'),
            callback=self.toggleImageMappingDialog,
            enabledFlag=self.configStatus and self.imageRegistry.registryIsLoaded(),
            parent=self.iface.mainWindow(),
            checkable=True)

        self.openDialogButtons.append(self.mappingActionBtn)

        #Fundortkartierung

        #if self.settings.value("APIS/disable_site_and_findspot", "0") != "1":
        iconPath = ':/plugins/APIS/icons/site.png'
        self.siteMappingActionBtn = self.addApisAction(
            iconPath,
            text=self.tr(u'Fundorte kartieren'),
            callback=self.toggleSiteMappingDialog,
            enabledFlag=self.configStatus and self.imageRegistry.registryIsLoaded() and self.settings.value("APIS/disable_site_and_findspot", "0") != "1",
            parent=self.iface.mainWindow(),
            checkable=True)

        self.openDialogButtons.append(self.siteMappingActionBtn)
        #else:
        #    self.siteMappingActionBtn = None

        iconPath = ':/plugins/APIS/icons/search.png'
        self.searchActionBtn = self.addApisAction(
            iconPath,
            text=self.tr(u'APIS Suche'),
            callback=self.toggleSearchDialg,
            enabledFlag=self.configStatus and self.imageRegistry.registryIsLoaded(),
            parent=self.iface.mainWindow(),
            checkable=True)

        self.openDialogButtons.append(self.searchActionBtn)

        # Register plugin layer type
        self.tileLayerType = TileLayerType()
        QgsPluginLayerRegistry.instance().addPluginLayerType(self.tileLayerType)

    def loadApisLayerTree(self):
        #res = QgsLayerDefinition.loadLayerDefinition(self.plugin_dir + "\\layer_tree\\apis_default_layer_definition.qlr", QgsProject.instance().layerTreeRoot())
        #QMessageBox.information(None, "LoadLayerDef", u"Loaded: {0}".format(res))
        if self.apisLayer and self.apisLayer.isLoaded:
            self.apisLayer.loadDefaultLayerTree()


    def openFilmDialog(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.filmDlg.show()
        # Run the dialog event loop
        result = self.filmDlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def toggleImageMappingDialog(self):
        if not self.imageMappingDlg:
            self.imageMappingDlg = ApisImageMappingDialog(self.iface, self.dbm, self.apisLayer)
            self.imageMappingDlg.visibilityChanged.connect(self.mappingActionBtn.setChecked)

        #if self.imageMappingDlg.isVisible():
        if self.mappingActionBtn.isChecked():
            self.imageMappingDlg.show()
            self.imageMappingMode = True
            #self.mappingActionBtn.setChecked(False)
        else:
            #TODO Check Mapping State !!!
            self.imageMappingDlg.hide()
            self.imageMappingMode = False
            #self.mappingActionBtn.setChecked(True)

    def toggleSiteMappingDialog(self):
        if not self.siteMappingDlg:
            self.siteMappingDlg = ApisSiteMappingDialog(self.iface, self.dbm, self.imageRegistry, self.apisLayer)
            self.siteMappingDlg.visibilityChanged.connect(self.siteMappingActionBtn.setChecked)

        if self.siteMappingActionBtn.isChecked():
            self.siteMappingDlg.show()
        else:
            self.siteMappingDlg.hide()

    def toggleSearchDialg(self):
        if not self.searchDlg:
            self.searchDlg = ApisSearchDialog(self.iface, self.dbm, self.imageRegistry, self.apisLayer)
            self.searchDlg.visibilityChanged.connect(self.searchActionBtn.setChecked)

        if self.searchActionBtn.isChecked():
            self.searchDlg.show()
        else:
            self.searchDlg.hide()


    # def toggleImageSearchTool(self):
    #     # Check if something is working at the moment ... if yes don't do anything!
    #     self.imageSearchTool = RectangleMapTool(self.iface, self.dbm)
    #     mb = self.iface.messageBar()
    #     if self.searchImageActionBtn.isChecked():
    #         self.iface.mapCanvas().setMapTool(self.imageSearchTool)
    #         mb.pushMessage("Luftbildsuche", "Klicken Sie auf die Karte oder ziehen Sie ein Rechteck auf um nach Luftbildern zu suchen!", level=QgsMessageBar.INFO)
    #     else:
    #         #if self.imageSearchTool.worker is None:
    #         self.iface.mapCanvas().unsetMapTool(self.imageSearchTool)
    #         mb.clearWidgets()

    def openSettingsDialog(self):
        """Run method that performs all the real work"""

        self.configStatus, self.settings = apisPluginSettings()
        if self.configStatus:
            if not self.imageRegistry.registryIsSetup():
                self.imageRegistry.setupSettings()
            if not self.imageRegistry.registryIsLoaded():
                self.imageRegistry.setupRegistry()
            self.settingsDlg.uiUpdateImageRegistryBtn.setEnabled(True)
        else:
            self.settingsDlg.uiUpdateImageRegistryBtn.setEnabled(False)
        # show the dialog
        self.settingsDlg.show()
        # Run the dialog event loop
        # See if OK was pressed
        if self.settingsDlg.exec_():
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            #self.configStatus,  = self.au.checkConfigStatus()
            self.configStatus, self.settings = apisPluginSettings()
            if self.configStatus:
                if not self.imageRegistry.registryIsSetup():
                    self.imageRegistry.setupSettings()
                if not self.imageRegistry.registryIsLoaded():
                    self.imageRegistry.setupRegistry()
            self.enableApis()
            # if self.configStatus and self.imageRegistry.registryIsLoaded():
            #     self.dbm = ApisDbManager(self.settings.value("APIS/database_file"))
            #     self.initDialogs()
            #     self.activateDialogs(True)
            # else:
            #if self.configStatus is False or self.imageRegistry.registryIsLoaded() is False:
            #    QMessageBox.warning(None, self.tr(u"Konfiguration"), u"{0}, {1}".format(self.configStatus, self.settings))
            #    self.activateDialogs(False)
                #self.openSettingsDialog()
        else:
            pass

    def activateDialogs(self, value):
        for action in self.openDialogButtons:
            if action is self.siteMappingActionBtn:
                if self.configStatus:
                    if self.settings.value("APIS/disable_site_and_findspot", "0") != "1":
                        action.setEnabled(value)
                    else:
                        action.setEnabled(False)
            else:
                action.setEnabled(value)
        self.areDialogsActive = value

        if self.configStatus and self.imageRegistry.registryIsLoaded():
            iconPath = ':/plugins/APIS/icons/settings.png'
        else:
            iconPath = ':/plugins/APIS/icons/settings_alert.png'

        self.openSettingsButton.setIcon(QIcon(iconPath))

        if self.mappingActionBtn.isChecked():
            self.mappingActionBtn.trigger()

        if self.siteMappingActionBtn and self.siteMappingActionBtn.isChecked():
            self.siteMappingActionBtn.trigger()

        if self.searchActionBtn.isChecked():
            self.searchActionBtn.trigger()




     # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('APIS', message)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        #
        # QMessageBox.information(None, "ApisUnload", "ApisUnload")
        self.activateDialogs(False)

        for action in self.actions:
            self.iface.removePluginDatabaseMenu(
                self.tr(u'&APIS'),
                action)
            self.iface.removeToolBarIcon(action)
        # unregister plugin layer type
        QgsPluginLayerRegistry.instance().removePluginLayerType(TileLayer.LAYER_TYPE)
        # remove the toolbar
        del self.toolbar

        # TODO deactivate all open connections ...