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

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()

from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import QSize

from q2gui.pyqt6.q2widget import Q2Widget


class q2text(QTextEdit, Q2Widget):
    def __init__(self, meta):
        super().__init__(meta)
        self.setTabChangesFocus(True)
        self.set_text(meta.get("data"))

    def set_text(self, text):
        self.setHtml(text)

    def get_text(self):
        return f"{self.toPlainText()}"

    def set_size_policy(self, horizontal, vertical):
        return super().set_size_policy(horizontal, vertical)

    def showEvent(self, ev):
        self.updateGeometry()
        return super().showEvent(ev)

    def sizeHint(self):
        if self.isVisible():
            return QSize(99999, 99999)
        else:
            return super().sizeHint()
