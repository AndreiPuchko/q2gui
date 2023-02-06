import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()

from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import QByteArray, QBuffer, QIODevice
from q2gui.pyqt6.q2widget import Q2Widget
from q2gui.q2app import Q2Actions
import q2gui.q2app as q2app


class q2image(QLabel, Q2Widget):
    def __init__(self, meta={}):

        actions = Q2Actions()
        actions.add_action("Load image", self.load_image_from_file)
        meta["actions"] = actions

        self.image_hex = None

        super().__init__(meta)
        self.setText("")
        self.set_text(self.meta["data"])

    def load_image_from_file(self):
        image_file = q2app.q2_app.get_open_file_dialoq("", filter="Images (*.jpg *.png)")[0]
        if image_file:
            image = QImage(image_file)
            pixmap = QPixmap.fromImage(image)
            self.setPixmap(pixmap)
            self.image_hex = self.get_hex()

    def get_hex(self):
        ba = QByteArray()
        buffer = QBuffer(ba)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        self.pixmap().toImage().save(buffer, "JPG")
        return ba.toHex()

    def set_text(self, text):
        self.image_hex = text
        image = QImage.fromData(QByteArray.fromHex(bytes(text, "utf8")))
        pixmap = QPixmap.fromImage(image)
        self.setPixmap(pixmap)

    def get_text(self):
        return self.image_hex
