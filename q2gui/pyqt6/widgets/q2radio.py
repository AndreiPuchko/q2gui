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




from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QRadioButton, QSizePolicy, QApplication
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QKeyEvent

from q2gui.pyqt6.q2window import q2_align
from q2gui.pyqt6.q2widget import Q2Widget
from q2gui.q2utils import int_


class q2radio(QFrame, Q2Widget):
    def __init__(self, meta):
        super().__init__(meta)
        self.setLayout(QVBoxLayout() if "v" in meta.get("control") else QHBoxLayout())
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.layout().setAlignment(q2_align["7"])
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setObjectName("radio")
        self.button_list = []
        for item in meta.get("pic", "").split(";"):
            button = q2RadioButton(item, self)
            self.button_list.append(button)
            self.layout().addWidget(button)

        self.button_list[0].setChecked(True)
        if meta.get("data") is not None:
            self.set_text(meta.get("data"))

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


    def can_get_focus(self):
        return True

    def focusInEvent(self, ev):
        self._focus_in()
        # return super().focusInEvent(ev)

    def _focus_in(self):
        self.button_list[self.get_current_index()].set_focus()

    def set_text(self, text):
        if hasattr(self, "button_list"):
            if self.meta.get("num"):
                index = int_(text)
                index = index - 1 if index else 0
            else:
                index_list = [
                    x for x in range(len(self.button_list)) if self.button_list[x].get_text() == text
                ]
                if index_list:
                    index = index_list[0]
                else:
                    index = 0
            self.button_list[index].setChecked(True)

    def get_current_index(self):
        index_list = [x for x in range(len(self.button_list)) if self.button_list[x].isChecked()]
        if index_list:
            return index_list[0]
        else:
            return None

    def get_text(self):
        index_list = [x for x in range(len(self.button_list)) if self.button_list[x].isChecked()]
        if index_list:
            index = index_list[0]
            if self.meta.get("num"):
                return str(index + 1)
            else:
                return self.button_list[index].get_text()
        else:
            return ""


class q2RadioButton(QRadioButton):
    def __init__(self, text, radio: q2radio):
        super().__init__(text)
        self.radio = radio
        self.toggled.connect(self.value_changed)
        self.setContentsMargins(0, 0, 0, 0)

    def focusInEvent(self, ev):
        self.radio._focus_in()
        return super().focusInEvent(ev)

    def value_changed(self, value):
        return self.radio.valid()

    def get_text(self):
        return self.text()

    def set_focus(self):
        self.setFocus()
