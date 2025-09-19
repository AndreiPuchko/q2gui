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


from PyQt6.QtGui import QMouseEvent, QColor, QPalette
from PyQt6.QtWidgets import QFrame, QColorDialog
from PyQt6.QtCore import Qt

import q2gui.q2app as q2app
from q2gui.q2form import Q2Form
from q2gui.q2utils import num
from q2gui.pyqt6.q2widget import Q2Widget
from q2gui.pyqt6.q2window import Q2Frame
from q2gui.pyqt6.widgets.q2line import q2line
from q2gui.pyqt6.widgets.q2button import q2button


class q2color(QFrame, Q2Widget, Q2Frame):
    def __init__(self, meta):
        super().__init__(meta)
        Q2Frame.__init__(self, "h")
        self.meta = meta
        self._color = QColor(meta.get("data", "black"))

        # --- Button ---
        self.btn = q2button(
            {
                "label": "",
                "valid": self.choose_color,
                # "when": self.when,
                "form": self.meta["form"],
            }
        )
        self.btn.setFixedSize(20, 20)
        # --- Line ---
        self.meta["changed"] = self.line_changed
        self.line = q2line(meta)

        # --- Layout ---
        self.add_widget(self.btn)
        self.add_widget(self.line)
        self.set_content_margins(0)
        self.layout().setSpacing(3)
        self.setFocusProxy(self.line)
        self._update_button_color()

    # --- Logic ---
    def _update_button_color(self):
        self.btn.add_style_sheet(f"background-color:{self.line.get_text()}")

    def choose_color(self):
        new_color = QColorDialog.getColor(QColor(self.line.get_text()), self, "Select Color")
        if new_color.isValid():
            self.set_color(new_color)

    def line_changed(self, text):
        color = QColor(text.strip())
        if color.isValid():
            self._update_button_color()

    # --- Public API ---
    def set_color(self, color):
        if hasattr(self, "line"):
            self.line.set_text(color.name())

    def set_text(self, text):
        color = QColor(text)
        if color.isValid():
            self.set_color(color)

    def text(self):
        return self.line.get_text()
