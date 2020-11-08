import sys

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter

def format(color, style=''):
    _color = QColor()
    _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format

STYLES = {
    'brace': format("#3777ef"),
    'tag': format("orange", "bold"),
    'parameter': format("magenta", "italic"),
    'string': format('green'),
    'comment': format('gray'),
}


class HtmlHighlighter(QSyntaxHighlighter):
    # html keywords
    
    braces = ['\<', "\>"]
    
    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)
        self.tri_single = (QRegExp("<!--"), 1, STYLES['comment'])

        rules = []
        
        rules += [
            (r"\<+(\w)*", 0, STYLES["tag"]),
            (r"\</+(\w)*", 0, STYLES["tag"]),
            (r"\-\-\>", 0, STYLES["comment"]),
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),
            (r"\b(\w)+\=", 0, STYLES["parameter"])
        ]

        rules += [(r'%s' % b, 0, STYLES['brace'])
            for b in HtmlHighlighter.braces]

        rules += [(r"\-\-\>", 0, STYLES["comment"])]

        self.rules = [(QRegExp(pat), index, fmt)
            for (pat, index, fmt) in rules]


    def highlightBlock(self, text):
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                index = expression.pos(nth)
                length = expression.cap(nth).__len__()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        in_multiline = self.match_multiline(text, *self.tri_single)



    def match_multiline(self, text, delimiter, in_state, style):
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
            end_tag = QRegExp("-->").indexIn(text)

        else:
            start = delimiter.indexIn(text)
            add = delimiter.matchedLength()
            end_tag = QRegExp("-->").indexIn(text)
            
        while start >= 0:
            end = end_tag
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            else:
                self.setCurrentBlockState(in_state)
                length = text.__len__() - start + add
            self.setFormat(start, length, style)
            start = delimiter.indexIn(text, start + length)
        if self.currentBlockState() == in_state:
            return True
        else:
            return False

