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


from PyQt6.QtWidgets import QListWidget, QListWidgetItem

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
        for item in data:
            self.addItem(QListWidgetItem(item))

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
