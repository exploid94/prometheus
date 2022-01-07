"""Custom window to view/edit folder paths for script locations."""

import sys
import webbrowser

from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance
from maya import OpenMayaUI
from maya import cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


class ScriptPathsWindow(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    """Create a simple window to display script paths."""

    tool_name = 'Prometheus Script Paths'
    tool_version = '0.0.1'

    list_changed = QtCore.Signal(object)

    def __init__(self, parent=None, paths=[]):
        """Initializer.

        :param parent: The parent widget of this window. (None)
        :type parent: :class:`QWidget`

        :param script_paths: A list of paths to be used. 
        :type script_paths: list
        """
        # delete self first
        self.deleteInstances()

        super(self.__class__, self).__init__(parent=parent)
        maya_main_window_parent = OpenMayaUI.MQtUtil.mainWindow() 
        wrapinstance(long(maya_main_window_parent), QtWidgets.QMainWindow)
        self.setObjectName(self.tool_name)

        # Setup window's properties
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("{} {}".format(self.tool_name, self.tool_version))
        self.resize(400, 400)

        # set the layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        # add the ListWidget
        self.default_paths = paths
        self.path_list = []
        self.path_list_widget = QtWidgets.QListWidget()
        self.add_button = QtWidgets.QPushButton("Add Path")
        self.remove_button = QtWidgets.QPushButton("Remove Path")
        self.reset_button = QtWidgets.QPushButton("Reset Paths")
        self.open_button = QtWidgets.QPushButton("Open Selected Path")

        self.path_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        
        # populate the list widget
        if paths:
            for path in paths:
                new_item = QtWidgets.QListWidgetItem()
                new_item.setText(path)
                self.path_list_widget.addItem(new_item)
                self.path_list.append(path)
        
        # add the widgets to the layout
        self.main_layout.addWidget(self.path_list_widget)
        self.main_layout.addWidget(self.add_button)
        self.main_layout.addWidget(self.remove_button)
        self.main_layout.addWidget(self.reset_button)
        self.main_layout.addWidget(self.open_button)

        # connect the signals to funcs
        self.add_button.clicked.connect(self.addPath)
        self.remove_button.clicked.connect(self.removePath)
        self.reset_button.clicked.connect(self.resetPaths)
        self.open_button.clicked.connect(self.openPath)
    
    @QtCore.Slot()
    def addPath(self):
        """Add a path to the script paths list."""
        path = cmds.fileDialog2(fm=2)
        if path:
            path = path[0]
            if path not in self.path_list:
                new_item = QtWidgets.QListWidgetItem()
                new_item.setText(path)
                self.path_list_widget.addItem(new_item)
                self.path_list.append(path)

        # emit change signal
        self.list_changed.emit(self.path_list)

    @QtCore.Slot()
    def removePath(self):
        """Remove the selected path from the script paths list."""
        for selected in self.path_list_widget.selectedItems():
            idx = self.path_list_widget.indexFromItem(selected).row()
            self.path_list_widget.takeItem(idx)
            self.path_list.remove(selected.text())
        
        # emit change signal
        self.list_changed.emit(self.path_list)
    
    @QtCore.Slot()
    def resetPaths(self):
        """Reset the paths list to the default_paths list."""
        self.path_list_widget.clear()
        if self.default_paths:
            for path in self.default_paths:
                new_item = QtWidgets.QListWidgetItem()
                new_item.setText(path)
                self.path_list_widget.addItem(new_item)
                self.path_list.append(path)
        
        # emit change signal
        self.list_changed.emit(self.path_list)
    
    @QtCore.Slot()
    def openPath(self):
        """Open the selected path in a file explorer."""
        selected = self.path_list_widget.selectedItems()
        if selected:
            webbrowser.open(selected[0].text())

    @QtCore.Slot()
    def openScriptLocation(self):
        """Open the script location."""
        for selected in self.path_list_widget.selected_items():
            if os.path.exists(selected.text()):
                webbrowser.open(selected.text())

    def deleteInstances(self):
        """Delete any instances of ScriptPathsWindow."""
        if cmds.workspaceControl("{}{}".format(self.tool_name, 'WorkspaceControl'), exists=True, q=True):
            cmds.deleteUI("{}{}".format(self.tool_name, 'WorkspaceControl'), control=True)
 

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Prometheus Script Paths")

    window = InfoWindow()
    app.exec_()
