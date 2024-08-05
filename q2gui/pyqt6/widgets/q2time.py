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


from PyQt6.QtWidgets import QTimeEdit, QAbstractSpinBox
from PyQt6.QtCore import QTime, Qt
from q2gui.pyqt6.q2widget import Q2Widget

# from q2gui.q2utils import int_


class q2time(QTimeEdit, Q2Widget):
    def __init__(self, meta):
        super().__init__(meta)
        self.meta = meta
        self.set_text(meta.get("data"))
        if self.meta.get("valid"):
            self.timeChanged.connect(self.meta.get("valid"))

        self.set_fixed_height()
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.PlusMinus)

    def set_text(self, text):
        self.setTime(QTime.fromString(text, "HH:mm:ss"))

    def get_text(self):
        return self.text()

    def keyPressEvent(self, ev):
        if ev.key() in [
            Qt.Key.Key_Down,
            Qt.Key.Key_Up,
            Qt.Key.Key_PageDown,
            Qt.Key.Key_PageUp,
        ]:
            ev.ignore()
        elif ev.key() == Qt.Key.Key_Plus:
            tm: QTime = self.time()
            if self.currentSection() == self.Section.HourSection:
                tm = tm.addSecs(3600)
                self.setTime(tm)
            if self.currentSection() == self.Section.MinuteSection:
                tm = tm.addSecs(60)
                self.setTime(tm)
        elif ev.key() == Qt.Key.Key_Minus:
            tm: QTime = self.time()
            if self.currentSection() == self.Section.HourSection:
                tm = tm.addSecs(-3600)
                self.setTime(tm)
            if self.currentSection() == self.Section.MinuteSection:
                tm = tm.addSecs(-60)
                self.setTime(tm)
        else:
            super().keyPressEvent(ev)
