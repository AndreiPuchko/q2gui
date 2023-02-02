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
