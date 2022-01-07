"""Custom info window to be used for viewing info of Prometheus TreeItem."""

import sys

from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance

from maya import OpenMayaUI
from maya import cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


class InfoWindow(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    """Create a simple window to display tree item information."""

    tool_name = 'Prometheus Item Info'
    tool_version = '0.0.1'

    def __init__(self, parent=None):
        """Initializer.

        :param parent: The parent widget of this window. (None)
        :type parent: :class:`QWidget`
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
        self.resize(50, 50)

        # set the layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        # add the TreeItem Info page
        self.name = QtWidgets.QLabel("Item Name: ")
        self.type = QtWidgets.QLabel("Item Type: ")
        self.file_path = QtWidgets.QLabel("Script File Path: ")
        self.temp_file_path = QtWidgets.QLabel("Temp File Path: ")

        # add the widgets to the layout
        self.main_layout.addWidget(self.name)
        self.main_layout.addWidget(self.type)
        self.main_layout.addWidget(self.file_path)
        self.main_layout.addWidget(self.temp_file_path)
    
    def updateLabels(self, name, type, file_path, temp_file_path):
        """Update the text within the window to match item data.

        :param name: The name of the item.
        :type name: str

        :param type: The item type.
        :type type: str

        :param file_path: The file path that is referenced from the item data.
        :type file_path: str

        :param temp_file_path: The file path of the temp cached file.
        :type temp_file_path: str
        """
        self.name.setText("Item Name: " + name)
        self.type.setText("Item Type: " + type)
        self.file_path.setText("Script File Path: " + str(file_path))
        self.temp_file_path.setText("Temp File Path: " + str(temp_file_path))

    def deleteInstances(self):
        """Delete any instances of InfoWindow."""
        if cmds.workspaceControl("{}{}".format(self.tool_name, 'WorkspaceControl'), exists=True, q=True):
            cmds.deleteUI("{}{}".format(self.tool_name, 'WorkspaceControl'), control=True)

    def run(self, item=None):
        """Show the window with the given item data.

        :param item: The item from the tree widget. (None)
        :type item: :class:`TreeItem`
        """
        self.show()
        if item:
            self.updateLabels(item.getName(), item.getType(), item.getFilePath(), item.getCacheFile())
 

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Prometheus Item Info")

    window = InfoWindow()
    app.exec_()
