#    Copyright © 2021 Andrei Puchko
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()

# from PyQt6.QtWidgets import QTextEdit, QSizePolicy
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)

from PyQt6.Qsci import QsciScintilla, QsciLexerPython, QsciLexerSQL, QsciLexerJSON, QsciAPIs, QsciLexer
from PyQt6.QtGui import QColor

# from PyQt6.QtWidgets import QMenu
from PyQt6.QtCore import Qt, QTimer, QSize

from q2gui.pyqt6.q2widget import Q2Widget
from q2gui.pyqt6.widgets.q2line import q2line
from q2gui.pyqt6.widgets.q2label import q2label
from q2gui.pyqt6.widgets.q2button import q2button
from q2gui.q2utils import int_


class q2code(QsciScintilla, Q2Widget):
    def __init__(self, meta):
        super().__init__(meta)
        self.setUtf8(True)
        self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle)

        self.lexer: QsciLexer = None
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
        self.setAutoCompletionThreshold(1)

        self.SCN_DOUBLECLICK

        self.setCaretLineVisible(True)

        self.searchIndicator = QsciScintilla.INDIC_CONTAINER
        self.SendScintilla(QsciScintilla.SCI_INDICSETSTYLE, self.searchIndicator, QsciScintilla.INDIC_BOX)
        self.SendScintilla(QsciScintilla.SCI_INDICSETFORE, self.searchIndicator, QColor("red"))

        self.cursorPositionChanged.connect(self.__cursorPositionChanged)
        self.__markOccurrencesTimer = QTimer(self)
        self.__markOccurrencesTimer.setSingleShot(True)
        self.__markOccurrencesTimer.setInterval(500)
        self.__markOccurrencesTimer.timeout.connect(self.__markOccurrences)
        self.textChanged.connect(self.valid)
        # self.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.editor_panel = q2editor_panel(self)
        # self.create_context_menu()
        self.set_custom_autocompletition_list()

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

    def set_custom_autocompletition_list(self, custom_autocompletions_list=[]):
        custom_autocompletions_list = self.meta["form"].q2_app.get_autocompletition_list()
        self.__api = QsciAPIs(self.lexer)
        for ac in custom_autocompletions_list:
            self.__api.add(ac)
        self.__api.prepare()

    def set_background_color(self, red=150, green=200, blue=230):
        # color_mode = self.meta.get("q2_app").q2style.get_system_color_mode()
        # print(color_mode, self.meta.get("q2_app").q2style.color_mode)
        # b_color = QColor(self.meta.get("q2_app").q2style.styles.get(color_mode).get("background"))
        # f_color = QColor(self.meta.get("q2_app").q2style.styles.get(color_mode).get("color"))

        # self.setMatchedBraceForegroundColor(QColor("lightgreen"))
        self.lexer.setDefaultPaper(QColor(red, green, blue))
        self.lexer.setPaper(QColor(red, green, blue))
        # self.lexer.setDefaultPaper(b_color)
        # self.lexer.setPaper(b_color)
        # self.lexer.setColor(f_color, 5)
        self.setMarginsForegroundColor(QColor("black"))
        self.setMarginsBackgroundColor(QColor("gray"))

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

    def mouseDoubleClickEvent(self, event):
        return super().mouseDoubleClickEvent(event)

    def focusInEvent(self, ev):
        super().focusInEvent(ev)
        self.create_context_menu()

    def focusOutEvent(self, ev):
        self.clear_actions()
        super().focusInEvent(ev)

    def clear_actions(self):
        for x in self.actions():
            self.removeAction(x)

    def create_context_menu(self):
        self.context_menu = self.createStandardContextMenu()
        self.context_menu.addSeparator()

        find_action = self.context_menu.addAction("Find next")
        find_action.triggered.connect(self.editor_panel.show_find_next)
        find_action.setShortcuts(["Ctrl+F", "F3"])

        find_action = self.context_menu.addAction("Find prev")
        find_action.triggered.connect(self.editor_panel.show_find_prev)
        find_action.setShortcuts(["Shift+F3"])

        replace_action = self.context_menu.addAction("Replace")
        replace_action.triggered.connect(self.editor_panel.show_replace)
        replace_action.setShortcut("Ctrl+H")

        gotoline_action = self.context_menu.addAction("Go to line")
        gotoline_action.triggered.connect(self.editor_panel.show_go)
        gotoline_action.setShortcut("Ctrl+G")

        self.context_menu.addSeparator()

        fold_action = self.context_menu.addAction("Fold/Unfold")
        fold_action.triggered.connect(self.perform_folding)
        fold_action.setShortcuts(["Alt+Up", "Alt+Down"])

        foldall_action = self.context_menu.addAction("Fold/Unfold All")
        foldall_action.triggered.connect(self.foldAll)
        foldall_action.setShortcuts(["Alt+Left", "Alt+Right"])

        self.context_menu.addSeparator()
        comment_action = self.context_menu.addAction("Comment/uncomment line(s)")
        comment_action.setShortcut("Ctrl+3")
        comment_action.triggered.connect(self.perform_comment)

        complete_action = self.context_menu.addAction("Autocomplete")
        complete_action.triggered.connect(self.autoCompleteFromAll)
        complete_action.setShortcuts(["Ctrl+Space"])

        self.addActions(self.context_menu.actions())
        for x in self.context_menu.actions():
            if x.isEnabled():
                x.setVisible(True)
            else:
                x.setVisible(False)

    def perform_comment(self):
        selected_lines = []
        current_line, current_pos = self.getCursorPosition()
        if self.hasSelectedText():
            line1, pos1, line2, pos2 = self.getSelection()
            for x in range(line1, line2 + 1):
                selected_lines.append(x)
        else:
            selected_lines.append(current_line)

        for line in selected_lines:
            new_pos = self.comment_line(line, current_pos)
            if line == current_line:
                self.setCursorPosition(current_line, new_pos)

        if len(selected_lines) > 1:
            self.setSelection(line1, pos1, line2, pos2)

    def comment_line(self, line, pos):
        current_line = self.text(line)
        if len(current_line.strip()):
            if current_line.lstrip()[0:2] == "# ":
                comment_pos = current_line.index("# ")
                if comment_pos < pos:
                    pos -= 2
                self.setSelection(line, comment_pos, line, comment_pos + 2)
                self.removeSelectedText()
            else:
                spaces_count = len(current_line) - len(current_line.lstrip())
                if pos > spaces_count:
                    pos += 2
                self.insertAt("# ", line, spaces_count)
        return pos

    def perform_folding(self):
        self.foldLine(self.getCursorPosition()[0])

    def current_line(self):
        return self.getCursorPosition()[0]

    def goto_line(self, line=0):
        self.setCursorPosition(int_(line) - 1, 0)
        self.set_focus()
        self.ensureLineVisible(self.getCursorPosition()[0])
        self.editor_panel.close()

    def contextMenuEvent(self, event):
        self.create_context_menu()
        self.context_menu.exec(event.globalPos())

    def showEvent(self, ev):
        self.updateGeometry()
        return super().showEvent(ev)

    def sizeHint(self):
        if self.isVisible():
            return QSize(99999, 99999)
        else:
            return super().sizeHint()


class q2editor_panel(QWidget):
    def __init__(self, parent, text=""):
        super().__init__(parent, Qt.WindowType.Popup)
        # super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.setObjectName("editor_panel")

        self.layout().setContentsMargins(0, 0, 0, 0)
        # self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.create_find()
        self.create_replace()
        self.create_go()

        self.layout().addWidget(self.find_frame)
        self.layout().addWidget(self.replace_frame)
        self.layout().addWidget(self.go_frame)

        self.set_find_text(text)
        self.q2code: q2code = parent
        self.last_find_direction = "down"

    def create_find(self):
        self.find_frame = QWidget()

        self.find_frame.setLayout(QHBoxLayout())
        self.find_frame.layout().setContentsMargins(0, 0, 0, 0)

        self.find_next_button = q2button({"label": ">"})
        self.find_next_button.set_fixed_width(3, "w")

        self.find_prev_button = q2button({"label": "<"})
        self.find_prev_button.set_fixed_width(3, "w")

        self.find_text = q2line({})
        self.find_frame.layout().addWidget(q2label({"label": "find:"}))
        self.find_frame.layout().addWidget(self.find_text)
        self.find_frame.layout().addWidget(self.find_prev_button)
        self.find_frame.layout().addWidget(self.find_next_button)
        self.find_next_button.pressed.connect(self.perform_find_next)
        self.find_prev_button.pressed.connect(self.perform_find_prev)
        self.find_text.keyPressEvent = self.find_keyPressEvent

    def find_keyPressEvent(self, event):
        if event.key() in [Qt.Key.Key_Up] or (
            event.key() in [Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_F3]
            and event.modifiers() == Qt.KeyboardModifier.ShiftModifier
        ):
            self.perform_find_prev()
        elif event.key() in [Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Down, Qt.Key.Key_F3]:
            self.perform_find_next()
        elif event.key() == Qt.Key.Key_H:
            self.show_replace()
        q2line.keyPressEvent(self.find_text, event)

    def perform_find_next(self):
        self.q2code.findFirst(self.find_text.get_text(), False, False, False, False, True)
        self.last_find_direction = "down"

    def perform_find_prev(self):
        line1, index1, line2, index2 = self.q2code.getSelection()
        self.q2code.setCursorPosition(line1, index1)
        self.q2code.findFirst(self.find_text.get_text(), False, False, False, False, False)
        self.last_find_direction = "up"

    def create_replace(self):
        self.replace_frame = QWidget()
        self.replace_frame.setLayout(QHBoxLayout())
        self.replace_frame.layout().setContentsMargins(0, 0, 0, 0)
        self.replace_text = q2line({})
        self.replace_text.returnPressed.connect(self.perform_replace)

        self.replace_frame.layout().addWidget(q2label({"label": "replace:"}))
        self.replace_frame.layout().addWidget(self.replace_text)

        self.replace_button = q2button({"label": "Ok", "datalen": 4})
        self.replace_button.pressed.connect(self.perform_replace)
        # self.replace_button.set_fixed_width(3, "w")
        self.replace_frame.layout().addWidget(self.replace_button)

    def perform_replace(self):
        self.q2code.replace(self.replace_text.get_text())
        if self.last_find_direction == "down":
            self.perform_find_next()
        else:
            self.perform_find_prev()

    def create_go(self):
        self.go_frame = QWidget()
        self.go_frame.setLayout(QHBoxLayout())
        self.go_frame.layout().setContentsMargins(0, 0, 0, 0)
        self.go_text = q2line({"datatype": "int", "datalen": 5, "num": 1})
        self.go_frame.layout().addWidget(q2label({"label": "go to line:"}))
        self.go_frame.layout().addWidget(self.go_text)
        self.go_button = q2button({"label": ">"})
        self.go_button.set_fixed_width(3, "w")
        self.go_frame.layout().addWidget(self.go_button)
        self.go_frame.layout().addStretch()
        self.go_text.editingFinished.connect(self.perform_go)
        self.go_button.pressed.connect(self.perform_go)

    def perform_go(self):
        self.q2code.goto_line(self.go_text.get_text())

    def show_find(self):
        st = self.q2code.selectedText()
        if st:
            self.find_text.set_text(st)
        self.find_frame.show()
        self.replace_frame.hide()
        self.go_frame.hide()
        self.find_text.set_focus()
        self.show()

    def show_find_prev(self):
        self.show_find()
        self.perform_find_prev()

    def show_find_next(self):
        self.show_find()
        self.perform_find_next()

    def show_replace(self):
        self.find_frame.show()
        self.replace_frame.show()
        self.go_frame.hide()
        self.show()

    def show_go(self):
        self.find_frame.hide()
        self.replace_frame.hide()
        self.go_frame.show()
        self.go_text.set_alignment(9)
        self.go_text.set_text("")
        self.go_text.set_focus()
        self.show()

    def set_find_text(self, text=""):
        self.find_text.set_text(text)
        self.find_text.set_focus()

    def show(self):
        self.set_geometry()
        return super().show()

    def set_geometry(self):
        parent = self.q2code
        rect = parent.rect()
        self.setFixedWidth(400 if rect.width() > 400 else int(rect.width() / 2))
        pos = rect.topLeft()
        pos.setX(rect.width() - self.width())
        pos = parent.mapToGlobal(pos)
        self.move(pos)
