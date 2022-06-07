import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()

# from PyQt6.QtWidgets import QTextEdit, QSizePolicy
from PyQt6.Qsci import QsciScintilla, QsciLexerPython, QsciLexerSQL, QsciLexerJSON
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QTimer

from q2gui.pyqt6.q2widget import Q2Widget


class q2code(QsciScintilla, Q2Widget):
    def __init__(self, meta):
        super().__init__(meta)
        self.setUtf8(True)
        self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle)

        self.lexer = None
        self.set_lexer()
        self.set_background_color()

        self.setAutoIndent(True)
        self.setIndentationGuides(True)
        self.setIndentationsUseTabs(False)
        self.setBraceMatching(QsciScintilla.BraceMatch.StrictBraceMatch)
        self.setMarginLineNumbers(1, True)
        self.setMarginWidth(1, "9999")
        self.setTabWidth(4)
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
        self.setAutoCompletionCaseSensitivity(True)
        self.setAutoCompletionReplaceWord(True)
        self.setAutoCompletionThreshold(0)

        self.searchIndicator = QsciScintilla.INDIC_CONTAINER
        self.SendScintilla(QsciScintilla.SCI_INDICSETSTYLE, self.searchIndicator, QsciScintilla.INDIC_BOX)
        self.SendScintilla(QsciScintilla.SCI_INDICSETFORE, self.searchIndicator, QColor("red"))

        self.cursorPositionChanged.connect(self.__cursorPositionChanged)
        self.__markOccurrencesTimer = QTimer(self)
        self.__markOccurrencesTimer.setSingleShot(True)
        self.__markOccurrencesTimer.setInterval(500)
        self.__markOccurrencesTimer.timeout.connect(self.__markOccurrences)
        self.textChanged.connect(self.valid)

    def set_lexer(self, lexer=""):
        if lexer == "":
            lexer = self.meta["control"]
        if "python" in lexer:
            self.lexer = QsciLexerPython()
        elif "sql" in lexer:
            self.lexer = QsciLexerSQL()
        elif "json" in lexer:
            self.lexer = QsciLexerJSON()
        else:
            self.lexer = QsciLexerPython()
        if self.lexer:
            self.setLexer(self.lexer)

    def set_background_color(self, red=150, green=200, blue=230):
        self.lexer.setDefaultPaper(QColor(red, green, blue))
        self.lexer.setPaper(QColor(red, green, blue))
        # self.setMatchedBraceForegroundColor(QColor("lightgreen"))

    def __cursorPositionChanged(self, line, index):
        self.__markOccurrencesTimer.stop()
        self.clearIndicatorRange(
            0, 0, self.lines() - 1, len(self.text(self.lines() - 1)), self.searchIndicator
        )
        self.__markOccurrencesTimer.start()

    def __findFirstTarget(self, text):
        if text == "":
            return False
        self.__targetSearchExpr = text.encode("utf-8")
        self.__targetSearchFlags = QsciScintilla.SCFIND_MATCHCASE | QsciScintilla.SCFIND_WHOLEWORD
        self.__targetSearchStart = 0
        self.__targetSearchEnd = self.SendScintilla(QsciScintilla.SCI_GETTEXTLENGTH)
        self.__targetSearchActive = True
        return self.__doSearchTarget()

    def __findNextTarget(self):
        if not self.__targetSearchActive:
            return False
        return self.__doSearchTarget()

    def __doSearchTarget(self):
        if self.__targetSearchStart == self.__targetSearchEnd:
            self.__targetSearchActive = False
            return False
        self.SendScintilla(QsciScintilla.SCI_SETTARGETSTART, self.__targetSearchStart)
        self.SendScintilla(QsciScintilla.SCI_SETTARGETEND, self.__targetSearchEnd)
        self.SendScintilla(QsciScintilla.SCI_SETSEARCHFLAGS, self.__targetSearchFlags)
        pos = self.SendScintilla(
            QsciScintilla.SCI_SEARCHINTARGET, len(self.__targetSearchExpr), self.__targetSearchExpr
        )
        if pos == -1:
            self.__targetSearchActive = False
            return False
        self.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, pos, len(self.__targetSearchExpr))
        targend = self.SendScintilla(QsciScintilla.SCI_GETTARGETEND)
        self.__targetSearchStart = targend
        return True

    def __markOccurrences(self):
        if self.hasFocus():
            line, index = self.getCursorPosition()
            ok = self.__findFirstTarget(self.__getWord(self.text(line), index - 1))
            while ok:
                ok = self.__findNextTarget()

    def __getWord(self, text, index):
        word = ""
        for x in range(index, -1, -1):
            if text[x].isalpha() or text[x].isdigit():
                word = text[x] + word
            else:
                break
        for x in range(index + 1, len(text)):
            if text[x].isalpha() or text[x].isdigit():
                word += text[x]
            else:
                break
        return word
