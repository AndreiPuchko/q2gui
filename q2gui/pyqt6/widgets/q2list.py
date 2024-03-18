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


from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QApplication
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QFocusEvent, QKeyEvent


from q2gui.pyqt6.q2widget import Q2Widget
from q2gui.q2utils import int_


class q2list(QListWidget, Q2Widget):
    def __init__(self, meta):
        super().__init__(meta)
        self.set_data(self.meta.get("pic", ""))
        if self.meta.get("data"):
            self.set_text(self.meta.get("data"))
        else:
            self.setCurrentRow(0)
        self.currentRowChanged.connect(self.valid)

    def set_data(self, data):
        self.clear()
        if isinstance(data, str):
            data = data.split(";")
        width = 0
        for item in data:
            self.addItem(QListWidgetItem(item))
            width = max(len(item), width)
        if int_(self.meta.get("datalen", 0)) != 0:
            width = int_(self.meta.get("datalen", 0))
        self.set_minimum_width(width)

    def set_text(self, text):
        if self.meta.get("num"):
            index = int_(text)
            index = index - 1 if index else 0
        else:
            index_list = [x for x in range(self.count()) if self.item(x).text() == text]
            if index_list:
                index = index_list[0]
            else:
                index = 0
        self.setCurrentRow(index)

    def get_text(self):
        if self.currentItem():
            if self.meta.get("num"):
                return self.row(self.currentItem()) + 1
            else:
                return self.currentItem().text()
        else:
            return ""

    def keyPressEvent(self, ev):
        if ev.key() in [
            Qt.Key.Key_PageDown,
            Qt.Key.Key_PageUp,
        ]:
            ev.ignore()
        elif ev.key() == Qt.Key.Key_Right:
            QApplication.sendEvent(self, QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Tab, ev.modifiers()))
        elif ev.key() == Qt.Key.Key_Left:
            QApplication.sendEvent(
                self, QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Tab, Qt.KeyboardModifier.ShiftModifier)
            )
        else:
            super().keyPressEvent(ev)

    def focusInEvent(self, e: QFocusEvent | None) -> None:
        if self.meta["q2_app"].q2style.color_mode in ("dark", "light"):
            self._focus_background_color = self.meta["q2_app"].q2style.styles[
                self.meta["q2_app"].q2style.color_mode
            ]["background_focus"]
            self._focus_color = self.meta["q2_app"].q2style.styles[self.meta["q2_app"].q2style.color_mode][
                "color_focus"
            ]
            self.setStyleSheet(f"background-color:{self._focus_background_color}; color:{self._focus_color}")
        return super().focusInEvent(e)

    def focusOutEvent(self, e: QFocusEvent | None) -> None:
        if self.meta["q2_app"].q2style.color_mode in ("dark", "light"):
            self._background_color = self.meta["q2_app"].q2style.styles[
                self.meta["q2_app"].q2style.color_mode
            ]["background"]
            self._color = self.meta["q2_app"].q2style.styles[self.meta["q2_app"].q2style.color_mode]["color"]
            self.setStyleSheet(f"background-color:{self._background_color}; color:{self._color}")
        return super().focusOutEvent(e)
