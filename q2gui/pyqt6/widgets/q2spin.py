import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()

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

    def set_text(self, text):
        self.setValue(int_(text))
