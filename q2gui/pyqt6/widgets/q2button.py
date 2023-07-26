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




from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontMetrics

from q2gui.pyqt6.q2widget import Q2Widget
from q2gui.q2utils import num


class q2button(QPushButton, Q2Widget):
    def __init__(self, meta):
        super().__init__(meta)
        # self.meta = meta
        # self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Maximum)
        self.set_text(meta.get("label"))
        if self.meta.get("valid"):
            self.clicked.connect(self.valid)
        ml = num(self.meta.get("datalen"))
        if ml:
            self.setMinimumWidth(int(QFontMetrics(self.font()).horizontalAdvance("W") * ml))

    def focusInEvent(self, event):
        if self.meta.get("form_window") and not self.meta.get("form_window").form_is_active is True:
            return
        if self.meta.get("when"):
            self.when()
        return super().focusInEvent(event)

    def keyPressEvent(self, ev):
        if ev.key() in [Qt.Key.Key_Enter, Qt.Key.Key_Return] and not self.meta.get("eat_enter"):
            ev.accept()
            self.focusNextChild()
        else:
            super().keyPressEvent(ev)
