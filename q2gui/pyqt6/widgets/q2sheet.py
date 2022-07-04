import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()

from PyQt6.QtWidgets import QTableWidget, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette


from q2gui.pyqt6.q2widget import Q2Widget
from q2gui.pyqt6.widgets.q2label import q2label

from q2gui.q2utils import int_


class q2sheet(QTableWidget, Q2Widget):
    def __init__(self, meta):
        # super().__init__({"label": meta.get("label", "")})
        super().__init__(meta)
        self.column_headers = []
        self.row_headers = []
        # print()
        self.selection_background_color = "yellow"
        self.selection_background_color = self.palette().color(QPalette.ColorRole.Highlight).toRgb().name()
        self.horizontalHeader().setMinimumSectionSize(0)
        self.verticalHeader().setMinimumSectionSize(0)
        self.auto_expand = False
        self.setEditTriggers(self.EditTrigger.NoEditTriggers)
        self.spaned_cells = []

        self.sheet_styles = {}
        self.cell_styles = {}

        if self.meta.get("when"):
            self.itemSelectionChanged.connect(self.meta.get("when"))
        if self.meta.get("valid"):
            self.itemSelectionChanged.connect(self.meta.get("valid"))

    def mousePressEvent(self, event):
        rez = super().mousePressEvent(event)
        if self.meta.get("when"):
            self.meta.get("when")()
        return rez

    def focusInEvent(self, event):
        rez = super().focusInEvent(event)
        if event.reason() not in (Qt.FocusReason.PopupFocusReason,):
            x = self.currentIndex()
            if x.isValid():
                self.setCurrentCell(x.row(), x.column())
            else:
                self.setCurrentCell(0, 0)
        if self.meta.get("when"):
            self.meta.get("when")()
        return rez

    def focusOutEvent(self, event):
        if self.meta.get("valid"):
            if self.meta.get("valid")() is False:
                self.setFocus()
                return
        rez = super().focusOutEvent(event)
        return rez

    def mouseDoubleClickEvent(self, e):
        if self.meta.get("form"):
            self.meta.get("form").grid_double_clicked()
        return super().mouseDoubleClickEvent(e)

    def keyPressEvent(self, ev):
        if ev.key() in [Qt.Key.Key_Enter, Qt.Key.Key_Return] and self.meta.get("eat_enter"):
            if self.meta.get("form"):
                if self.meta.get("dblclick"):
                    self.meta.get("dblclick")()
                else:
                    self.meta.get("form").grid_double_clicked()
        else:
            super().keyPressEvent(ev)

    def set_auto_expand(self, mode=True):
        self.auto_expand = mode

    def expand(self):
        if self.auto_expand:
            self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum))
            height = self.horizontalHeader().height() + 0
            for x in range(self.rowCount()):
                height += self.rowHeight(x)
            self.setFixedHeight(height)

            width = self.verticalHeader().width() + 0
            for x in range(self.columnCount()):
                width += self.columnWidth(x)
            self.setFixedWidth(width)
        else:
            self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
            self.setMinimumWidth(0)
            self.setMinimumHeight(0)

    def set_row_count(self, row=2):
        self.setRowCount(row)
        self.expand()

    def set_column_count(self, column=2):
        self.setColumnCount(column)
        self.expand()

    def set_row_column_count(self, row=2, column=2):
        self.set_row_count(row)
        self.set_column_count(column)
        self.expand()

    def set_row_header_size(self, size):
        self.verticalHeader().setFixedWidth(size)
        self.expand()

    def set_column_headers(self, headers_list=[]):
        self.column_headers = headers_list
        self.setHorizontalHeaderLabels(self.column_headers)
        self.expand()

    def set_row_headers(self, headers_list=[]):
        self.row_headers = headers_list
        self.setVerticalHeaderLabels(self.row_headers)
        self.expand()

    def set_column_header(self, column=0, header=""):
        if column >= self.columnCount():
            return

        if not column < len(self.column_headers):
            for x in range(len(self.column_headers), self.columnCount()):
                self.column_headers.append("")
        self.column_headers[column] = header
        self.set_column_headers(self.column_headers)
        self.expand()

    def set_row_header(self, row=0, header=""):
        if row >= self.rowCount():
            return
        if not row < len(self.row_headers):
            for x in range(len(self.row_headers) - 1, self.rowCount()):
                self.row_headers.append("")
        self.row_headers[row] = header
        self.set_row_headers(self.row_headers)
        self.expand()

    def hide_column_headers(self):
        self.horizontalHeader().hide()
        self.expand()

    def show_column_headers(self):
        self.horizontalHeader().show()
        self.expand()

    def hide_row_headers(self):
        self.verticalHeader().hide()
        self.expand()

    def show_row_headers(self):
        self.verticalHeader().show()
        self.expand()

    def set_column_size(self, width=[], column=None):
        if isinstance(width, list):
            for column, size in enumerate(width):
                self.set_column_size(size, column)
        elif isinstance(width, int) and column is None:
            for x in range(self.columnCount()):
                self.set_column_size(width, x)
        else:
            self.setColumnWidth(column, width)
        self.expand()

    def get_row_size(self, row=None):
        return self.rowHeight(row)

    def set_row_size(self, heights=[], row=None):
        if isinstance(heights, list):
            for row, size in enumerate(heights):
                self.set_row_size(size, row)
        elif isinstance(heights, int) and row is None:
            for x in range(self.rowCount()):
                self.set_row_size(heights, x)
        else:
            self.setRowHeight(row, int(heights))
        self.expand()

    def clear_selection(self):
        self.clearSelection()

    def get_selection(self):
        return [(x.row(), x.column()) for x in self.selectedIndexes()]

    def clear_spans(self):
        self.spaned_cells = []
        self.clearSpans()
        self.updateGeometries()

    def set_span(self, row, column, row_span, column_span):
        self.setSpan(row, column, row_span, column_span)
        for sr in range(row, row + row_span):
            for sc in range(column, column + column_span):
                if sr != row or sc != column:
                    self.spaned_cells.append((sr, sc))
                    # self.get_cell_widget(sr, sc).setVisible(False)
                    self.removeCellWidget(sr, sc)
        self.expand()
        self.updateGeometries()

    def get_cell_text(self, row=None, column=None):
        rez = []
        if row is None and column is None:
            row = 0
        if row is not None and column is None:
            for column in range(self.columnCount()):
                rez.append(self.get_cell_text(row, column))
        elif row is None and column is not None:
            for row in range(self.rowCount()):
                rez.append(self.get_cell_text(row, column))
        else:
            row = int_(row)
            column = int_(column)
            rez = self.get_cell_widget(row, column).get_text()
        return rez

    def get_cell_style_sheet(self, row=None, column=None):
        rez = []
        if row is None and column is None:
            row = 0
        if row is not None and column is None:
            for column in range(self.columnCount()):
                rez.append(self.get_cell_style(row, column))
        elif row is None and column is not None:
            for row in range(self.rowCount()):
                rez.append(self.get_cell_style(row, column))
        else:
            row = int_(row)
            column = int_(column)
            rez = self.get_cell_widget(row, column).get_style_sheet()
        return rez

    def get_text(self):
        return self.get_cell_widget(self.current_row(), self.current_column()).get_text()

    def set_text(self, text):
        self.set_cell_text(text, self.current_row(), self.current_column())

    def set_cell_text(self, text="", row=None, column=None):
        if isinstance(text, list):
            if row is None and column is None:
                row = 0
            if row is not None:
                for x in range(self.columnCount()):
                    if x < len(text):
                        self.set_cell_text(text[x], row, x)
            else:
                for x in range(self.rowCount()):
                    if x < len(text):
                        self.set_cell_text(text[x], x, column)
        else:
            row = int_(row)
            column = int_(column)
            cell_widget = self.get_cell_widget(row, column)
            cell_widget.setText(text)

    def set_cell_style_sheet(self, style_text="", row=None, column=None):
        if row is None and column is None:
            row = 0
        if row is not None and column is None:
            for x in range(self.columnCount()):
                if isinstance(style_text, dict):
                    if x < len(style_text):
                        self.set_cell_style_sheet(style_text[x], row, x)
                else:
                    self.set_cell_style_sheet(style_text, row, x)
        elif row is None and column is not None:
            for x in range(self.rowCount()):
                if isinstance(style_text, dict):
                    if x < len(style_text):
                        self.set_cell_style_sheet(style_text[x], x, column)
                else:
                    self.set_cell_style_sheet(style_text, x, column)
        else:  # row and column - set style
            row = int_(row)
            column = int_(column)
            cell_widget = self.get_cell_widget(row, column)
            if (row, column) in self.spaned_cells:
                cell_widget.set_style_sheet("")
                cell_widget.setVisible(False)
                # print(row, column)
                return
            # else:
            #     cell_widget.setVisible(True)
            cell_key = f"{row},{column}"
            if style_text is None and cell_key not in self.cell_styles:
                style_text = cell_widget.get_style_sheet()
            if (row, column) in [(x.row(), x.column()) for x in self.selectedIndexes()]:
                if isinstance(style_text, dict):
                    style_text["background-color"] = self.selection_background_color
                elif isinstance(style_text, str):
                    style_text += f";background-color:{self.selection_background_color};"
                else:  # None - using self.cell_styles
                    style_text = dict(self.sheet_styles)
                    style_text.update(self.cell_styles.get(cell_key, {}))
                    style_text["background-color"] = self.selection_background_color
            else:
                if isinstance(style_text, str):
                    style_text = style_text.replace(f"background-color:{self.selection_background_color}", "")
                elif style_text is None:
                    style_text = dict(self.sheet_styles)
                    style_text.update(self.cell_styles.get(cell_key, {}))

            cell_widget.set_style_sheet(style_text)

    def selectionChanged(self, selected, deselected):
        rez = super().selectionChanged(selected, deselected)
        for x in deselected.indexes():
            # st = self.get_cell_widget(x.row(), x.column()).get_style_sheet()
            self.set_cell_style_sheet(None, x.row(), x.column())

        for x in selected.indexes():
            # st = self.get_cell_widget(x.row(), x.column()).get_style_sheet()
            self.set_cell_style_sheet(None, x.row(), x.column())
        return rez

    def get_cell_widget(self, row, column):
        cell_widget = self.cellWidget(row, column)
        if cell_widget is None:
            cell_widget = q2label({"label": "", "dblclick": self.meta.get("dblclick")})
            cell_widget.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
            cell_widget.set_maximum_height(9999)
            self.setCellWidget(row, column, cell_widget)
        return cell_widget

    def get_current_widget(self):
        return self.get_cell_widget(self.currentRow(), self.currentColumn())

    def current_row(self):
        return self.currentRow()

    def current_column(self):
        return self.currentColumn()

    def set_current_cell(self, row, column):
        self.setCurrentCell(row, column)

    def insert_row(self, after_row=None):
        self.setRowCount(self.rowCount() + 1)
        for row in range(self.rowCount() - 1, after_row, -1):
            for col in range(self.columnCount()):
                self.set_cell_text(self.get_cell_text(row - 1, col), row, col)
                self.set_cell_style_sheet(self.get_cell_style_sheet(row - 1, col), row, col)
                if row == after_row + 1:
                    self.set_cell_text("", row - 1, col)
                    self.set_cell_style_sheet("", row - 1, col)

    def move_row(self, after_row):
        for col in range(self.columnCount()):
            text = self.get_cell_text(after_row, col)
            style = self.get_cell_style_sheet(after_row, col)
            self.set_cell_text(self.get_cell_text(after_row + 1, col), after_row, col)
            self.set_cell_style_sheet(self.get_cell_style_sheet(after_row + 1, col), after_row, col)
            self.set_cell_text(text, after_row + 1, col)
            self.set_cell_style_sheet(style, after_row + 1, col)

    def remove_row(self, remove_row):
        for row in range(remove_row, self.rowCount()):
            for col in range(self.columnCount()):
                self.set_cell_text(self.get_cell_text(row + 1, col), row, col)
                self.set_cell_style_sheet(self.get_cell_style_sheet(row + 1, col), row, col)
        self.setRowCount(self.rowCount() - 1)

    def insert_column(self, after_column=None):
        self.setColumnCount(self.columnCount() + 1)
        for col in range(self.columnCount() - 1, after_column, -1):
            for row in range(self.rowCount()):
                self.set_cell_text(self.get_cell_text(row, col - 1), row, col)
                self.set_cell_style_sheet(self.get_cell_style_sheet(row, col - 1), row, col)
                if col == after_column + 1:
                    self.set_cell_text("", row, col - 1)
                    self.set_cell_style_sheet("", row, col - 1)

    def remove_column(self, remove_column):
        for col in range(remove_column, self.columnCount()):
            for row in range(self.rowCount()):
                self.set_cell_text(self.get_cell_text(row, col + 1), row, col)
                self.set_cell_style_sheet(self.get_cell_style_sheet(row, col + 1), row, col)
        self.setColumnCount(self.columnCount() - 1)

    def move_column(self, after_column):
        for row in range(self.rowCount()):
            text = self.get_cell_text(row, after_column)
            style = self.get_cell_style_sheet(row, after_column)
            self.set_cell_text(self.get_cell_text(row, after_column + 1), row, after_column)
            self.set_cell_style_sheet(self.get_cell_style_sheet(row, after_column + 1), row, after_column)
            self.set_cell_text(text, row, after_column + 1)
            self.set_cell_style_sheet(style, row, after_column + 1)
