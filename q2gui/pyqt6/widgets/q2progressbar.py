import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()

from PyQt6.QtWidgets import QProgressBar


from q2gui.pyqt6.q2widget import Q2Widget


class q2progressbar(QProgressBar, Q2Widget):
    def __init__(self, meta):
        super().__init__(meta)
        self.set_text(meta["label"])
        self.setMaximum(0)
        self.setMinimum(0)

    def set_max(self, value):
        self.setMaximum(value)

    def set_min(self, value):
        self.setMinimum(value)

    def set_value(self, value):
        if self.minimum() < self.maximum():
            self.setValue(value)
