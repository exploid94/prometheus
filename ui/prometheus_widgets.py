"""Custom Qt widgets to be used within the prometheus main window."""

import os
from functools import partial
import webbrowser
import getpass

from PySide2 import QtGui, QtCore, QtWidgets
from maya import cmds

from prometheus.utils import json_utils
from prometheus.utils import cache_utils
from prometheus.utils import path_utils
import code_editor
import info_window
import constants
import script_path_window


class TreeItem(QtWidgets.QTreeWidgetItem):
    """Custom tree widget item that contains all node data."""

    def __init__(self, parent=None, item=None):
        """Initializer.

        :param parent: The parent widget of this window. (None)
        :type parent: :class:`QWidget`

        :param item: The item to be converted. (None)
        :type item: :class:`QTreeWidgetItem`
        """
        super(self.__class__, self).__init__(parent=parent, item=item)

        # settings for the tree widget items
        self.red = QtGui.QColor(255, 0, 0, 255)
        self.green = QtGui.QColor(0, 255, 0, 255)
        self.yellow = QtGui.QColor(255, 255, 0, 255)

        self.red_pixmap = QtGui.QPixmap(100, 100)
        self.red_pixmap.fill(self.red)
        self.green_pixmap = QtGui.QPixmap(100, 100)
        self.green_pixmap.fill(self.green)
        self.yellow_pixmap = QtGui.QPixmap(100, 100)
        self.yellow_pixmap.fill(self.yellow)

        base_folder = os.path.dirname(os.path.dirname(__file__))
        ui_folder = os.path.join(base_folder, "ui")
        self.icon_folder = os.path.join(ui_folder, "icons").replace("\\", "/")

        self.null_pixmap = QtGui.QPixmap(os.path.join(self.icon_folder, "null.png"))
        self.group_pixmap = QtGui.QPixmap(os.path.join(self.icon_folder, "group.png"))
        self.script_pixmap = QtGui.QPixmap(os.path.join(self.icon_folder, "script.png"))

        self.setCheckState(0, QtCore.Qt.Checked)
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)

        self.emitDataChanged()

        self.edited = False
        self.enabled = True
        self.default_icon = None

        # this is used to convert treewidgetitem to treeitem
        if item:
            self.setName(item.data(constants.NAME_DATA_VALUE, 0))
            self.setType(item.data(constants.TYPE_DATA_VALUE, 0))
            self.setFilePath(item.data(constants.FILE_PATH_DATA_VALUE, 0))
            self.setCode(item.data(constants.CODE_DATA_VALUE, 0))
            self.setGroupColor(item.data(constants.GROUP_COLOR_DATA_VALUE, 0))
            self.setPixmap(item.icon(0))

    def isEdited(self):
        """Return whether the item is edited or not.

        :return: Whether the item is edited or not.
        :rtype: bool
        """
        return self.edited

    def isEnabled(self):
        """Return whether the item is enabled or not.

        :return: Whether the item is enabled or not.
        :rtype: bool
        """
        if self.checkState(0) is QtCore.Qt.CheckState.Checked:
            return True
        else:
            return False

    def getName(self):
        """Return the item name.

        :return: The item name.
        :rtype: str
        """
        return self.data(constants.NAME_DATA_VALUE, 0)
    
    def getType(self):
        """Return the item type.

        :return: The item type.
        :rtype: str
        """
        return self.data(constants.TYPE_DATA_VALUE, 0)
    
    def getFilePath(self):
        """Return the item file path.

        :return: The item file path.
        :rtype: str
        """
        return self.data(constants.FILE_PATH_DATA_VALUE, 0)
    
    def getCode(self):
        """Return the item code.

        :return: The item code.
        :rtype: str
        """
        # convert tabs to spaces
        try:
            return self.data(constants.CODE_DATA_VALUE, 0).replace("\t", "    ")
        except Exception:
            return self.data(constants.CODE_DATA_VALUE, 0)

    def getIcon(self):
        """Return the item icon.

        :return: The item icon.
        :rtype: :class:`QIcon`
        """
        return self.icon(0)

    def getGroupColor(self):
        """Return the item group color.

        :return: The item group color.
        :rtype: :class:`QColor`
        """
        return self.data(constants.GROUP_COLOR_DATA_VALUE, 0)

    def getPixmap(self):
        """Return the item pixmap.

        :return: The item pixmap.
        :rtype: :class:`QPixmap`
        """
        icon = self.getIcon()
        return icon.pixmap(icon.availableSizes()[0])

    def getCacheFile(self):
        """Return the linked cache file, if there is one.

        :return: The cached file path.
        :rtype: str
        """
        return self.data(constants.CACHE_FILE_DATA_VALUE, 0)

    def setIsEdited(self, edited):
        """Set whether the item is edited or not.

        :param edited: bool
        :type edited: bool
        """
        self.edited = edited

        if self.edited:
            if self.getType() != "Null":
                self.setName(self.getName() + " (edited)")
        else:
            if self.getType() != "Null":
                self.setName(self.getName().replace(" (edited)", ""))

    def setIsEnabled(self, enabled):
        """Set whether the item is enabled or not.

        :param enabled: bool
        :type enabled: bool
        """
        if enabled:
            self.enabled = True
            self.setCheckState(0, QtCore.Qt.Checked)
        else:
            self.enabled = False
            self.setCheckState(0, QtCore.Qt.Unchecked)
        
    def setName(self, data):
        """Set the name of the item.

        :param data: The new name of the item.
        :type data: str
        """
        self.setData(constants.NAME_DATA_VALUE, 0, data)
    
    def setType(self, data):
        """Set the item type.

        :param data: The new item type.
        :type data: str
        """
        self.setData(constants.TYPE_DATA_VALUE, 0, data)
    
    def setFilePath(self, data):
        """Set the file path of the item.

        :param data: The new file path of the item.
        :type data: str
        """
        self.setData(constants.FILE_PATH_DATA_VALUE, 0, data)
    
    def setCode(self, data):
        """Set the code of the item.

        :param data: The new code of the item.
        :type data: str
        """
        self.setData(constants.CODE_DATA_VALUE, 0, data)

    def setPixmap(self, icon):
        """Set the pixmap of the item.

        :param icon: The new pixmap of the item.
        :type icon: :class:`QPixmap`
        """
        if not self.default_icon:
            self.default_icon = icon
        self.setIcon(0, icon)

    def setGroupColor(self, color):
        """Set the group color of the item.

        :param color: The new color of the item.
        :type color: :class:`QColor`
        """
        self.setData(constants.GROUP_COLOR_DATA_VALUE, 0, color)

    def setCacheFile(self, filepath):
        """Set the cache file to link this item to.

        :param data: The file path of the cache file.
        :type data: str
        """
        self.setData(constants.CACHE_FILE_DATA_VALUE, 0, filepath)

    def iconTint(self, overlay):
        """Set the overlay of the item.

        :param overlay: The new overlay of the item.
        :type overlay: :class:`QPixmap`
        """
        pixmap = self.default_icon

        if isinstance(pixmap, QtGui.QPixmap):
            self.setPixmap(pixmap)

            temp = QtGui.QPixmap(overlay)

            painter = QtGui.QPainter(temp)
            painter.setCompositionMode(painter.CompositionMode_Multiply)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()

            self.setPixmap(temp)


class Tree(QtWidgets.QTreeWidget):
    """Custom tree widget for the main window."""

    def __init__(self, parent=None):
        """Initializer.

        :param parent: The parent widget of this window. (None)
        :type parent: :class:`QWidget`
        """
        super(self.__class__, self).__init__(parent=parent)

        base_folder = os.path.dirname(os.path.dirname(__file__))
        ui_folder = os.path.join(base_folder, "ui")
        self.icon_folder = os.path.join(ui_folder, "icons").replace("\\", "/")

        style_sheet = self.getTreeStyleSheet()
        self.setStyleSheet(style_sheet)

        # settings for the tree widget
        self.setDragDropMode(self.DragDrop)
        self.setSelectionMode(self.ExtendedSelection)
        self.setAcceptDrops(True)
        self.setHeaderHidden(True)

        # slots
        self.itemDoubleClicked.connect(self.openEditor)
        self.currentItemChanged.connect(self.refreshAllItemPixmaps)

        # Connect the contextmenu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.menuContext)
        
        # custom shortcuts for tree widget
        QtWidgets.QShortcut(QtGui.QKeySequence("Backspace"), self, self.removeSelected, context=QtCore.Qt.WidgetShortcut)
        QtWidgets.QShortcut(QtGui.QKeySequence("Delete"), self, self.removeSelected, context=QtCore.Qt.WidgetShortcut)
        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_G), self, self.groupItems, context=QtCore.Qt.WidgetShortcut)

        # custom variables
        self.code_editor = None
        self.info_window = None
        self.drag_item = None

        # set the custom item delegate
        self.setItemDelegate(TreeItemDelegate())

        # cache the item when it emits a dataChanged signal
        self.model().dataChanged.connect(self.itemDataChangedEvent)

    def dragEnterEvent(self, event):
        """Do drag enter event.

        :param event: The drag enter event.
        :type event: :class:`QDragEnterEvent`
        """
        super(self.__class__, self).dragEnterEvent(event)
        self.drag_item = self.currentItem()

    def dropEvent(self, event):
        """Do drop event.

        :param event: The drop event.
        :type event: :class:`QDropEvent`
        """
        # check if we drop from self
        if event.source() is self:
            event.setDropAction(QtCore.Qt.MoveAction)
            super(self.__class__, self).dropEvent(event)
            
            # set the group color in the item data based on it's new parent
            parent_item = self.itemAt(event.pos())
            held_item = self.drag_item

            # don't set group color on drop event
            if held_item.getType() != "Group":
                # only want to change items that aren't groups
                # parent item will return None if no item is selected
                if parent_item:
                    for child in self.getSubtreeItems(held_item):
                        if parent_item is child.parent():
                            child.setGroupColor(parent_item.getGroupColor())
                else:
                    for child in self.getSubtreeItems(held_item):
                        child.setGroupColor(None)

        # this is used if the item comes from a listWidget
        if isinstance(event.source(), QtWidgets.QListWidget):
            # get the list widget info
            list_widget = event.source()
            list_items = list_widget.selectedItems()
            
            # get the tree widget info
            tree_item = self.itemAt(event.pos())

            # add the items selected in the list widget to the tree widget
            for list_item in list_items:
                # get the data from the list item
                list_item_name = list_item.getName()
                list_item_type = list_item.getType()
                list_item_file_path = list_item.getFilePath()
                list_item_code = list_item.getCode()
                
                # create a new tree item
                new_tree_item = TreeItem()
                new_tree_item.setPixmap(new_tree_item.script_pixmap)
                new_tree_item.setName(list_item_name)
                new_tree_item.setType(list_item_type)
                new_tree_item.setFilePath(list_item_file_path)
                new_tree_item.setCode(list_item_code)
                self.cacheItemCode(new_tree_item)

                # add the new item to the tree widget
                if tree_item:
                    tree_item.addChild(new_tree_item)
                else:
                    self.invisibleRootItem().addChild(new_tree_item)
                
                # set the group color in the item data based on it's new parent
                parent_item = tree_item
                held_item = new_tree_item
                if parent_item:
                    if parent_item is held_item.parent():
                        held_item.setGroupColor(parent_item.getGroupColor())
                else:
                    held_item.setGroupColor(held_item.getGroupColor()) 

    @QtCore.Slot(QtCore.QPoint)
    def menuContext(self, point):
        """Create a menu when the user right clicks on the tree widget.

        :param point: The point where the user clicks.
        :type point: object
        """
        # Info about the node selected.
        index = self.indexAt(point)

        # We build the menu.
        menu = QtWidgets.QMenu()

        # if an item is clicked within the tree, sort by item type
        if index.isValid():
            item = self.itemAt(point)
            item_type = item.getType()
    
            # only edit code for script or null types
            if item_type in ["Script", "Null"]:
                editor = menu.addAction("Open Code Editor")
                editor.triggered.connect(partial(self.openEditor, item))
                menu.addSeparator()

            null = menu.addAction("Add Null Item")
            group = menu.addAction("Add group")
            menu.addSeparator()
            
            if item_type == "Group":
                color_menu = menu.addMenu("Set Group Color")
                color_action = ColorAction(color_menu)
                color_menu.addAction(color_action)
                color_action.color_selected.connect(lambda color, event=item: self.setGroupGradient(color, item))

            ##### These items should always appear
            # add actions to menu
            rename = menu.addAction("Rename")
            enable = menu.addAction("Enable Tree")
            disable = menu.addAction("Disable Tree")
            menu.addSeparator()
            duplicate_item = menu.addAction("Duplicate Item")
            duplicate_tree = menu.addAction("Duplicate Tree")
            remove_item = menu.addAction("Remove Item")
            remove_tree = menu.addAction("Remove Tree")
            revert_item_code = menu.addAction("Revert Code")
            menu.addSeparator()
            info = menu.addAction("Info")

            # connect the signals to functions
            rename.triggered.connect(partial(self.renameItem, item))
            enable.triggered.connect(partial(self.enableTree, item))
            disable.triggered.connect(partial(self.disableTree, item))
            null.triggered.connect(partial(self.addNullItem, item))
            group.triggered.connect(partial(self.addGroupItem, item))
            duplicate_item.triggered.connect(partial(self.cloneItem, item))
            duplicate_tree.triggered.connect(partial(self.cloneTree, item))
            remove_item.triggered.connect(partial(self.removeItem, item))
            remove_tree.triggered.connect(partial(self.removeTree, item))
            revert_item_code.triggered.connect(partial(self.revertItemCode, item))
            info.triggered.connect(partial(self.openInfo, item))

        # if no item is clicked within the tree
        else:
            # add actions to menu
            null = menu.addAction("Add Null")
            group = menu.addAction("Add Group")

            # connect the signals to functions
            null.triggered.connect(self.addNullItem)
            group.triggered.connect(self.addGroupItem)

        menu.exec_(self.mapToGlobal(point))
    
    @QtCore.Slot(QtCore.QModelIndex)
    def itemDataChangedEvent(self, event):
        """Do events when the item is changed in any way.

        :param event: The item change event.
        :type event: :class:`QModelIndex`
        """
        item = self.itemFromIndex(event)
        if item.getType() != "Group":
            self.cacheItemCode(item)
    
    def cacheItemCode(self, item):
        """Create or update the cache file for the item.

        :param item: The item to cache.
        :type item: :class:`TreeItem`
        """
        if "PROMETHEUS_SCRIPTS_DATE_CACHE" in os.environ:
            if os.path.exists(os.environ["PROMETHEUS_SCRIPTS_DATE_CACHE"]):
                # get all the data from the item
                directory = os.environ["PROMETHEUS_SCRIPTS_DATE_CACHE"]
                prefix = "{}_".format(item.getName())
                extension = ".py"
                data = item.getCode()
                cache_file = item.getCacheFile()

                # update the cache file if it exists
                if cache_file:
                    cache_utils.updateTempFile(cache_file, data)
                else:
                    # create a new cache if the set one doesn't exist
                    new_cache = cache_utils.writeTempFile(directory, prefix, extension, data)
                    item.setCacheFile(new_cache)

    @QtCore.Slot(TreeItem)
    def renameItem(self, item):
        """Rename the item specified.

        :param item: The item to rename.
        :type item: :class:`TreeItem`
        """
        new_name, rename = QtWidgets.QInputDialog.getText(self, item.getName(), "Enter a new name")

        if item.isEdited():
            if item.getType() != "Null":
                new_name = new_name + " (edited)"
            else:
                new_name = new_name
        
        if rename:
            item.setName(new_name)
            new_filepath = cache_utils.renameCacheFile(item.getCacheFile(), new_name)
            item.setCacheFile(new_filepath)

    @QtCore.Slot(TreeItem)
    def enableTree(self, item):
        """Enable every item under the given item.

        :param item: The TreeItem.
        :type item: :class:`TreeItem`
        """
        for i in self.getSubtreeItems(item):
            i.setCheckState(0, QtCore.Qt.Checked)

    @QtCore.Slot(TreeItem)
    def disableTree(self, item):
        """Disable every item under the given item.

        :param item: The TreeItem.
        :type item: :class:`TreeItem`
        """
        for i in self.getSubtreeItems(item):
            i.setCheckState(0, QtCore.Qt.Unchecked)

    @QtCore.Slot(TreeItem)
    def removeItem(self, item):
        """Remove the given item under the tree.

        :param item: The TreeItem.
        :type item: :class:`TreeItem`
        """
        parent = item.parent()
        children = self.getImmediateChildren(item)

        if self.isTopLevelItem(item):
            # don't remove the children
            # move the children under the items parent
            for child in children:
                self.changeItemParent(child, self.invisibleRootItem())
            self.takeTopLevelItem(self.indexOfTopLevelItem(item))
        else:
            # don't remove the children
            # move the children under the items parent
            for child in children:
                self.changeItemParent(child, parent)
            parent.takeChild(parent.indexOfChild(item))
    
    @QtCore.Slot(TreeItem)
    def removeTree(self, item):
        """Remove every item under the given item.

        :param item: The TreeItem.
        :type item: :class:`TreeItem`
        """
        parent = item.parent()

        if self.isTopLevelItem(item):
            self.takeTopLevelItem(self.indexOfTopLevelItem(item))
        else:
            parent.takeChild(parent.indexOfChild(item))
    
    @QtCore.Slot(TreeItem, TreeItem)
    def changeItemParent(self, item, new_parent):
        """Change the given item parent to another parent.

        :param item: The TreeItem to change the parent of.
        :type item: :class:`TreeItem`

        :param new_parent: The new parent TreeItem.
        :type item: :class:`TreeItem`
        """
        old_parent = item.parent()
        if old_parent:
            ix = old_parent.indexOfChild(item)
            item_without_parent = old_parent.takeChild(ix)
        else:
            ix = self.indexOfTopLevelItem(item)
            item_without_parent = self.takeTopLevelItem(ix)
        new_parent.addChild(item_without_parent)

    @QtCore.Slot(TreeItem)
    def revertItemCode(self, item):
        """Reset the given item code to it's source code.

        :param item: The TreeItem.
        :type item: :class:`TreeItem`
        """
        file_path = item.getFilePath()
        if file_path:
            with open(item.getFilePath(), "r") as f:
                item.setCode(f.read())
        else:
            item.setCode("")
        item.setIsEdited(False)

    @QtCore.Slot(TreeItem)
    def cloneItem(self, item):
        """Clone the given item and all of it's data.

        :param item: The TreeItem to duplicate.
        :type item: :class:`TreeItem`

        :return: The new duplicate TreeItem.
        :rtype: :class:`TreeItem`
        """
        clone = TreeItem(None, item.clone())

        clone.setCheckState(0, item.checkState(0))

        if self.isTopLevelItem(item):
            self.addTopLevelItem(clone)
        else:
            parent = item.parent()
            parent.addChild(clone)
        
        if clone.getType() == "Group":
            self.setGroupGradient(clone.getGroupColor(), clone)
        
        return clone
    
    @QtCore.Slot(TreeItem)
    def cloneTree(self, item):
        """Clone the given item and all of it's children.

        :param item: The TreeItem.
        :type item: :class:`TreeItem`
        """
        # duplicate the entire tree
        # this will create treeWidgetItem instead of TreeItem
        base_clone = item.clone()
        if item.parent():
            item.parent().addChild(base_clone)

        # need to convert every treeWidgetItem to TreeItem
        for child in self.getSubtreeItems(base_clone):
            # this will create a new TreeItem
            new_clone = self.cloneItem(child)

            # parent the base_clone children to the new clone
            for grandchild in self.getImmediateChildren(child):
                self.changeItemParent(grandchild, new_clone)

            self.removeItem(child)

    @QtCore.Slot(TreeItem)
    def addNullItem(self, parent=None):
        """Create a new null item at or under the selected location.

        :param parent: The selected item. (None)
        :type parent: :class:`TreeItem`

        :return: The new Null TreeItem.
        :rtype: :class:`TreeItem`
        """
        item = TreeItem()
        item.setName("Null")
        item.setType("Null")
        item.setPixmap(item.null_pixmap)
        item.setCode("")
        #item.setCacheFile("")
        self.cacheItemCode(item)

        # create a new cache file for this item

        if parent:
            parent.addChild(item)
            item.setGroupColor(parent.getGroupColor())
        else:
            self.addTopLevelItem(item)
        
        return item
    
    @QtCore.Slot(TreeItem)
    def addGroupItem(self, parent=None):
        """Create a new group item at or under the selected location.

        :param parent: The selected item. (None)
        :type parent: :class:`TreeItem`

        :return: The new Group TreeItem.
        :rtype: :class:`TreeItem`
        """
        item = TreeItem()
        item.setName("Group")
        item.setType("Group")
        item.setPixmap(item.group_pixmap)

        if parent:
            parent.addChild(item)
            self.setGroupGradient(parent.getGroupColor(), item)
        else:
            self.addTopLevelItem(item)
        
        return item
    
    @QtCore.Slot(QtGui.QColor, TreeItem)
    def setGroupGradient(self, color, item):
        """Set the group gradient to the given color.

        :param color: The color to set the gradient to.
        :type color: object

        :param item: The item to set the group color of.
        :type item: :class:`TreeItem`
        """
        # create a new gradient and assign the colors
        gradient = QtGui.QLinearGradient(QtCore.QPointF(100, 100), QtCore.QPointF(200, 100))
        
        if color:
            gradient.setColorAt(0, QtCore.Qt.transparent)
            gradient.setColorAt(1, color)
        else:
            gradient.setColorAt(0, QtCore.Qt.transparent)
            gradient.setColorAt(1, QtCore.Qt.transparent)
        brush = QtGui.QBrush(gradient)
        item.setBackground(0, brush)

        # set the group color of the group item
        item.setGroupColor(color)

        # for all the the children under the group item, assign the same color 
        # unless it's another group with a different color, then do the same to that tree
        for i in self.getSubtreeItems(item)[1:]:
            if i.getType() == "Group":
                if not i.getGroupColor():
                    self.setGroupGradient(color, i)
            else:
                i.setGroupColor(color)

    @QtCore.Slot(TreeItem)
    def openInfo(self, item):
        """Open the info window for the current item.

        :param item: The item to get the info of.
        :type item: :class:`TreeItem`
        """
        item_type = item.getType()

        # if there's already a window open, close it
        if self.info_window:
            self.info_window.close()

        # open a fresh window
        self.info_window = info_window.InfoWindow(self.parent())
        self.info_window.run(item)

    @QtCore.Slot(TreeItem)
    def updateItemCode(self, item):
        """Update the item code editor to the given item's code data.

        :param item: The TreeItem to update the code of.
        :type item: :class:`TreeItem`
        """
        item.setCode(self.code_editor.getText())

        if not item.isEdited():
            item.setIsEdited(True)

    @QtCore.Slot(TreeItem)
    def openEditor(self, item):
        """Open the code editor and fill it with the item code.

        :param item: The TreeItem to open the editor for.
        :type item: :class:`TreeItem`
        """
        if item.getType() != "Group":
            # opens the code editor
            file_code = item.getCode()

            # if there's already a window open, close it
            if self.code_editor:
                self.code_editor.close()
            
            # open a fresh window
            self.code_editor = code_editor.MainWindow(self.parent())
            self.code_editor.run(file_code)

            # when any code is changed, update the tree item that was opened
            self.code_editor.editor.textChanged.connect(partial(self.updateItemCode, item))

    def getSubtreeItems(self, item):
        """Return all child items at the given node.

        :param item: The TreeItem to get the children of.
        :type item: :class:`TreeItem`

        :return: List of tree items.
        :rtype: list
        """
        nodes = []
        nodes.append(item)
        for i in range(item.childCount()):
            nodes.extend(self.getSubtreeItems(item.child(i)))
        return nodes

    def getAllItems(self):
        """Return all items within the tree widget.

        :return: List of tree items.
        :rtype: list
        """
        all_items = []
        for i in range(self.topLevelItemCount()):
            top_item = self.topLevelItem(i)
            all_items.extend(self.getSubtreeItems(top_item))
        return all_items

    def getTopLevelItems(self):
        """Return all top level items within the tree widget.

        :return: List of tree items.
        :rtype: list
        """
        top_level_items = []
        for x in range(self.topLevelItemCount()):
            top_level_items.append(self.topLevelItem(x))
        return top_level_items

    def getImmediateChildren(self, item):
        """Return all immediate children of the given item.

        :param item: The TreeItem to get the immediate children of.
        :type item: :class:`TreeItem`

        :return: List of tree items
        :rtype: list
        """
        # get only the immediate children because this is recursive
        children = []
        sub_nodes = self.getSubtreeItems(item)
        if len(sub_nodes) > 1:
            for child in sub_nodes[1:]:
                if child.parent() is item:
                    children.append(child)
        return children
    
    def isTopLevelItem(self, item):
        """Return whether the given item is a top level item or not.

        :param item: The TreeItem.
        :type item: :class:`TreeItem`

        :return: Return True if the item has no parent.
        :rtype: bool
        """
        parent = item.parent()
        if parent is None:
            return True
        else:
            return False
    
    @QtCore.Slot()
    def groupItems(self):
        """Create a group item and parent all selected items under the newly created group."""
        # get the selected items
        selected_items = self.selectedItems()

        # store the selected items parents into a list
        selected_items_parents_list = []
        for item in selected_items:
            selected_items_parents_list.append(item.parent())
        
        # if all the parents are the same, use it as the new group parent
        parents_list_no_duplicates = list(dict.fromkeys(selected_items_parents_list))
        if len(parents_list_no_duplicates) == 1:
            group_parent = parents_list_no_duplicates[0]
        else:
            group_parent = None

        # create the group item and parent all selected items under it
        group = self.addGroupItem(parent=group_parent)
        for item in selected_items:
            self.changeItemParent(item, group)

    @QtCore.Slot()
    def removeSelected(self):
        """Remove the selected tree items."""
        for item in self.selectedItems():
            if self.isTopLevelItem(item):
                self.takeTopLevelItem(self.indexOfTopLevelItem(item))
            else:
                parent = item.parent()
                parent.takeChild(parent.indexOfChild(item))

    @QtCore.Slot()
    def refreshAllItemPixmaps(self):
        """Set all items back to their defualt pixmaps."""
        for item in self.getAllItems():
            item.setPixmap(item.default_icon)

    def getTreeStyleSheet(self):
        """Return the style sheet used for a tree widget.

        :return: The style sheet to be used.
        :rtype: str
        """
        style = """QTreeView::branch:has-siblings:!adjoins-item {border-image: url(%s/vline.png) 0;}
                QTreeView::branch:has-siblings:adjoins-item {border-image: url(%s/branch-more.png) 0;}
                QTreeView::branch:!has-children:!has-siblings:adjoins-item {border-image: url(%s/branch-end.png) 0;}
                QTreeView::branch:has-children:!has-siblings:closed,
                QTreeView::branch:closed:has-children:has-siblings {border-image: none;image: url(%s/branch-closed.png);}
                QTreeView::branch:open:has-children:!has-siblings,
                QTreeView::branch:open:has-children:has-siblings  {border-image: none;image: url(%s/branch-open.png);}
                """ % (self.icon_folder, self.icon_folder, self.icon_folder, self.icon_folder, self.icon_folder)
        return style

    def hierarchyTree(self, parent, tree_dict):
        """Add all child info of the parent to the tree dictionary.

        :param parent: The TreeItem to get the hierarchy of.
        :type parent: :class:`TreeItem`

        :param tree_dict: The dictionary to assign the child lists to.
        :type tree_dict: dict
        """
        # get only the immediate children because this is recursive
        children = self.getImmediateChildren(parent)
        child_list = self.getConfigChildList(children)

        # update the dict
        for x, child in enumerate(children):
            tree_dict[x] = (child_list[x], {})
            
            if self.getImmediateChildren(child):  
                self.hierarchyTree(child, tree_dict[x][1])

    def getConfigChildList(self, children):
        """Return the list of dictionaries containing the children data.

        :param children: The list of TreeItems.
        :type children: list of :class:`TreeItem`

        :return: List of dictionaries of all children.
        :rtype: list of dict
        """
        # get a dict of all the children data, then add to a list
        child_list = []
        child_data = {}
        for child in children:
            if child.getGroupColor():
                group_color = child.getGroupColor().getRgbF()
            else:
                group_color = None
            child_data = {  "name" : child.getName(),
                            "type" : child.getType(),
                            "file_path" : child.getFilePath(),
                            "code" : child.getCode(),
                            "group_color" : group_color,
                            "is_edited" : child.isEdited(),
                            "is_enabled" : child.isEnabled()} 
            child_list.append(child_data)
        
        return child_list

    def buildConfigChildData(self, parent, tree_dict):
        """Build a dictionary of all the child data to the dictionary given.

        :param parent: The list of TreeItems.
        :type parent: list of :class:`TreeItem`

        :param tree_dict: The current dictionary to assign child data to.
        :type tree_dict: dict
        """
        # this function adds the treeItem to the tree
        for child in sorted(tree_dict):
            child_data = tree_dict[child][0]
            grandchild_data = tree_dict[child][1]

            # create a new tree item
            new_tree_item = TreeItem()
            new_tree_item.setName(child_data["name"])
            new_tree_item.setType(child_data["type"])
            new_tree_item.setFilePath(child_data["file_path"])
            new_tree_item.setCode(child_data["code"])
            new_tree_item.setIsEdited(child_data["is_edited"])
            new_tree_item.setIsEnabled(child_data["is_enabled"])

            # need to convert strings to qt data from json dict
            if child_data["type"] == "Null":
                new_tree_item.setPixmap(new_tree_item.null_pixmap)
            elif child_data["type"] == "Group":
                new_tree_item.setPixmap(new_tree_item.group_pixmap)
            elif child_data["type"] == "Script":
                new_tree_item.setPixmap(new_tree_item.script_pixmap)

            if child_data["group_color"]:
                r = child_data["group_color"][0]
                g = child_data["group_color"][1]
                b = child_data["group_color"][2]
                a = child_data["group_color"][3]
                new_tree_item.setGroupColor(QtGui.QColor.fromRgbF(r, g, b, a))
                if new_tree_item.getType() == "Group":
                    self.setGroupGradient(new_tree_item.getGroupColor(), new_tree_item)

            # add the new child
            parent.addChild(new_tree_item)

            # if there's any grandchildren, then rerun this function
            if grandchild_data:
                self.buildConfigChildData(new_tree_item, grandchild_data)

    def buildConfigParentData(self, tree_dict):
        """Assign all the top level items to the given dictionary.

        :param tree_dict: The current dictionary to assign child data to.
        :type tree_dict: dict
        """
        # this function builds the top level items
        for parent in sorted(tree_dict):
            parent_data = tree_dict[parent][0]
            child_data = tree_dict[parent][1]

            # create a new tree item
            new_tree_item = TreeItem()
            new_tree_item.setName(parent_data["name"])
            new_tree_item.setType(parent_data["type"])
            new_tree_item.setFilePath(parent_data["file_path"])
            new_tree_item.setCode(parent_data["code"])
            new_tree_item.setIsEdited(parent_data["is_edited"])
            new_tree_item.setIsEnabled(parent_data["is_enabled"])

            # need to convert strings to qt data from json dict
            if parent_data["type"] == "Null":
                new_tree_item.setPixmap(new_tree_item.null_pixmap)
            elif parent_data["type"] == "Group":
                new_tree_item.setPixmap(new_tree_item.group_pixmap)
            elif parent_data["type"] == "Script":
                new_tree_item.setPixmap(new_tree_item.script_pixmap)

            if parent_data["group_color"]:
                r = parent_data["group_color"][0]
                g = parent_data["group_color"][1]
                b = parent_data["group_color"][2]
                a = parent_data["group_color"][3]
                new_tree_item.setGroupColor(QtGui.QColor.fromRgbF(r, g, b, a))
                if new_tree_item.getType() == "Group":
                    self.setGroupGradient(new_tree_item.getGroupColor(), new_tree_item)

            # add the new item to the tree widget
            self.invisibleRootItem().addChild(new_tree_item)

            if child_data:
                self.buildConfigChildData(new_tree_item, child_data)

    @QtCore.Slot()
    def saveConfig(self):
        """Save all the tree item data with the tree widget to a json file."""
        config_dict = {}

        top_items = self.getTopLevelItems()
        top_items_list = self.getConfigChildList(top_items)

        # need to get a single stacked tree
        for x, top_item in enumerate(top_items):
            hierarchy_tree_dict = {}
            self.hierarchyTree(top_item, hierarchy_tree_dict)

            if top_item.getGroupColor():
                group_color = top_item.getGroupColor().getRgbF()
            else:
                group_color = None  

            data = {"name" : top_item.getName(),
                    "type" : top_item.getType(),
                    "file_path" : top_item.getFilePath(),
                    "code" : top_item.getCode(),
                    "group_color" : group_color,
                    "is_edited" : top_item.isEdited(),
                    "is_enabled" : top_item.isEnabled()}

            config_dict.update({x : (data, hierarchy_tree_dict)})
        
        json_utils.saveAsJson(config_dict)

    @QtCore.Slot()
    def loadConfig(self):
        """Load a config file and fill the tree widget with all the data in the config file."""
        # clear the tree before adding anything
        self.clear()

        # create the items with the data
        config_dict = json_utils.loadAsJson()
        if config_dict:
            # dict looks like {parent_name:({parent_data}, {[child:({child_data}, {})]})}
            self.buildConfigParentData(config_dict)

    def exportCodeToFile(self, directory, item):
        """Write the item code to a python file. Will name the python file the name of the item.

        :param directory: The folder location to save the file at.
        :type directory: str

        :param item: The TreeItem to export the code of.
        :type item: :class:`TreeItem`
        """
        # get the code from the item
        item_code = item.getCode()

        # set the filepath variable
        filepath = os.path.join(directory, "{}.py".format(item.getName()))

        # if the path already exists, prompt the user to rename if they wish to
        if os.path.exists(filepath):
            message = "{}.py already exists in this folder, name it something else?".format(item.getName())
            change_name = cmds.promptDialog(m=message, button=['Change Name', 'Overwrite'])
            if change_name == "Change Name":
                new_name = cmds.promptDialog(query=True, text=True)
                if not new_name.endswith(".py"):
                    new_name = "{}.py".format(new_name)
                filepath = os.path.join(directory, new_name)

        # Write the code to a python file at the directory location
        with open(filepath, 'w+') as outfile:
            outfile.write(item_code)
        print ('File Saved:', filepath)
        return filepath
    
    @QtCore.Slot()
    def exportSelected(self):
        """Write all the selected items code to python files."""
        # get the folder location to save to
        directory = cmds.fileDialog2(fm=3)[0]
        if directory and os.path.exists(directory):
            for item in self.selectedItems():
                if item.getType() != "Group":
                    self.exportCodeToFile(directory, item)


class TreeItemDelegate(QtWidgets.QStyledItemDelegate):
    """Custom delegate of the tree items to be used."""

    def paint(self, painter, option, index):
        """Do paint event. Will allow the user to disable items and still select them.
        
        :param painter: The QPainter oject.
        :type painter: :class:`QPainter`

        :param option: The widget option.
        :type option: object

        :param index: The model index.
        :type index: :class:`QModelIndex`
        """
        # the color here is only to make the unchecked items appear greyed out
        if index.model().data(index, QtCore.Qt.CheckStateRole):
            color = QtGui.QColor(0, 0, 0, 0)
        else:
            color = QtGui.QColor(0, 0, 0, 75)
        
        # This applies the greyed out color to each item if it's unchecked
        QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)
        painter.save()
        painter.setCompositionMode(painter.CompositionMode_Multiply)
        painter.fillRect(option.rect, color)
        painter.restore()

        # update the foreground colors based on the items data group color
        tree = index.model().parent()
        for child in tree.getAllItems():
            if isinstance(child, TreeItem):
                # if its a group, set it to itself
                if child.getType() == "Group":
                    child.setData(0, QtCore.Qt.ForegroundRole, child.getGroupColor())
                # if its not a group, set it to its parent's color
                else:
                    if child.parent():
                        child.setData(0, QtCore.Qt.ForegroundRole, child.parent().getGroupColor())
                    else:
                        child.setData(0, QtCore.Qt.ForegroundRole, None)
            
            # This adds an outline around the checkbox of every item
            # just for easier display
            painter.save()
            painter.setPen(QtGui.QColor(100, 100, 100, 255))
            rectangle = QtCore.QRectF(option.rect)
            rectangle.setX(rectangle.x() + 1)
            rectangle.setY(rectangle.y() + 2)
            rectangle.setWidth(13)
            rectangle.setHeight(13)
            painter.drawRect(rectangle)
            painter.restore()


class ListItem(QtWidgets.QListWidgetItem):
    """Custom listWidgetItem to be used in the main window List."""

    def getName(self):
        """Return the name of the item.

        :return: The name of the item.
        :rtype: str
        """
        return self.data(constants.NAME_DATA_VALUE)
    
    def getType(self):
        """Return the item type.

        :return: The item type.
        :rtype: str
        """
        return self.data(constants.TYPE_DATA_VALUE)
    
    def getFilePath(self):
        """Return the file path of the item.

        :return: The file path of the item.
        :rtype: str
        """
        return self.data(constants.FILE_PATH_DATA_VALUE)
    
    def getCode(self):
        """Return the code of the item.

        :return: The code of the item.
        :rtype: str
        """
        return self.data(constants.CODE_DATA_VALUE)

    def setName(self, data):
        """Set the name of the item.

        :param data: The name of the item.
        :type data: str
        """
        self.setData(constants.NAME_DATA_VALUE, data)
    
    def setType(self, data):
        """Set the item type.

        :param data: The item type.
        :type data: str
        """
        self.setData(constants.TYPE_DATA_VALUE, data)

    def setFilePath(self, data):
        """Set the file path of the item.

        :param data: The file path of the item.
        :type data: str
        """
        self.setData(constants.FILE_PATH_DATA_VALUE, data)
    
    def setCode(self, data):
        """Set the code of the item.

        :param data: The code of the item.
        :type data: str
        """
        self.setData(constants.CODE_DATA_VALUE, data)


class List(QtWidgets.QListWidget):
    """Custom list widget that works with the custom tree widget."""

    def __init__(self, parent=None):
        """Initializer.

        :param parent: The parent widget of this window. (None)
        :type parent: object
        """
        super(self.__class__, self).__init__(parent=parent)

        self.setDragDropMode(self.DragDrop)
        self.setSelectionMode(self.ExtendedSelection)
        self.setAcceptDrops(False)

        # Connect the contextmenu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.menuContext)

        # get file path of the modules
        self.default_script_path = path_utils.getUserScriptsLibrary("default_user")
        self.user_script_path = path_utils.getUserScriptsLibrary(getpass.getuser())

        # set the script paths 
        self.script_paths = [self.default_script_path, self.user_script_path]
        self.updateListItems()

    def updateListItems(self):
        """Update the list widget and add all new items based on the script path."""
        self.clear()
        for path in self.script_paths:
            for module in os.listdir(path):
                if not module.endswith(".pyc") and module.endswith(".py"):
                    if module != "__init__.py":
                        
                        # data to be saved with the new item
                        module_name = module.replace(".py", "")
                        file_path = os.path.join(path, module)
                        with open(file_path, 'r') as f:
                            file_code = f.read()

                        # create a new item
                        list_item = ListItem()

                        # set the item's data
                        list_item.setName(module_name)
                        list_item.setType("Script")
                        list_item.setFilePath(file_path)
                        list_item.setCode(file_code)

                        # add the item to the list
                        self.addItem(list_item)
    
    def addScriptPath(self, path):
        """Add the folder path to the script path list.

        :param path: The folder location.
        :type path: str
        """
        if path not in self.script_paths:
            self.script_paths.append(path)
            self.updateListItems()

    def removeScriptPath(self, path):
        """Remove the folder path from the script path list.

        :param path: The folder location.
        :type path: str
        """
        if path in self.script_paths:
            self.script_paths.remove(path)
            self.updateListItems()
    
    def resetScriptPath(self):
        """Remove all folder paths from the script paths variable."""
        self.script_paths = [self.default_script_path, self.user_script_path]
        self.updateListItems()

    @QtCore.Slot()
    def updateScriptPaths(self, path_list):
        """Update the script paths."""
        self.script_paths = []
        for path in path_list:
           if os.path.exists(path):
               self.addScriptPath(path)

    @QtCore.Slot()
    def openScriptPathWindow(self):
        """Change the script location to a prompted location."""
        self.script_path_window = script_path_window.ScriptPathsWindow(parent=self, paths=self.script_paths)
        self.script_path_window.show()

        # connect the list change signal to update the script paths list
        self.script_path_window.list_changed.connect(self.updateScriptPaths)

    @QtCore.Slot(QtCore.QPoint)
    def menuContext(self, point):
        """Create a menu when the user right clicks on the list widget.

        :param point: The point where the user clicks.
        :type point: object
        """
        # Info about the node selected.
        index = self.indexAt(point)

        # We build the menu.
        menu = QtWidgets.QMenu()
        
        # add actions to menu
        refresh = menu.addAction("Refresh")

        # connect actions to functions
        refresh.triggered.connect(self.updateListItems)

        menu.exec_(self.mapToGlobal(point))


class ColorAction(QtWidgets.QWidgetAction):
    """Create an action menu containing a list of QColors."""

    color_selected = QtCore.Signal(object)

    def __init__(self, parent):
        """Initializer.

        :param parent: The parent of this action.
        :type parent: object
        """
        # create the action as a widget
        QtWidgets.QWidgetAction.__init__(self, parent)
        widget = QtWidgets.QWidget(parent)

        # set the layout
        layout = QtWidgets.QGridLayout(widget)
        layout.setSpacing(0)
        layout.setContentsMargins(2, 2, 2, 2)

        # get the palette and set the colors
        palette = self.palette()
        count = len(palette)
        rows = int(count // round(count ** .5))
        for row in range(rows):
            for column in range(count // rows):
                qcolor = palette.pop()
                button = QtWidgets.QToolButton(widget)
                button.setAutoRaise(True)
                button.clicked.connect(partial(self.handleButton, qcolor))
                pixmap = QtGui.QPixmap(16, 16)
                pixmap.fill(qcolor)
                button.setIcon(QtGui.QIcon(pixmap))
                layout.addWidget(button, row, column)
        self.setDefaultWidget(widget)

    @QtCore.Slot(QtGui.QColor)
    def handleButton(self, color):
        """Emit a signal when a color is pressed within the action menu.

        :param color: The selected color.
        :type color: :class:`QColor`
        """
        if color.getRgbF() == (0, 0, 0, 0):
            self.color_selected.emit(None)
        else:
            self.color_selected.emit(color)

    def palette(self):
        """Return the list of colors to be used."""
        # create the color palette based on rgb colors
        palette = []
        for g in range(4):
            for r in range(4):
                for b in range(3):
                    palette.append(QtGui.QColor(r * 255 // 3, g * 255 // 3, b * 255 // 2))
        palette.append(QtGui.QColor(0, 0, 0, 0))
        return palette
