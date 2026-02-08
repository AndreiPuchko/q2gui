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

import q2gui.q2app as q2app

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QToolButton

from PyQt6.Qsci import QsciScintilla, QsciLexerPython, QsciLexerSQL, QsciLexerJSON, QsciAPIs, QsciLexer
from PyQt6.QtGui import QColor, QKeyEvent, QResizeEvent, QRegularExpressionValidator
from PyQt6.QtCore import Qt, QTimer, QSize, QRegularExpression

from q2gui.pyqt6.q2widget import Q2Widget
from q2gui.q2utils import int_


def _(s):
    return s


def tr(s):
    return q2app.q2_app.i18n.tr(s)


widgets_stylesheet = """
            QWidget {
                background: #5fb0e3;
                border: 1px solid #555;
                border-radius: 6px;
            }
            QLineEdit {
                background: #3e3e3e;
                color: white;
                border: none;
                padding: 4px;
            }
            QToolButton {
                color: white;
            }
        """


class q2code(QsciScintilla, Q2Widget):
    INDIC_CURRENT = 8  # current word
    INDIC_SEL = 10  # selection

    def __init__(self, meta):
        super().__init__(meta)
        self.setUtf8(True)
        self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle)

        self.lexer: QsciLexer = None
        self.set_lexer()
        self.set_background_color()

        self.setAutoIndent(True)
        self.setIndentationGuides(True)
        self.setIndentationGuidesForegroundColor(QColor("#cccccc"))
        self.SendScintilla(self.SCI_SETTABDRAWMODE, 1)

        self.setIndentationsUseTabs(False)
        self.setBackspaceUnindents(True)
        self.setBraceMatching(QsciScintilla.BraceMatch.StrictBraceMatch)
        self.setMarginLineNumbers(1, True)
        self.setMarginWidth(1, "9999")
        self.setTabWidth(4)

        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
        self.setAutoCompletionCaseSensitivity(True)
        self.setAutoCompletionReplaceWord(True)
        self.setAutoCompletionThreshold(1)

        self.SCN_DOUBLECLICK

        # highlight current line
        self.setCaretLineVisible(True)

        self.setEdgeColor(QColor("#555555"))  # Темно-серый

        def sync_edge_with_cursor(line, col):
            indent_size = self.indentationWidth() or 4
            full_line = self.text(line)
            leading_spaces = len(full_line) - len(full_line.lstrip()) - 1
            if col < leading_spaces:
                leading_spaces = col
            visual_column = (leading_spaces // indent_size) * indent_size
            if visual_column:
                self.setEdgeMode(QsciScintilla.EdgeMode.EdgeLine)
                self.setEdgeColumn(visual_column)
            else:
                self.setEdgeMode(QsciScintilla.EdgeMode.EdgeNone)

        self.cursorPositionChanged.connect(sync_edge_with_cursor)

        if self.meta.get("valid"):
            self.textChanged.connect(self.valid)
        self.gotoline_widget = GoToLineWidget(self)
        self.find_widget = FindWidget(self)
        self.set_custom_autocompletition_list()
        self.define_highlights()

        self.highlight_timer = QTimer()
        self.highlight_timer.setSingleShot(True)
        self.highlight_timer.timeout.connect(self.highlight)

        self.cursorPositionChanged.connect(lambda: self.highlight_timer.start(300))
        self.selectionChanged.connect(lambda: self.highlight_timer.start(300))

    def define_highlights(self):
        self.searchIndicator = QsciScintilla.INDIC_CONTAINER
        self.SendScintilla(QsciScintilla.SCI_INDICSETSTYLE, self.searchIndicator, QsciScintilla.INDIC_BOX)
        self.SendScintilla(QsciScintilla.SCI_INDICSETFORE, self.searchIndicator, QColor("red"))

        self.SendScintilla(QsciScintilla.SCI_INDICSETSTYLE, self.INDIC_SEL, QsciScintilla.INDIC_ROUNDBOX)
        self.SendScintilla(QsciScintilla.SCI_INDICSETFORE, self.INDIC_SEL, 0x0000FF)
        self.SendScintilla(QsciScintilla.SCI_INDICSETALPHA, self.INDIC_SEL, 150)
        self.SendScintilla(QsciScintilla.SCI_INDICSETUNDER, self.INDIC_SEL, True)

    def highlight(self):
        if self.isListActive():
            return
        self.highlight_current_word()
        self.highlight_current_selection()

    def highlight_current_word(self):
        self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, self.INDIC_CURRENT)
        self.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE, 0, self.length())
        current_word = self.wordAtLineIndex(*self.getCursorPosition())
        if not current_word or len(current_word) <= 1:
            return
        search_bytes = current_word.encode("utf-8")
        search_len = len(search_bytes)  # Длина в БАЙТАХ
        pos = 0
        doc_len = self.SendScintilla(QsciScintilla.SCI_GETLENGTH)
        self.SendScintilla(QsciScintilla.SCI_SETSEARCHFLAGS, QsciScintilla.SCFIND_WHOLEWORD)
        while pos < doc_len:
            self.SendScintilla(QsciScintilla.SCI_SETTARGETSTART, pos)
            self.SendScintilla(QsciScintilla.SCI_SETTARGETEND, doc_len)
            found_pos = self.SendScintilla(QsciScintilla.SCI_SEARCHINTARGET, search_len, search_bytes)
            if found_pos == -1:
                break
            match_end = self.SendScintilla(QsciScintilla.SCI_GETTARGETEND)
            self.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, found_pos, match_end - found_pos)
            if pos == match_end:
                pos += 1
            else:
                pos = match_end

    def highlight_current_selection(self):
        self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, self.INDIC_SEL)
        self.SendScintilla(
            QsciScintilla.SCI_INDICATORCLEARRANGE, 0, self.SendScintilla(QsciScintilla.SCI_GETLENGTH)
        )
        if not self.hasSelectedText():
            return
        sel = self.selectedText()
        if len(sel) < 2:
            return
        search_bytes = sel.encode("utf-8")
        search_len = len(search_bytes)
        if search_len == 0 or sel.isspace():
            return
        self.SendScintilla(QsciScintilla.SCI_SETSEARCHFLAGS, 0)
        current_pos = 0
        doc_len = self.SendScintilla(QsciScintilla.SCI_GETLENGTH)
        while current_pos < doc_len:
            self.SendScintilla(QsciScintilla.SCI_SETTARGETSTART, current_pos)
            self.SendScintilla(QsciScintilla.SCI_SETTARGETEND, doc_len)
            found_pos = self.SendScintilla(QsciScintilla.SCI_SEARCHINTARGET, search_len, search_bytes)
            if found_pos == -1:
                break
            match_end = self.SendScintilla(QsciScintilla.SCI_GETTARGETEND)
            self.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, found_pos, match_end - found_pos)
            current_pos = match_end
            if found_pos == match_end:
                current_pos += 1

    def set_lexer(self, lexer=""):
        test_string_color = QColor("#0C6102")
        if lexer == "":
            lexer = self.meta["control"]
        if "sql" in lexer:
            self.lexer = QsciLexerSQL()
            self.lexer.setColor(test_string_color, QsciLexerSQL.SingleQuotedString)
            self.lexer.setColor(test_string_color, QsciLexerSQL.DoubleQuotedString)
        elif "json" in lexer:
            self.lexer = QsciLexerJSON()
        else:
            self.lexer = QsciLexerPython()
            self.lexer.setColor(QColor("#023A55"), QsciLexerPython.DoubleQuotedFString)
            self.lexer.setColor(QColor("#023A55"), QsciLexerPython.SingleQuotedFString)
            self.lexer.setColor(test_string_color, QsciLexerPython.DoubleQuotedString)
            self.lexer.setColor(test_string_color, QsciLexerPython.SingleQuotedString)

        if self.lexer:
            self.setLexer(self.lexer)

    def set_custom_autocompletition_list(self, custom_autocompletions_list=[]):
        custom_autocompletions_list = self.meta["form"].q2_app.get_autocompletition_list()
        self.__api = QsciAPIs(self.lexer)
        for ac in custom_autocompletions_list:
            self.__api.add(ac)
        self.__api.prepare()

    def set_background_color(self, red=150, green=200, blue=230):
        d_color = self.meta.get("q2_app").q2style.get_style("background_disabled")
        self.set_style_sheet("QFrame:disabled {background:%s}" % d_color)
        self.setMatchedBraceForegroundColor(QColor("red"))
        self.lexer.setDefaultPaper(QColor(red, green, blue))
        self.lexer.setPaper(QColor(red, green, blue))
        self.setMarginsForegroundColor(QColor("black"))
        self.setMarginsBackgroundColor(QColor("gray"))

    def resizeEvent(self, e: QResizeEvent) -> None:
        super().resizeEvent(e)
        self.find_widget.set_widget_position()
        self.gotoline_widget.set_widget_position()

    def focusInEvent(self, ev):
        super().focusInEvent(ev)
        self.create_context_menu()

    def focusOutEvent(self, ev):
        self.clear_actions()
        super().focusInEvent(ev)

    def clear_actions(self):
        for x in self.actions():
            self.removeAction(x)

    def addAction(self, text, worker, shortcuts):
        _action = self.context_menu.addAction(text)
        _action.triggered.connect(worker)
        _action.setShortcuts(shortcuts)

    def create_context_menu(self):
        self.context_menu = self.createStandardContextMenu()
        self.context_menu.addSeparator()

        self.addAction(_("Find"), self.show_find, ["Ctrl+F"])
        self.addAction(_("Find next"), self.find_next_, ["F3"])
        self.addAction(_("Find previous"), self.find_prev_, ["Shift+F3"])

        self.addAction(_("Replace"), self.find_widget.show_replace, ["Ctrl+H"])

        self.context_menu.addSeparator()

        self.addAction(
            _("Move selection up"),
            self.perform_move_up,
            [
                "Ctrl+Alt+Up",
                "Ctrl+Shift+Up",
            ],
        )
        self.addAction(_("Move selection down"), self.perform_move_down, ["Ctrl+Alt+Down", "Ctrl+Shift+Down"])

        self.context_menu.addSeparator()

        self.addAction(_("Go to line"), self.gotoline_widget.focus, ["Ctrl+G"])

        self.context_menu.addSeparator()

        self.addAction(_("Fold/Unfold"), self.perform_folding, ["Alt+Up", "Alt+Down"])
        self.addAction(_("Fold/Unfold All"), self.foldAll, ["Alt+Left", "Alt+Right"])

        self.context_menu.addSeparator()

        self.addAction(_("Comment/uncomment line(s)"), self.perform_comment, ["Ctrl+3"])

        self.addAction(_("Autocomplete"), self.autoCompleteFromAll, ["Ctrl+Space"])

        self.addActions(self.context_menu.actions())
        for x in self.context_menu.actions():
            if x.isEnabled():
                x.setVisible(True)
            else:
                x.setVisible(False)

    def show_find(self):
        self.find_widget.show_find(self.selectedText())

    def find_next_(self):
        self.find_widget._next()
        self.setFocus()

    def find_prev_(self):
        self.find_widget._prev()
        self.setFocus()

    def perform_move_down(self):
        self.SendScintilla(QsciScintilla.SCI_MOVESELECTEDLINESDOWN)

    def perform_move_up(self):
        self.SendScintilla(QsciScintilla.SCI_MOVESELECTEDLINESUP)

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

    def goto_line(self, line_num=0):
        line_count = self.lines()
        line_num = max(1, min(line_num, line_count))

        self.setCursorPosition(int_(line_num) - 1, 0)
        self.set_focus()
        self.ensureLineVisible(self.getCursorPosition()[0])

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

    def find_next(self, text):
        return self._find(text, True)

    def getSelectedText(self):
        if self.hasSelectedText():
            line1, pos1, line2, pos2 = self.getSelection()
            for x in range(line1, line2 + 1):
                selected_lines.append(x)

    def find_prev(self, text):
        line1, index1, line2, index2 = self.getSelection()
        self.setCursorPosition(line1, index1)
        return self._find(text, False)

    def _find(self, text, direction):
        return self.findFirst(text, False, False, False, False, direction)

    def replace_one(self, text1, text2):
        if text1 == "":
            return
        if self.selectedText() != text1:
            return self.find_next(text1)
        self.replace(text2)
        self.find_next(text1)

    def keyPressEvent(self, e):
        key = e.key()
        if key == Qt.Key.Key_Escape and self.isVisible():
            self.setFocus()
            self.find_widget.hide()
            self.gotoline_widget.hide()
            return
        super().keyPressEvent(e)


class FindWidget(QWidget):
    def __init__(self, parent: q2code = None):
        super().__init__(parent)

        self.setWindowFlags(Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setObjectName(_("FindWidget"))

        self.last_find_direction = "down"

        # --- find ---
        self.find_edit = QLineEdit()
        self.find_edit.setPlaceholderText(_("Find"))

        btn_prev = QToolButton()
        btn_prev.setText("↑")

        btn_next = QToolButton()
        btn_next.setText("↓")

        btn_close = QToolButton()
        btn_close.setText("✕")

        # --- replace ---
        self.replace_edit = QLineEdit()
        self.replace_edit.setPlaceholderText(_("Replace"))

        btn_replace = QToolButton()
        btn_replace.setText("↵")

        btn_replace_all = QToolButton()
        # btn_replace_all.setText("↵ ↵")

        # --- layouts ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)

        find_row = QHBoxLayout()
        find_row.setSpacing(2)
        find_row.addWidget(self.find_edit)
        find_row.addWidget(btn_prev)
        find_row.addWidget(btn_next)
        find_row.addWidget(btn_close)

        replace_row = QHBoxLayout()
        replace_row.setSpacing(2)
        replace_row.addWidget(self.replace_edit)
        replace_row.addWidget(btn_replace)
        # replace_row.addWidget(btn_replace_all)

        self.find_container = QWidget()
        self.find_container.setLayout(find_row)
        self.find_container.hide()

        self.replace_container = QWidget()
        self.replace_container.setLayout(replace_row)
        self.replace_container.hide()

        main_layout.addWidget(self.find_container)
        main_layout.addWidget(self.replace_container)

        # --- signals ---
        btn_next.clicked.connect(self._next)
        btn_prev.clicked.connect(self._prev)
        btn_close.clicked.connect(self.hide)

        btn_replace.clicked.connect(self._replace_one)
        # btn_replace_all.clicked.connect(self._replace_all)

        # --- style ---
        self.setStyleSheet(widgets_stylesheet)
        self.hide()

    # --- mode control -------------------------------------------------

    def keyPressEvent(self, e: QKeyEvent) -> None:
        key = e.key()
        mods = e.modifiers()
        if sum(
            [
                (key in [Qt.Key.Key_Return, Qt.Key.Key_Enter] and mods == Qt.KeyboardModifier.NoModifier)
                and self.find_edit.hasFocus(),
                (key in [Qt.Key.Key_F3] and mods == Qt.KeyboardModifier.NoModifier),
                (key in [Qt.Key.Key_Down]),
            ]
        ):
            self._next()
            return
        elif sum(
            [
                (key in [Qt.Key.Key_Return, Qt.Key.Key_Enter] and mods == Qt.KeyboardModifier.ShiftModifier),
                (key in [Qt.Key.Key_F3] and mods == Qt.KeyboardModifier.ShiftModifier),
                (key in [Qt.Key.Key_Up]),
            ]
        ):
            self._prev()
            return
        elif key == Qt.Key.Key_H and mods == Qt.KeyboardModifier.ControlModifier:
            self.show_replace()
        elif (
            key in [Qt.Key.Key_Return, Qt.Key.Key_Enter]
            and mods == Qt.KeyboardModifier.NoModifier
            and self.replace_edit.hasFocus()
        ):
            self._replace_one()
            return

        return super().keyPressEvent(e)

    def _next(self):
        self.show_find()
        self.parent().find_next(self.find_edit.text())
        self.last_find_direction = "down"

    def _prev(self):
        self.show_find()
        self.parent().find_prev(self.find_edit.text())
        self.last_find_direction = "up"

    def _replace_one(self):
        self.parent().replace_one(self.find_edit.text(), self.replace_edit.text())

    def _replace_all(self):
        pass

    def set_widget_position(self):
        margin = 1
        vp = self.parent().viewport()
        self.adjustSize()

        x = vp.width() - self.width() - margin
        y = margin

        self.move(
            vp.mapToParent(vp.rect().topLeft()).x() + x,
            vp.mapToParent(vp.rect().topLeft()).y() + y,
        )

    def show_find(self, text=""):
        if self.find_container.isVisible():
            self.focus()
            return
        if text:
            self.find_edit.setText(text)
        self.find_container.show()
        self.replace_container.hide()
        self.focus()

    def show_replace(self):
        self.find_container.show()
        self.replace_container.show()
        self.focus()

    def focus(self):
        self.show()
        self.set_widget_position()
        self.raise_()
        self.find_edit.setFocus()
        self.find_edit.selectAll()


class GoToLineWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setObjectName("GoToLineWidget")

        # --- input ---
        self.line_edit = QLineEdit()
        regex = QRegularExpression("^[0-9]*$")
        validator = QRegularExpressionValidator(regex)

        self.line_edit.setValidator(validator)
        self.line_edit.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.line_edit.setPlaceholderText(_("Go to line"))

        # --- buttons ---
        btn_go = QToolButton()
        btn_go.setText(_("Go"))

        btn_close = QToolButton()
        btn_close.setText("✕")

        # --- layout ---
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        layout.addWidget(self.line_edit)
        layout.addWidget(btn_go)
        layout.addWidget(btn_close)

        # --- signals ---
        btn_go.clicked.connect(self.goto_line)
        btn_close.clicked.connect(self.hide)

        # --- style ---
        self.setStyleSheet(widgets_stylesheet)
        self.hide()

    # -------------------------------
    def goto_line(self):
        try:
            line_num = int_(self.line_edit.text())
        except ValueError:
            return  # invalid input, ignore
        self.parent().goto_line(line_num)
        self.hide()

    # -------------------------------
    def set_widget_position(self):
        margin_top = 2
        vp = self.parent().viewport()
        self.adjustSize()

        # X — по центру viewport по ширине
        x = (vp.width() - self.width()) // 2

        # Y — сверху с небольшим margin
        y = margin_top

        # map viewport -> координаты родителя
        self.move(vp.mapToParent(vp.rect().topLeft()).x() + x, vp.mapToParent(vp.rect().topLeft()).y() + y)

    def focus(self):
        self.show()
        self.set_widget_position()
        self.raise_()
        self.line_edit.setFocus()
        self.line_edit.selectAll()

    def keyPressEvent(self, e: QKeyEvent) -> None:
        key = e.key()
        if key in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            self.goto_line()
            return
        return super().keyPressEvent(e)
