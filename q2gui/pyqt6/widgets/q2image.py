import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()

import codecs
import os
from PyQt6.QtWidgets import QLabel, QApplication
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import QByteArray, QBuffer, QIODevice, QFile
from q2gui.pyqt6.q2widget import Q2Widget
from q2gui.q2app import Q2Actions
import q2gui.q2app as q2app


class q2image(QLabel, Q2Widget):
    def __init__(self, meta={}):
        actions = Q2Actions()
        # actions.show_main_button = 0
        # actions.show_actions = 0
        actions.add_action("Load", self.load_image_from_file)
        actions.add_action("Save", self.save_image_to_file)
        actions.add_action("-")
        actions.add_action("Paste", self.clipboard_paste)
        actions.add_action("Copy", self.clipboard_copy)
        actions.add_action("-")
        actions.add_action("Clear", self.clear_image)
        meta["actions"] = actions
        super().__init__(meta)

        self.image_base64 = None

        self.set_text(self.meta["data"])
        self.set_style_sheet("{border: 1px solid black; border-radius:0px; margin:0px; padding:0px }")

    def clear_image(self):
        self.set_qimage(QImage())

    def clipboard_copy(self):
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(self.pixmap())

    def clipboard_paste(self):
        clipboard = QApplication.clipboard()
        if not clipboard.image(clipboard.Mode.Clipboard).isNull():
            self.set_qimage(clipboard.image(clipboard.Mode.Clipboard))
        elif clipboard.mimeData().hasUrls():
            filename = clipboard.mimeData().urls()[0].toLocalFile()
            if "LNK" == filename[-3:].upper():
                filename = QFile.symLinkTarget(filename)
            try:
                self.set_qimage(QImage(filename))
            except Exception:
                pass

    def save_image_to_file(self):
        image_file, image_type = q2app.q2_app.get_save_file_dialoq(
            "Save image",
            filter="PNG (*.png);;JPG(*.jpg)",
        )
        if image_file:
            self.pixmap().toImage().save(image_file)

    def load_image_from_file(self):
        image_file = q2app.q2_app.get_open_file_dialoq(
            "Load image",
            filter="Images (*.png *.jpg)",
        )[0]
        if image_file:
            self.set_qimage(QImage(image_file))
            self.image_base64 = self.get_base64()

    def get_base64(self):
        ba = QByteArray()
        buffer = QBuffer(ba)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        self.pixmap().toImage().save(buffer, "PNG")
        return ba.toBase64()

    def ensure_base64(self, text):
        try:
            text = text.replace("\n", "").replace(" ", "")
            int(text, 16)
            text = codecs.encode(codecs.decode(text, "hex"), "base64").decode()
        except Exception:
            pass
        finally:
            return text

    def set_text(self, text):
        self.image_base64 = self.ensure_base64(text)
        image = QImage.fromData(QByteArray.fromBase64(bytes(self.image_base64, "utf8")))
        self.set_qimage(image)

    def set_qimage(self, image):
        pixmap = QPixmap.fromImage(image)
        self.setPixmap(pixmap)
        # self.setFixedSize(self.pixmap().size())
        if self.parentWidget():
            self.parentWidget().layout().update()

    def get_text(self):
        return self.image_base64
