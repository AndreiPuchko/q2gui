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


from PyQt6.QtWidgets import (
    QTableView,
    QStyledItemDelegate,
    QAbstractItemView,
    QSizePolicy,
)
from PyQt6.QtGui import QPalette, QPainter

from PyQt6.QtCore import Qt, QAbstractTableModel, QVariant, QItemSelectionModel

from q2gui.pyqt6.q2window import q2_align
from q2gui.q2utils import int_
from q2gui.q2model import Q2Model
from q2gui.pyqt6.widgets.q2lookup import q2lookup


sort_ascend_char = "▲"
sort_decend_char = "▼"


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

        def set_order(self, column):
            self.q2_model.order_column(column)

        def rowCount(self, parent=None):
            return self.q2_model.row_count()

        def columnCount(self, parent=None):
            return self.q2_model.column_count()

        def refresh(self):
            self.beginResetModel()
            self.endResetModel()
            self._q2_model_refresh()

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
                return sort_char + self.q2_model.headers[col]
            elif orientation == Qt.Orientation.Vertical and role == Qt.ItemDataRole.DisplayRole:
                return QVariant("")
            else:
                return QVariant()

        def flags(self, index):
            control = self.q2_model.meta[index.column()].get("control")
            flags = super().flags(index)
            if control == "check":
                flags |= Qt.ItemFlag.ItemIsUserCheckable
            return flags

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
            lookup_widget = q2_grid_lookup(self, event.text())
            lookup_widget.show(self, self.currentIndex().column())
        else:
            super().keyPressEvent(event)

    def get_selected_rows(self):
        return [x.row() for x in self.selectionModel().selectedRows()]

    def set_selected_rows(self, index_list):
        self.clearSelection()
        indexes = [self.model().index(r, 0) for r in index_list]
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
        return super().show()

    def set_geometry(self):
        parent = self.parent()
        rect = parent.visualRect(parent.currentIndex())
        rect.moveTop(parent.horizontalHeader().height() + 2)
        rect.moveLeft(parent.verticalHeader().width() + rect.x() + 2)
        pos = rect.topLeft()
        pos = parent.mapToGlobal(pos)
        self.setFixedWidth(parent.width() - rect.x())
        self.move(pos)
