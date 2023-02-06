import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()

from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import QByteArray, QBuffer, QIODevice
from q2gui.pyqt6.q2widget import Q2Widget


class q2image(QLabel, Q2Widget):
    def __init__(self, meta={}):
        super().__init__(meta)
        self.setWordWrap(True)
        super().setText("")
        self.set_text(self.meta["data"])

    def set_text(self, text):
        img = QImage.fromData(QByteArray.fromHex(bytes(text, "utf8")))
        pixmap = QPixmap.fromImage(img)
        self.setPixmap(pixmap)

    def get_text(self):
        ba = QByteArray()
        buffer = QBuffer(ba)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        self.pixmap().toImage().save(buffer, "JPG")
        return ba.toHex()
