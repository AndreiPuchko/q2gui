import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QSizePolicy

from q2gui.pyqt6.q2widget import Q2Widget


class q2space(QFrame, Q2Widget):
    def __init__(self, meta):
        super().__init__(meta)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.setLayout(QHBoxLayout())
        self.layout().addStretch()
