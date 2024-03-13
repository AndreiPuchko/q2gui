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


from PyQt6.QtWidgets import QComboBox, QApplication
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QKeyEvent
from q2gui.pyqt6.q2widget import Q2Widget
from q2gui.q2utils import int_


class q2combo(QComboBox, Q2Widget):
    def __init__(self, meta):
        super().__init__(meta)
        self.meta = meta
        self.set_data(meta.get("pic", ""))
        if self.meta.get("data"):
            self.set_text(self.meta.get("data"))
        else:
            self.setCurrentIndex(0)
        self.currentIndexChanged.connect(self.valid)

    def set_data(self, data):
        self.clear()
        if isinstance(data, str):
            data = data.split(";")
        width = 0
        for item in data:
            self.addItem(item)
            width = max(len(item), width)
        width = self.meta.get("datalen", width)
        self.set_minimum_width(width)

    def keyPressEvent(self, ev):
        if ev.key() in [
            Qt.Key.Key_Down,
            Qt.Key.Key_Up,
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

    def set_text(self, text):
        if self.meta.get("num") or isinstance(text, int):
            index = int_(text)
            index = index - 1 if index else 0
        else:
            index_list = [x for x in range(self.count()) if self.itemText(x) == text]
            if index_list:
                index = index_list[0]
            else:
                index = 0
        self.setCurrentIndex(index)

    def get_text(self):
        if self.currentText():
            if self.meta.get("num"):
                return self.currentIndex() + 1
            else:
                return self.currentText()
        else:
            return ""

    def set_readonly(self, arg):
        self.setDisabled(arg)
        return super().set_readonly(arg)
