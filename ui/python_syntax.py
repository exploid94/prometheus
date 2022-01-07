"""Custom syntax settings for python code to be used with a QPlainTextEditor."""

import re

from PySide2 import QtCore, QtGui


def format(color, style=""):
    """Return a QTextCharFormat with the given attributes.

    :param color: The color to format.
    :type color: object

    :param style: The style of the text. Can be bold or italic. ("")
    :type style: str

    :return: The text format.
    :rtype: :class:`QTextCharFormat`
    """
    _color = QtGui.QColor()
    _color.setNamedColor(color)

    _format = QtGui.QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QtGui.QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


# Syntax styles that can be shared by all languages
STYLES = {'keyword' : format('magenta'),
        'operator' : format('white'),
        'brace' : format('white'),
        'defclass' : format('cyan'),
        'string' : format('yellow'),
        'string2' : format('yellow'),
        'comment' : format('green'),
        'self' : format('cyan', 'italic'),
        'numbers' : format('grey'),
        'whitespace' : format('transparent')}


class PythonHighlighter(QtGui.QSyntaxHighlighter):
    """Syntax highlighter for the Python language."""

    # Python keywords
    keywords = ['and', 'assert', 'break', 'class', 'continue', 'def',
                'del', 'elif', 'else', 'except', 'exec', 'finally',
                'for', 'from', 'global', 'if', 'import', 'in',
                'is', 'lambda', 'not', 'or', 'pass', 'print',
                'raise', 'return', 'try', 'while', 'yield',
                'None', 'True', 'False']
    
    # Python operators
    operators = ['=',
                # Comparison
                '==', '!=', '<', '<=', '>', '>=',
                # Arithmetic
                '\+', '-', '\*', '/', '//', '\%', '\*\*',
                # In-place
                '\+=', '-=', '\*=', '/=', '\%=',
                # Bitwise
                '\^', '\|', '\&', '\~', '>>', '<<']

    # Python braces
    braces = ['\{', '\}', '\(', '\)', '\[', '\]']

    def __init__(self, parent=QtGui.QTextDocument):
        """Initializer.

        :param parent: The parent widget of this window. (QTextDocument)
        :type parent: :class:`QTextDocument`
        """
        super(self.__class__, self).__init__(parent)

        # Multi-line strings (expression, flag, style)
        self.tri_single = (QtCore.QRegExp(r"'''"), 1, STYLES['string2'])
        self.tri_double = (QtCore.QRegExp(r'"""'), 2, STYLES['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b{}\b'.format(w), 0, STYLES['keyword']) for w in PythonHighlighter.keywords]
        rules += [(r'{}'.format(o), 0, STYLES['operator']) for o in PythonHighlighter.operators]
        rules += [(r'{}'.format(b), 0, STYLES['brace']) for b in PythonHighlighter.braces]

        # All other rules
        rules += [
            # 'self'
            (r'\bself\b', 0, STYLES['self']),

            # 'def' followed by an identifier
            (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),
            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, STYLES['defclass']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*\S*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*\S*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # From '#' until a newline
            (r'#[^\n]*', 0, STYLES['comment']),
            
            # for whitespace
            (r'\s', 0, STYLES['whitespace']),

        ]

        # Build a QRegExp for each pattern
        self.rules = [(QtCore.QRegExp(pat), index, fmt) for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.

        :param text: The text to highlight.
        :type text: str
        """
        self.triple_quoutes_within_strings = []
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)
            if index >= 0:
                # if there is a string we check
                # if there are some triple quotes within the string
                # they will be ignored if they are matched again
                if expression.pattern() in [r'"[^"\\]*\S*(\\.[^"\\]*)*"', r"'[^'\\]*\S*(\\.[^'\\]*)*'"]:
                    
                    inner_index = self.tri_single[0].indexIn(text, index + 1)
                    if inner_index - 1:
                        inner_index = self.tri_double[0].indexIn(text, index + 1)

                    if inner_index != -1:
                        triple_quote_indexes = range(inner_index, inner_index + 3)
                        self.triple_quoutes_within_strings.extend(triple_quote_indexes)

            while index >= 0:
                # skipping triple quotes within strings
                if index in self.triple_quoutes_within_strings:
                    index += 1
                    expression.indexIn(text, index)
                    continue

                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.matchMultiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.matchMultiline(text, *self.tri_double)
        
        # need to set all whitespaces to their format
        # using re module until i can figure out how to do it in qt regexp
        expression = re.compile(r'\s')
        m = expression.search(text)
        while m is not None:
            start, end = m.span()
            self.setFormat(start, end - start, STYLES['whitespace'])
            m = expression.search(text, end)

    def matchMultiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. 

            .. note::
                ``delimiter`` should be a ``QRegExp`` for triple-single-quotes 
                or triple-double-quotes, and ``in_state`` should be a unique 
                integer to represent the corresponding state changes when inside those strings. 
                Return True if we're still inside a multi-line string when this function is finished.

        :param text: The current text.
        :type text: str

        :param delimiter: The regular expression used.
        :type delimiter: :class:`QRegExp`

        :param in_state: State changes inside the strings.
        :type in_state: int

        :param style: The style to set the format of.
        :type style: str
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() is in_state:
            start = 0
            add = 0

        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)

            # skipping triple quotes within strings
            if start in self.triple_quoutes_within_strings:
                return False

            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)

            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)

            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add

            # Apply formatting
            self.setFormat(start, length, style)

            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() is in_state:
            return True
        else:
            return False
