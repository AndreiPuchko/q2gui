import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()


from PyQt6.QtWidgets import (
    QTableView,
    QStyledItemDelegate,
    QAbstractItemView,
    QStyle,
    QSizePolicy,
    QStyleOptionButton,
    QApplication,
)
from PyQt6.QtGui import QPalette, QPainter

from PyQt6.QtCore import Qt, QAbstractTableModel, QVariant

from q2gui.pyqt6.q2window import q2_align
from q2gui.q2utils import int_
from q2gui.q2model import Q2Model
from q2gui.pyqt6.widgets.q2lookup import q2lookup


class q2Delegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option, index):
        if self.parent().currentIndex().column() == index.column():
            color = option.palette.color(QPalette.ColorRole.AlternateBase).darker(900)
            color.setAlpha(int(color.alpha() / 10))
            painter.fillRect(option.rect, color)
        meta = self.parent().model().q2_model.meta[index.column()]
        if meta.get("control") == "check":
            self.paint_checkbox(painter, option, index, meta)
            return
        # elif meta.get("relation"):
        #     super().paint(painter, option, index)
        #     self.paint_relation_button(painter, option, index, meta)
        #     return
        super().paint(painter, option, index)

    # def paint_relation_button(self, painter: QPainter, option, index, meta):
    #     pb_option = QStyleOptionButton()
    #     pb_option.text = "?"
    #     checkBoxRect = QApplication.style().subElementRect(QStyle.SE_PushButtonBevel, pb_option, None)
    #     sz = 30
    #     pb_option.rect = option.rect
    #     pb_option.rect.setX(pb_option.rect.x() - sz + option.rect.width())
    #     print(checkBoxRect.height())
    #     pb_option.rect.setHeight(sz)
    #     pb_option.rect.setWidth(sz)
    #     QApplication.style().drawControl(QStyle.CE_PushButton, pb_option, painter)

    def paint_checkbox(self, painter: QPainter, option, index, meta):
        """paint checkbox - left - with top+left alignment"""
        if meta.get("num"):
            checked = True if int_(index.data()) else False
        else:
            checked = True if index.data() else False
        cb_option = QStyleOptionButton()
        if checked:
            cb_option.state |= QStyle.StateFlag.State_On
        else:
            cb_option.state |= QStyle.StateFlag.State_Off
        checkBoxRect = QApplication.style().subElementRect(
            QStyle.SubElement.SE_CheckBoxIndicator, cb_option, None
        )
        cb_option.rect = option.rect
        cb_option.rect.setX(cb_option.rect.x() + int(checkBoxRect.width() / 2))
        if cb_option.rect.height() > checkBoxRect.height() * 2 + 3:
            cb_option.rect.setHeight(checkBoxRect.height() * 2)
        QApplication.style().drawControl(QStyle.ControlElement.CE_CheckBox, cb_option, painter)


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
            if role == Qt.ItemDataRole.DisplayRole:
                return QVariant(self.q2_model.data(index.row(), index.column()))
            elif role == Qt.ItemDataRole.TextAlignmentRole:
                return QVariant(q2_align[str(self.q2_model.alignment(index.column()))])
            else:
                return QVariant()

        def headerData(self, col, orientation, role=Qt.ItemDataRole.DisplayRole):
            if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
                return self.q2_model.headers[col]
            elif orientation == Qt.Orientation.Vertical and role == Qt.ItemDataRole.DisplayRole:
                return QVariant("")
            else:
                return QVariant()

    # currentCellChangedSignal = pyqtSignal(int, int)

    def __init__(self, meta):
        super().__init__()
        self.meta = meta

        self.q2_form = self.meta.get("form")
        self.q2_model = self.q2_form.model

        # self.setModel(self.Q2TableModel(self.q2_form.model))
        self.setItemDelegate(q2Delegate(self))
        self.setTabKeyNavigation(False)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.horizontalHeader().setSectionsMovable(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.horizontalHeader().setDefaultAlignment(q2_align["7"])
        self.doubleClicked.connect(self.q2_form.grid_double_clicked)
        self.horizontalHeader().sectionClicked.connect(self.q2_form.grid_header_clicked)
        self.setModel(self.Q2TableModel(self.q2_form.model))

    def currentChanged(self, current, previous):
        # self.currentCellChangedSignal.emit(current.row(), current.column())
        super().currentChanged(current, previous)
        self.model().dataChanged.emit(current, previous)
        self.q2_form._grid_index_changed(self.currentIndex().row(), self.currentIndex().column())

    def current_index(self):
        return self.currentIndex().row(), self.currentIndex().column()

    def set_focus(self):
        self.setFocus()

    def row_count(self):
        return self.model().rowCount()

    def column_count(self):
        return self.model().columnCount()

    def set_index(self, row, column=None):
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

    def get_columns_headers(self):
        rez = {}
        hohe = self.horizontalHeader()
        for x in range(0, hohe.count()):
            rez[hohe.model().headerData(x, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)] = x
        return rez

    def get_columns_settings(self):
        rez = []
        hohe = self.horizontalHeader()
        for x in range(0, hohe.count()):
            header = hohe.model().headerData(x, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
            width = self.columnWidth(x)
            pos = hohe.visualIndex(x)
            rez.append({"name": header, "data": f"{pos}, {width}"})
        return rez

    def set_column_settings(self, col_settings):
        headers = self.get_columns_headers()
        for x in col_settings:
            if "," not in col_settings[x]:
                continue
            column_pos = int_(col_settings[x].split(",")[0])
            column_width = int_(col_settings[x].split(",")[1])
            # column_width = column_width if column_width else 10
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
