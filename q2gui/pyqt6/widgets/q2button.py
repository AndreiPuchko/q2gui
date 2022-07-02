import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()


from PyQt6.QtWidgets import QPushButton, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontMetrics

from q2gui.pyqt6.q2widget import Q2Widget
from q2gui.q2utils import num


class q2button(QPushButton, Q2Widget):
    def __init__(self, meta):
        super().__init__(meta)
        # self.meta = meta
        # self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Maximum)
        self.set_text(meta.get("label"))
        if self.meta.get("valid"):
            self.clicked.connect(self.valid)
        ml = num(self.meta.get("datalen"))
        if ml:
            self.setMinimumWidth(int(QFontMetrics(self.font()).horizontalAdvance("W") * ml))

    def focusInEvent(self, event):
        if self.meta.get("form_window") and not self.meta.get("form_window").form_is_active is True:
            return
        if self.meta.get("when"):
            self.when()
        return super().focusInEvent(event)

    def keyPressEvent(self, ev):
        if ev.key() in [Qt.Key.Key_Enter, Qt.Key.Key_Return] and not self.meta.get("eat_enter"):
            ev.accept()
            self.focusNextChild()
        else:
            super().keyPressEvent(ev)
