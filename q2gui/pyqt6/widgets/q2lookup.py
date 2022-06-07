import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()


from PyQt6.QtWidgets import (
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtGui import QKeyEvent

from PyQt6.QtCore import Qt, QTimer

from q2gui.pyqt6.widgets.q2line import q2line
from q2gui.pyqt6.widgets.q2list import q2list


class q2lookup(QWidget):
    def __init__(self, parent, text):
        super().__init__(parent, Qt.WindowType.Popup)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.lookup_edit = q2line({})
        self.lookup_list = q2list({})
        self.layout().addWidget(self.lookup_edit)
        self.layout().addWidget(self.lookup_list)
        self.lookup_edit.set_text("" if text == "*" else text)
        self.lookup_edit.setFocus()

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.lookup_search)

        self.lookup_edit.textChanged.connect(self.lookup_text_changed)
        self.lookup_edit.returnPressed.connect(self.lookup_edit_return_pressed)

        self.lookup_list.itemActivated.connect(self.lookup_list_selected)

        self.set_geometry()

    def lookup_list_selected(self):
        print("Method lookup_list_selected has to be implemented...")

    def set_geometry(self):
        print("Method set_geometry has to be implemented...")

    # def show(self, column):
    #     self.q2_model_column = column
    #     return super().show()

    def lookup_list_selected(self):
        print(self.lookup_list.currentItem().text())
        self.close()

    def lookup_search(self):
        self.lookup_list.clear()
        for x in range(6):
            self.lookup_list.addItem(f"{x} Method lookup_search has to be implemented...")

    def lookup_edit_return_pressed(self):
        self.timer.stop()
        self.timer.timeout.emit()
        self.lookup_list.setFocus()

    def lookup_text_changed(self):
        if len(self.lookup_edit.get_text()) > 1:
            self.timer.start()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Down and self.lookup_edit.hasFocus():
            event.accept()
            self.lookup_list.setCurrentRow(0)
            self.lookup_list.setFocus()
        elif event.key() == Qt.Key.Key_Up and self.lookup_list.hasFocus() and self.lookup_list.currentRow() == 0:
            self.lookup_edit.setFocus()
            event.accept()
        else:
            return super().keyPressEvent(event)
