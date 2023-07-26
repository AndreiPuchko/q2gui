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



from PyQt6.QtWidgets import QSpinBox

from q2gui.pyqt6.q2widget import Q2Widget
from q2gui.q2utils import int_


class q2spin(QSpinBox, Q2Widget):
    def __init__(self, meta):
        super().__init__(meta)
        self.meta = meta
        self.set_text(meta.get("data"))
        if self.meta.get("valid"):
            self.valueChanged.connect(self.meta.get("valid"))
        self.set_fixed_height()

    def set_text(self, text):
        self.setValue(int_(text))
