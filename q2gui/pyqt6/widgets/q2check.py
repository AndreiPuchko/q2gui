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



from PyQt6.QtWidgets import QCheckBox, QSizePolicy

from q2gui.pyqt6.q2widget import Q2Widget
from q2gui.q2utils import int_


class q2check(QCheckBox, Q2Widget):
    def __init__(self, meta):
        super().__init__(meta)
        if meta.get("pic"):
            self.setText(meta.get("pic"))
        else:
            self.setText(meta.get("label", ""))
        self.managed_widgets = []
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.stateChanged.connect(self.state_changed)

    def state_changed(self):
        for x in self.managed_widgets:
            x.set_enabled(self.isChecked())
            if x.is_enabled() and self.hasFocus():
                x.set_focus()
            if self.isChecked():
                if x.meta.get("when"):
                    x.meta.get("when")()
            else:
                if x.meta.get("valid"):
                    x.meta.get("valid")()
        self.valid()

    def add_managed_widget(self, widget):
        self.managed_widgets.append(widget)
        widget.check = self

    def remove_managed_widget(self, widget):
        if widget in self.managed_widgets:
            self.managed_widgets.pop(self.managed_widgets.index(widget))

    def set_text(self, text):
        if self.meta.get("num"):
            self.setChecked(True if int_(text) else False)
        else:
            self.setChecked(True if text else False)

    def set_title(self, title):
        self.setText(title)

    def get_text(self):
        if self.meta.get("num"):
            return 1 if self.isChecked() else 0
        else:
            return "*" if self.isChecked() else ""

    def set_checked(self, mode=True):
        self.set_text(mode)

    def is_checked(self):
        return True if self.get_text() else False
