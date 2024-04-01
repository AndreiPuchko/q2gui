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


from PyQt6.QtWidgets import (
    QTableWidget,
    QFrame,
    QTableView,
    QStyledItemDelegate,
    QAbstractItemView,
    QSizePolicy,
    QVBoxLayout,
)
from PyQt6.QtGui import QCloseEvent, QKeyEvent, QPalette, QPainter, QFontMetrics, QBrush

from PyQt6.QtCore import (
    Qt,
    QAbstractTableModel,
    QVariant,
    QItemSelectionModel,
    QSortFilterProxyModel,
)

from q2gui.pyqt6.q2window import q2_align
from q2gui.q2utils import int_
from q2gui.q2model import Q2Model
from q2gui.pyqt6.widgets.q2lookup import q2lookup
from q2gui.pyqt6.widgets.q2button import q2button
from q2gui.pyqt6.widgets.q2line import q2line
from q2gui.pyqt6.widgets.q2check import q2check
from q2gui.pyqt6.widgets.q2frame import q2frame


sort_ascend_char = "▲"
sort_decend_char = "▼"
filtered_char = "☑"


class q2Delegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option, index):
        if self.parent().currentIndex().column() == index.column():
            color = option.palette.color(QPalette.ColorRole.AlternateBase).darker(900)
            color.setAlpha(int(color.alpha() / 5))
            painter.fillRect(option.rect, color)
        super().paint(painter, option, index)


class q2grid(QTableView):
    class Q2TableModel(QAbstractTableModel):
        def __init__(self, q2_model):
            super().__init__(parent=None)
            self.q2_model: Q2Model = q2_model
            self._q2_model_refresh = self.q2_model.refresh
            self.q2_model.refresh = self.refresh

        def rowCount(self, parent=None):
            return self.q2_model.row_count()

        def columnCount(self, parent=None):
            return self.q2_model.column_count()

        def refresh(self):
            self.beginResetModel()
            self.endResetModel()
            self._q2_model_refresh()
            self.apply_col_filter()

        def data(self, index, role=Qt.ItemDataRole.DisplayRole):
            control = self.q2_model.meta[index.column()].get("control")
            if role == Qt.ItemDataRole.DisplayRole:
                if control == "check":
                    return QVariant()
                else:
                    return QVariant(self.q2_model.data(index.row(), index.column()))
            elif role == Qt.ItemDataRole.TextAlignmentRole:
                return QVariant(q2_align[str(self.q2_model.alignment(index.column()))])
            elif role == Qt.ItemDataRole.CheckStateRole:
                if control == "check":
                    if self.q2_model.data(index.row(), index.column()):
                        return Qt.CheckState.Checked
                    else:
                        return Qt.CheckState.Unchecked
            else:
                return QVariant()

        def headerData(self, col, orientation, role=Qt.ItemDataRole.DisplayRole):
            if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
                sort_char = ""
                if self.q2_model.columns[col] in self.q2_model.order_text:
                    if "desc" in self.q2_model.order_text:
                        sort_char = sort_decend_char
                    else:
                        sort_char = sort_ascend_char
                if col in self.q2_model.filtered_columns:
                    sort_char += f" {filtered_char} "
                return sort_char + self.q2_model.headers[col]
            # elif orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.BackgroundRole:
            #     return QBrush(Qt.GlobalColor.red)
            elif orientation == Qt.Orientation.Vertical and role == Qt.ItemDataRole.DisplayRole:
                if col in self.q2_model.hidden_rows and not self.q2grid.isRowHidden(col):
                    self.q2grid.setRowHidden(col, True)
                return QVariant("")
            else:
                return QVariant()

        def flags(self, index):
            control = self.q2_model.meta[index.column()].get("control")
            flags = super().flags(index)
            if control == "check":
                flags |= Qt.ItemFlag.ItemIsUserCheckable
            return flags

        def apply_col_filter(self, filter_values=None, column=None):
            for row in range(self.rowCount()):
                self.q2grid.setRowHidden(row, False)
            self.q2_model.hidden_rows = []
            if filter_values is not None:
                self.q2_model.columns_filter_values[column] = filter_values
                if self.q2_model.columns_filter_values[column] == []:
                    del self.q2_model.columns_filter_values[column]
                self.q2_model.filtered_columns = list(self.q2_model.columns_filter_values.keys())
            for row in range(self.rowCount()):
                if row in self.q2_model.hidden_rows:
                    continue
                for col, values in self.q2_model.columns_filter_values.items():
                    if self.q2_model.data(row, col) not in values:
                        self.q2_model.hidden_rows.append(row)
                        # self.q2grid.setRowHidden(row, True)
                        break

    def __init__(self, meta):
        super().__init__()
        self.meta = meta

        self.q2_form = self.meta.get("form")
        self.q2_model = self.q2_form.model

        self.setItemDelegate(q2Delegate(self))
        self.setTabKeyNavigation(False)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.horizontalHeader().setSectionsMovable(True)
        self.horizontalHeader().setDefaultAlignment(q2_align["7"])
        self.horizontalHeader().sectionClicked.connect(self.q2_form.grid_header_clicked)
        h = self.fontMetrics().height()
        self.verticalHeader().setMinimumSectionSize(h + h // 4)
        self.verticalHeader().setDefaultSectionSize(self.fontMetrics().height())

        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.doubleClicked.connect(self.q2_form.grid_double_clicked)
        self.setModel(self.Q2TableModel(self.q2_form.model))
        self.model().q2grid = self
        self.horizontalHeader().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.horizontalHeader().customContextMenuRequested.connect(self.activate_header_menu)

    def activate_header_menu(self, pos):
        self.set_index(self.currentIndex().row(), self.horizontalHeader().logicalIndexAt(pos))
        self.meta["q2_app"].process_events()
        if self.row_count() > 10000:
            return
        column_manager = q2_col_manager(self)
        column_manager.show()

    def apply_col_filter(self, filter_values):
        self.model().apply_col_filter(filter_values, self.currentIndex().column())
        self.set_index(0)

    def currentChanged(self, current, previous):
        super().currentChanged(current, previous)
        self.model().dataChanged.emit(current, previous)
        self.model().dataChanged.emit(previous, current)
        self.q2_form._grid_index_changed(self.currentIndex().row(), self.currentIndex().column())

    def current_index(self):
        return self.currentIndex().row(), self.currentIndex().column()

    def set_focus(self):
        self.setFocus()

    def has_focus(self):
        return self.hasFocus()

    def is_enabled(self):
        return self.isEnabled()

    def row_count(self):
        return self.model().rowCount()

    def column_count(self):
        return self.model().columnCount()

    def set_index(self, row, column=None):
        _last_row = self.currentIndex().row()
        self.clearSelection()
        if row < 0:
            row = 0
        elif row > self.row_count() - 1:
            row = self.row_count() - 1

        if column is None:
            column = self.currentIndex().column()
        elif column < 0:
            column = 0
        elif column > self.column_count() - 1:
            column = self.column_count() - 1

        if self.model().q2_model.filtered_columns:
            if row > _last_row:
                while self.isRowHidden(row) and row < self.model().rowCount() - 1:
                    row += 1
            elif row < _last_row and row > 0:
                while self.isRowHidden(row) and row > 0:
                    row -= 1

            if row == 0:
                while self.isRowHidden(row):
                    row += 1
            elif row == self.model().rowCount() - 1:
                while self.isRowHidden(row):
                    row -= 1

        self.setCurrentIndex(self.model().index(row, column))

    def keyPressEvent(self, event):
        event.accept()
        # if ev.key() in [Qt.Key.Key_F] and ev.modifiers() == Qt.ControlModifier:
        #     self.searchText()
        # if event.key() in [Qt.Key.Key_Asterisk]:
        if (
            event.text()
            and event.key() not in (Qt.Key.Key_Escape, Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Space)
            and self.model().rowCount() >= 1
            and event.modifiers() != Qt.KeyboardModifier.ControlModifier
            and event.modifiers() != Qt.KeyboardModifier.AltModifier
        ):
            lookup_widget = q2_grid_lookup(self, event.text(), meta=self.meta)
            lookup_widget.show(self, self.currentIndex().column())
        else:
            super().keyPressEvent(event)

    def get_selected_rows(self):
        return [x.row() for x in self.selectionModel().selectedRows() if not self.isRowHidden(x.row())]

    def set_selected_rows(self, index_list):
        self.clearSelection()
        indexes = [self.model().index(row, 0) for row in index_list if not self.isRowHidden(row)]
        mode = QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows
        [self.selectionModel().select(index, mode) for index in indexes]

    def get_columns_headers(self):
        rez = {}
        hohe = self.horizontalHeader()
        for x in range(0, hohe.count()):
            # col_header = hohe.model().headerData(x, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
            col_header = self.q2_model.headers[x]
            rez[col_header] = x
        return rez

    def get_columns_settings(self):
        rez = []
        hohe = self.horizontalHeader()
        for x in range(0, hohe.count()):
            # header = hohe.model().headerData(x, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
            header = self.q2_model.headers[x]
            width = self.columnWidth(x)
            pos = hohe.visualIndex(x)
            rez.append({"name": header, "data": f"{pos}, {width}"})
        return rez

    def set_column_settings(self, col_settings):
        headers = self.get_columns_headers()
        for x, col_size in col_settings.items():
            if "," not in col_settings[x]:
                continue
            column_pos, column_width = [int_(sz) for sz in col_size.split(",")]
            self.setColumnWidth(headers.get(x), column_width)
            old_visual = self.horizontalHeader().visualIndex(int_(headers[x]))
            self.horizontalHeader().moveSection(old_visual, column_pos)
        self.set_index(0, self.horizontalHeader().logicalIndex(0))


class q2_grid_lookup(q2lookup):
    def lookup_list_selected(self):
        self.q2_grid.set_index(self.found_rows[self.lookup_list.currentRow()][0])
        self.close()

    def lookup_search(self):
        self.lookup_list.clear()
        self.found_rows = self.q2_model.lookup(self.q2_model_column, self.lookup_edit.get_text())
        for x in self.found_rows:
            self.lookup_list.addItem(f"{x[1]}")

    def show(self, q2_grid, column):
        self.q2_grid = q2_grid
        self.q2_model_column = column
        self.q2_model = q2_grid.q2_model
        super().show()
        self.lookup_edit.setCursorPosition(1)

    def set_geometry(self):
        parent = self.parent()
        rect = parent.visualRect(parent.currentIndex())
        rect.moveTop(parent.horizontalHeader().height() + 2)
        rect.moveLeft(parent.verticalHeader().width() + rect.x() + 2)
        pos = rect.topLeft()
        pos = parent.mapToGlobal(pos)
        self.setFixedWidth(parent.width() - rect.x())
        self.move(pos)


class q2_col_manager(QFrame):

    class content_view(QTableView):
        class content_view_model(QAbstractTableModel):
            def __init__(self, parent):
                super().__init__(parent)
                # self._content = set()
                q2grid = self.parent().parent().q2grid
                column = self.parent().parent()._column
                self._content = q2grid.model().q2_model.unique_column_values(column)

            def rowCount(self, parent=None):
                return len(self._content)

            def columnCount(self, parent=None):
                return 1

            def data(self, index, role=Qt.ItemDataRole.DisplayRole):
                if role == Qt.ItemDataRole.DisplayRole:
                    return self._content[index.row()]["v"]
                elif role == Qt.ItemDataRole.TextAlignmentRole:
                    return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                elif role == Qt.ItemDataRole.CheckStateRole:
                    if self._content[index.row()].get("c", True):
                        return Qt.CheckState.Checked
                    else:
                        return Qt.CheckState.Unchecked

            def toogle_check(self, index):
                self._content[index.row()]["c"] = not self._content[index.row()].get("c", True)
                self.dataChanged.emit(index, index)

        def __init__(self, parent):
            super().__init__(parent)
            self.setShowGrid(False)
            self.setTabKeyNavigation(False)
            self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
            self._model = q2_col_manager.content_view.content_view_model(self)
            self.proxy = QSortFilterProxyModel()
            self.proxy.setSourceModel(self._model)
            self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            self.setModel(self.proxy)

            self.horizontalHeader().hide()
            self.verticalHeader().hide()

            self.setHorizontalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
            self.verticalHeader().setDefaultSectionSize(QFontMetrics(self.font()).height())
            self.resizeColumnsToContents()
            self.clicked.connect(self.on_click)

        def on_search_changed(self, text):
            self.proxy.setFilterWildcard(text)
            # self.proxy.setFilterRegularExpression(text)

        def get_checked(self):
            rez = []
            for x in range(self.model().rowCount()):
                row = self.proxy.mapToSource(self.proxy.index(x, 0)).row()
                if self._model._content[row].get("c", True):
                    rez.append(self._model._content[row]["v"])
            return rez

        def check_all(self, state):
            for x in range(self.model().rowCount()):
                self._model._content[self.proxy.mapToSource(self.proxy.index(x, 0)).row()]["c"] = state
            self._model.beginResetModel()
            self._model.endResetModel()

        def keyPressEvent(self, event: QKeyEvent):
            if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Space):
                self.on_click(self.currentIndex())
                self.setCurrentIndex(self.model().index(self.currentIndex().row() + 1, 0))
            return super().keyPressEvent(event)

        def on_click(self, index):
            self._model.toogle_check(self.proxy.mapToSource(index))

    def __init__(self, parent):
        parent.setDisabled(True)
        super().__init__(parent, Qt.WindowType.Popup)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.filter_values = None
        self.q2grid = parent
        self._column = parent.currentIndex().column()
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setObjectName("col_manager")
        self.setStyleSheet("QFrame#col_manager {border: 1px solid palette(Mid);border-radius: 0.25ex;}")
        self.meta = {}
        # self.q2grid.meta["q2_app"].process_events()

        self.frame_order = q2frame({"column": "/v", "label": "Order"})

        self.order_az = q2button(self.meta)
        self.order_az.set_minimum_width(20)
        self.order_az.set_text("Sort A - Z")
        self.order_az.clicked.connect(self._order_az)

        self.order_za = q2button(self.meta)
        self.order_za.set_text("Sort Z - A")
        self.order_za.clicked.connect(self._order_za)

        self.frame_order.layout().addWidget(self.order_az)
        self.frame_order.layout().addWidget(self.order_za)

        self.filter_by_cond = q2button(self.meta)
        self.filter_by_cond.set_text("Filter by condition")

        self.filter_by_values = q2button(self.meta)
        self.filter_by_values.set_text("Filter by values")
        self.filter_by_values.set_minimum_width(20)

        self._search_item = q2line()
        self._search_item.setPlaceholderText("Search items...")
        self._search_item.textChanged.connect(self.on_search_changed)

        self.frame_filter = q2frame({"column": "/v", "label": "Filter"})
        self.check_all = q2check({"label": "Check all", "data": True})
        self.content_viewer = q2_col_manager.content_view(self)
        self.check_all.toggled.connect(self.content_viewer.check_all)

        self.frame_filter_buttons = q2frame({"column": "/h", "label": "-"})

        self.filter_ok_button = q2button(self.meta)
        self.filter_ok_button.set_text("Ok")
        self.filter_ok_button.setObjectName("_ok_button")
        self.filter_ok_button.clicked.connect(self.apply_filter)

        self.filter_cancel_button = q2button(self.meta)
        self.filter_cancel_button.set_text("Cancel")
        self.filter_cancel_button.setObjectName("_cancel_button")
        self.filter_cancel_button.clicked.connect(self.close)
        self.frame_filter_buttons.layout().addWidget(self.filter_ok_button)
        self.frame_filter_buttons.layout().addWidget(self.filter_cancel_button)

        self.frame_filter.layout().addWidget(self._search_item)
        self.frame_filter.layout().addWidget(self.check_all)
        self.frame_filter.layout().addWidget(self.content_viewer)
        self.frame_filter.layout().addWidget(self.frame_filter_buttons)

        self.layout().addWidget(self.frame_order)
        self.layout().addWidget(self.frame_filter)

    def on_search_changed(self, text):
        self.content_viewer.on_search_changed(text)

    def apply_filter(self):
        checked = self.content_viewer.get_checked()
        if len(checked) == self.content_viewer._model.rowCount():
            checked = []
        self.q2grid.apply_col_filter(checked)
        self.close()

    def check_all_changed(self):
        self.content_viewer.check_all(self.check_all.isChecked())

    def closeEvent(self, a0):
        self.q2grid.setEnabled(True)
        self.q2grid.set_focus()
        return super().closeEvent(a0)

    def _order_az(self):
        self.hide()
        self.q2grid.q2_form.grid_header_clicked(self._column, "AZ")
        self.close()

    def _order_za(self):
        self.hide()
        self.q2grid.q2_form.grid_header_clicked(self._column, "ZA")
        self.close()

    def show(self) -> None:
        super().show()
        self.set_geometry()
        self._search_item.setFocus()

    def set_geometry(self):
        rect = self.q2grid.visualRect(self.q2grid.currentIndex())
        rect.moveTop(self.q2grid.horizontalHeader().height() + 2)
        rect.moveLeft(self.q2grid.verticalHeader().width() + rect.x() + 2)
        if self.content_viewer.columnWidth(0) > self.q2grid.width():
            w = self.content_viewer.columnWidth(0)
            if w > self.q2grid.width():
                w = self.q2grid.width() - rect.topLeft().x()
            self.setFixedWidth(w)
        pos = rect.topLeft()
        if pos.x() + self.width() > self.q2grid.rect().width():
            pos.setX(self.q2grid.rect().width() - self.width())
        pos = self.q2grid.mapToGlobal(pos)
        self.move(pos)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_PageDown:
            self.apply_filter()
        return super().keyPressEvent(event)
