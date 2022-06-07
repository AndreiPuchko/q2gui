import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()

from PyQt6.QtWidgets import QToolButton, QSizePolicy

from q2gui.pyqt6.q2widget import Q2Widget


class q2toolbutton(QToolButton, Q2Widget):
    def __init__(self, meta):
        super().__init__(meta)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.set_text(meta.get("label"))
        if self.meta.get("valid"):
            self.clicked.connect(self.valid)
