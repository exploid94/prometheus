"""Custom Python script editor to be used for editing code of Prometheus TreeItem."""

import sys

from PySide2 import QtGui, QtCore, QtWidgets
from shiboken2 import wrapInstance
from maya import OpenMayaUI
from maya import cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from dd_prometheus.ui import python_syntax


class MainWindow(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    """The main window of the code editor."""

    tool_name = 'Prometheus Code Editor'
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
        self.resize(800, 600)

        # Create main layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        # create the editor
        self.editor = TextEditor()

        # add the editor to the layout
        self.main_layout.addWidget(self.editor)

    def getText(self):
        """Return the text contained within the code editor window.

        :return: Raw text within the window.
        :rtype: str
        """
        return self.editor.toPlainText() 

    def deleteInstances(self):
        """Delete any instances of MainWindow."""
        if cmds.workspaceControl("{}{}".format(self.tool_name, 'WorkspaceControl'), exists=True, q=True):
            cmds.deleteUI("{}{}".format(self.tool_name, 'WorkspaceControl'), control=True)

    def run(self, text=""):
        """Show the window with the given text.

        :param text: The text to display. ("")
        :type text: str
        """
        self.show()
        self.editor.setPlainText(text)


class LineNumberArea(QtWidgets.QWidget):
    """The line number area that displays line numbers."""

    def __init__(self, editor):
        """Initializer.

        :param editor: The parent widget of this window.
        :type editor: :class:`QWidget`
        """
        super(self.__class__, self).__init__(editor)
        self.my_editor = editor

    def sizeHint(self):
        """Return the size of self.

        :return: The width of the widget.
        :rtype: :class:`QSize`
        """
        return QtCore.Qsize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        """Do paint line number area on parent widget.

        :param event: The paint event.
        :type event: :class:`QPaintEvent`
        """
        self.my_editor.lineNumberAreaPaintEvent(event)


class TextEditor(QtWidgets.QPlainTextEdit):
    """The plain text editor of the window."""

    def __init__(self, parent=None):
        """Initializer.

        :param parent: The parent widget of this window. (None)
        :type parent: :class:`QWidget`
        """
        super(self.__class__, self).__init__(parent=parent)

        # settings for the whole editor
        self.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)

        # set the style for the text
        font = QtGui.QFont()
        font.setPixelSize(14)
        font.setLetterSpacing(QtGui.QFont.AbsoluteSpacing, 1)
        font.setWeight(55)
        font.setStyleHint(QtGui.QFont.Times)
        self.setFont(font)

        # show the spaces, 
        # but they will be transparent, they only show when selected
        option = QtGui.QTextOption()
        option.setFlags(QtGui.QTextOption.ShowTabsAndSpaces)
        self.document().setDefaultTextOption(option)

        # add the python_syntax
        self.highlight = python_syntax.PythonHighlighter(self.document())

        self.setTabChangesFocus(True)

        # add the line number area
        self.line_number_area = LineNumberArea(self)

        # connect the signals on line change
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        self.updateLineNumberAreaWidth(0)

    def keyPressEvent(self, event):
        """Do action when a key is pressed within the text editor.

        :param event: The key press event.
        :type event: :class:`QPaintEvent`

        :return: The key press event.
        :rtype: :class:`QPaintEvent`
        """
        # get the cursor
        cursor = self.textCursor()
        
        # save the start and end selection
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        
        # get the first and last lines selected
        cursor.setPosition(start)
        first_line = cursor.blockNumber() + 1
        cursor.setPosition(end)
        last_line = cursor.blockNumber() + 1
        line_count = (last_line - first_line) + 1

        # we don't want to inherit the original functions of tabbing
        # so don't use super in these keys
        if event.key() == QtCore.Qt.Key_Tab:
            cursor.beginEditBlock()
            self.tab(cursor, start, line_count)
            cursor.endEditBlock()
            return event
        
        elif event.key() == QtCore.Qt.Key_Backtab:
            cursor.beginEditBlock()
            self.backTab(cursor, start, first_line, last_line, line_count)
            cursor.endEditBlock()
            return event
        
        elif event.key() == QtCore.Qt.Key_Return:
            cursor.beginEditBlock()
            self.setIndentLevel()
            cursor.endEditBlock()
            return event

        else:
            super(self.__class__, self).keyPressEvent(event)

    def lineNumberAreaWidth(self):
        """Return the width of the line number area.

        :return: The width of the area.
        :rtype: int
        """
        count = max(1, self.blockCount())
        digits = len(str(count))
        space = 6 + (self.fontMetrics().width('1') * digits)
        return space

    @QtCore.Slot()
    def updateLineNumberAreaWidth(self, _):
        """Update the line number area width after getting the new area width."""
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    @QtCore.Slot(QtCore.QRect, int)
    def updateLineNumberArea(self, rect, dy):
        """Do update the line number area rect and width.

        :param rect: The rect object of the line number area.
        :type rect: :class:`QRect`

        :param dy: The new position to scroll to.
        :type dy: int
        """
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        """Do resize the line number area event.

        :param event: The resize event.
        :type event: :class:`QResizeEvent`
        """
        super(self.__class__, self).resizeEvent(event)

        contents_rect = self.contentsRect()
        self.line_number_area.setGeometry(QtCore.QRect(contents_rect.left(), contents_rect.top(), self.lineNumberAreaWidth(), contents_rect.height()))

    def lineNumberAreaPaintEvent(self, event):
        """Do paint the line number area.
        
        :param event: The line number paint event.
        :type event: :class:`QPaintEvent`
        """
        my_painter = QtGui.QPainter(self.line_number_area)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        # Just to make sure I use the right font
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(block_number + 1)
                my_painter.setPen(QtCore.Qt.darkGray)
                my_painter.drawText(0, top, self.line_number_area.width() - 3, height, QtCore.Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    @QtCore.Slot()
    def highlightCurrentLine(self):
        """Highlight the line that the user is currently on."""
        extra_selections = []

        if not self.isReadOnly():
            selection = QtWidgets.QTextEdit.ExtraSelection()

            line_color = QtGui.QColor(QtCore.Qt.gray).lighter(35)

            selection.format.setBackground(line_color)
            selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)
    
    def setIndentLevel(self):
        """Match the same indent level on the next line. Used upon return keypress."""
        # match same indent level when enter is hit
        indent_char_num = 0

        # move forward one character at a time
        # count the number of spaces there are
        cursor = self.textCursor()
        pos = cursor.position()
        cursor.movePosition(cursor.MoveOperation.StartOfLine, cursor.MoveAnchor)
        cursor.movePosition(cursor.MoveOperation.NextCharacter, cursor.KeepAnchor)
        self.setTextCursor(cursor)
        if cursor.selectedText().isspace():
            while cursor.selectedText().isspace():
                cursor.movePosition(cursor.MoveOperation.NextCharacter, cursor.MoveAnchor)
                cursor.movePosition(cursor.MoveOperation.NextCharacter, cursor.KeepAnchor)
                self.setTextCursor(cursor)
                indent_char_num += 1
                if not cursor.selectedText().isspace() or cursor.atBlockEnd():
                    break
        
        # if first word on current line is a keyword, indent on the next
        cursor.movePosition(cursor.MoveOperation.StartOfLine, cursor.MoveAnchor)
        cursor.movePosition(cursor.MoveOperation.NextWord, cursor.KeepAnchor)
        self.setTextCursor(cursor)
        while cursor.selectedText().isspace():
            cursor.movePosition(cursor.MoveOperation.NoMove, cursor.MoveAnchor)
            cursor.movePosition(cursor.MoveOperation.NextWord, cursor.KeepAnchor)
            self.setTextCursor(cursor)
            if cursor.selectedText().isspace() or cursor.atBlockEnd():
                break
        
        # add extra indentaiton if the first word is in keywords
        keywords = ['class', 'def', 'elif', 'else', 'except', 'for', 'if', 'try', 'while']
        if cursor.selectedText().strip() in keywords:
            indent_char_num += 4

        # set the cursor to the new location
        cursor.setPosition(pos)
        self.setTextCursor(cursor)

        # match previous indent level
        cursor.insertBlock()
        for x in range(indent_char_num):
            cursor.insertText(" ")

    def tab(self, cursor, start, line_count):
        """Add 4 spaces (tab) at the start of every line selected.

        :param cursor: The current cursor used within the text edit.
        :type cursor: :class:`QTextCursor`

        :param start: The starting position of the cursor.
        :type start: int

        :param line_count: The number of lines selected with the cursor.
        :type line_count: int
        """
        # tab makes four spaces at the start of the line for all lines selected
        cursor.setPosition(start) 
        for line in range(line_count):
            cursor.movePosition(cursor.MoveOperation.StartOfLine)
            cursor.insertText("    ")
            cursor.movePosition(cursor.MoveOperation.NextBlock)

    def backTab(self, cursor, start, first_line, last_line, line_count):
        """Remove up to 4 spaces (tab) at the start of every line selected.

        :param cursor: The current cursor used within the text edit.
        :type cursor: :class:`QTextCursor`

        :param start: The starting position of the cursor.
        :type start: int

        :param first_line: The first line selected.
        :type first_line: int

        :param last_line: The last line selected.
        :type last_line: int

        :param line_count: The number of lines selected with the cursor.
        :type line_count: int
        """
        cursor.setPosition(start, cursor.MoveAnchor)
        back_num = 0
        for line in range(line_count):
            cursor.movePosition(cursor.MoveOperation.StartOfLine, cursor.MoveAnchor)

            # now move forward 4 characters if possible
            # select only one character foreward at a time
            for x in range(4):
                cursor.movePosition(cursor.Right, cursor.MoveAnchor)
                cursor.movePosition(cursor.Left, cursor.KeepAnchor)
                self.setTextCursor(cursor)
                
                # dont remove the character if its not a whitespace
                if not cursor.atBlockEnd():
                    if cursor.selectedText().isspace():
                        # remove the selected text
                        cursor.removeSelectedText()
                        back_num = back_num + 1

            # move to the next line
            if line != line_count - 1:
                cursor.movePosition(cursor.MoveOperation.NextBlock)
            self.setTextCursor(cursor)
        
        # set the new start position for selecting the lines
        if not cursor.atBlockStart():
            cursor.setPosition(start - back_num, cursor.MoveAnchor)
        self.setTextCursor(cursor)

        # this is to select more than 2 lines
        # select the whole of the lines
        if line_count > 2:
            if cursor.blockNumber() + 1 == last_line:
                cursor.movePosition(cursor.EndOfLine, cursor.MoveAnchor)
                cursor.movePosition(cursor.StartOfLine, cursor.KeepAnchor)
                for x in range(line_count - 1):
                    cursor.movePosition(cursor.Up, cursor.KeepAnchor)
                self.setTextCursor(cursor)
            elif cursor.blockNumber() + 1 == first_line:
                cursor.movePosition(cursor.StartOfLine, cursor.MoveAnchor)
                for x in range(line_count - 1):
                    cursor.movePosition(cursor.Down, cursor.KeepAnchor)
                    cursor.movePosition(cursor.EndOfLine, cursor.KeepAnchor)
                self.setTextCursor(cursor)
        
        # this is to select just 2 lines
        # select the whole two lines
        elif line_count == 2:
            if cursor.blockNumber() + 1 == last_line:
                cursor.movePosition(cursor.EndOfLine, cursor.MoveAnchor)
                cursor.movePosition(cursor.Up, cursor.KeepAnchor)
                cursor.movePosition(cursor.StartOfLine, cursor.KeepAnchor)
                self.setTextCursor(cursor)
            elif cursor.blockNumber() + 1 == first_line:
                cursor.movePosition(cursor.StartOfLine, cursor.MoveAnchor)
                cursor.movePosition(cursor.Down, cursor.KeepAnchor)
                cursor.movePosition(cursor.EndOfLine, cursor.KeepAnchor)
                self.setTextCursor(cursor)     


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Prometheus Code Editor")

    window = MainWindow()
    app.exec_()
