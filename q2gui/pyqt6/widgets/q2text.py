import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()

from PyQt6.QtWidgets import QTextEdit, QSizePolicy

from q2gui.pyqt6.q2widget import Q2Widget


class q2text(QTextEdit, Q2Widget):
    def __init__(self, meta):
        super().__init__(meta)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
        self.set_text(meta.get('data'))

    def set_text(self, text):
        self.setHtml(text)

    def get_text(self):
        return f"{self.toPlainText()}"
