"""Tool to create a script tree that is easy to edit and save builds."""

import os
import webbrowser

from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance
from maya import OpenMayaUI
from maya import cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

import prometheus_widgets
from prometheus.utils import cache_utils


class PrometheusWindow(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    """The main window for the tool."""

    tool_name = 'Prometheus'
    tool_version = '0.0.2'
    
    def __init__(self, parent=None):
        """Initializer.

        :param parent: The parent widget of this window. (None)
        :type parent: :class:`QWidget`
        """
        # delete self first
        self.deleteInstances()
        
        # initialize the temp cache folders
        self.initCacheFolders()

        super(self.__class__, self).__init__(parent=parent)
        maya_main_window_parent = OpenMayaUI.MQtUtil.mainWindow() 
        wrapinstance(long(maya_main_window_parent), QtWidgets.QMainWindow)
        self.setObjectName(self.tool_name)

        # Setup window's properties
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("{} {}".format(self.tool_name, self.tool_version))
        self.resize(400, 600)

        # Create tab widgets
        self.tab_bar = QtWidgets.QTabWidget()
        self.setup_tab = QtWidgets.QWidget()
        self.build_tab = QtWidgets.QWidget()
        self.tab_bar.addTab(self.build_tab, 'Build')

        # Create main layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.main_layout.addWidget(self.tab_bar)
        self.setLayout(self.main_layout)

        # create the build tab
        self.build_layout = BuildTab()
        self.build_tab.setLayout(self.build_layout)
    
    def initCacheFolders(self):
        """Create the cache folders if they don't already exist."""
        # init the scripts cache folder
        # there should always just be the one folder 
        self.scripts_temp_folder = cache_utils.initScriptsCacheFolder()

        # next we want to flush any folders that are more than 5 days old
        # only folders living under the given directory will be deleted
        cache_utils.flushOutdatedCache(self.scripts_temp_folder)

        # init the date folder inside the scripts cache folder
        # this date folder will be assigned to the current session
        # that way we can cache multiple sessions to the same date without overwriting files
        cache_utils.initDateFolder(self.scripts_temp_folder, "PROMETHEUS_SCRIPTS_DATE_CACHE")

    def deleteInstances(self):
        """Delete any instances of PrometheusWindow."""
        if cmds.workspaceControl("{}{}".format(self.tool_name, 'WorkspaceControl'), exists=True, q=True):
            cmds.deleteUI("{}{}".format(self.tool_name, 'WorkspaceControl'), control=True)

    def run(self):
        """Show the window and make it dockable."""
        self.show(dockable=True)


class BuildTab(QtWidgets.QGridLayout):
    """The build tab to be used within the main window."""

    def __init__(self, parent=None):
        """Initializer.

        :param parent: The parent widget of this window. (None)
        :type parent: :class:`QWidget`
        """
        super(self.__class__, self).__init__(parent=parent)

        # create a menu bar
        self.menu_bar = QtWidgets.QMenuBar()
        self.file_menu = self.menu_bar.addMenu("File")
        self.save_config_action = self.file_menu.addAction("Save Config")
        self.load_config_action = self.file_menu.addAction("Load Config")
        self.file_menu.addSeparator()
        self.export_selected_action = self.file_menu.addAction("Export Selected To File")
        self.file_menu.addSeparator()
        self.change_location_action = self.file_menu.addAction("Change Script Location")
        self.file_menu.addSeparator()
        self.open_cached_scripts_action = self.file_menu.addAction("Open Cached Scripts")
        self.flush_cached_scripts_action = self.file_menu.addAction("Flush Cached Scripts")
        self.setMenuBar(self.menu_bar)

        # create the widgets
        self.build_tree = prometheus_widgets.Tree()
        self.module_list = prometheus_widgets.List()
        self.build_button = QtWidgets.QPushButton("Run Script Tree")

        # add the widgets
        self.addWidget(self.build_tree)
        self.addWidget(self.module_list)
        self.addWidget(self.build_button)

        # add signals
        self.build_button.clicked.connect(self.runBuildTree)
        self.save_config_action.triggered.connect(self.build_tree.saveConfig)
        self.load_config_action.triggered.connect(self.build_tree.loadConfig)
        self.export_selected_action.triggered.connect(self.build_tree.exportSelected)
        self.change_location_action.triggered.connect(self.module_list.openScriptPathWindow)
        self.open_cached_scripts_action.triggered.connect(self.openCachedScripts)
        self.flush_cached_scripts_action.triggered.connect(self.flushCachedScripts)

    @QtCore.Slot()
    def runBuildTree(self):
        """Execute all enabled treeItem code within the tree widget."""
        items = self.build_tree.getAllItems()

        # run the scripts
        for item in items:
            if item.getType() != "Group":
                
                if item.checkState(0) is QtCore.Qt.Checked:
                    # turn all the pixmaps red first
                    item.iconTint(item.red_pixmap)
                    # turn the pixmap yellow while the script is running
                    item.iconTint(item.yellow_pixmap)
                    # need this to update the icon so we know its currently running
                    QtWidgets.QApplication.processEvents()

                    # run the class and function
                    try:
                        exec(item.getCode(), locals())
                    except Exception:
                        item.iconTint(item.red_pixmap)
                        raise 

                    # turn the pixmap green when the script is done running
                    item.iconTint(item.green_pixmap)
                    QtWidgets.QApplication.processEvents()

    @QtCore.Slot()
    def flushCachedScripts(self):
        """Delete the current scripts cache folder being used by the maya session."""
        # prompt the user to make sure they want to do this
        message = "Are you sure you want to flush all the cached scripts? This is NOT undoable."
        message_box = QtWidgets.QMessageBox()
        message_box.setText(message)
        message_box.setStandardButtons(message_box.Yes | message_box.No)
        message_box.setDefaultButton(message_box.No)
        user_input = message_box.exec_()
        
        # delete all cached folders under the PROMETHEUS_SCRIPTS_CACHE folder
        # also delete the date env var created 
        if user_input == message_box.Yes:
            if "PROMETHEUS_SCRIPTS_DATE_CACHE" in os.environ:
                del os.environ["PROMETHEUS_SCRIPTS_DATE_CACHE"]
            if "PROMETHEUS_SCRIPTS_CACHE" in os.environ:
                if os.path.exists(os.environ["PROMETHEUS_SCRIPTS_CACHE"]):
                    cache_utils.flushCachedChildren(os.environ["PROMETHEUS_SCRIPTS_CACHE"])

    @QtCore.Slot()
    def openCachedScripts(self):
        """Open the folder location of the cached scripts. If it doesn't exist, go to top folder."""
        # try to open the date folder
        # if it doesn't exists, then try to open the main scripts cache folder
        if "PROMETHEUS_SCRIPTS_DATE_CACHE" in os.environ:
            if os.path.exists(os.environ["PROMETHEUS_SCRIPTS_DATE_CACHE"]):
                webbrowser.open(os.environ["PROMETHEUS_SCRIPTS_DATE_CACHE"])
        elif "PROMETHEUS_SCRIPTS_CACHE" in os.environ:
            if os.path.exists(os.environ["PROMETHEUS_SCRIPTS_CACHE"]):
                webbrowser.open(os.environ["PROMETHEUS_SCRIPTS_CACHE"])
