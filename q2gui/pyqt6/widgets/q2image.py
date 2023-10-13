#    Copyright © 2021 Andrei Puchko
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import os


import codecs

from PyQt6.QtWidgets import QLabel, QApplication, QSizePolicy
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import QByteArray, QBuffer, QIODevice, QFile, Qt

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
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)

        self.image_base64 = ""
        self.image = None

        self.set_text(self.meta["data"])
        self.set_style_sheet("{border: 1px solid black; border-radius:0px; margin:0px; padding:0px }")

    def clear_image(self):
        self.set_qimage(image=QImage())

    def clipboard_copy(self):
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(QPixmap.fromImage(self.image))

    def clipboard_paste(self):
        clipboard = QApplication.clipboard()
        if not clipboard.image(clipboard.Mode.Clipboard).isNull():
            self.set_qimage(image=clipboard.image(clipboard.Mode.Clipboard))
        elif clipboard.mimeData().hasUrls():
            filename = clipboard.mimeData().urls()[0].toLocalFile()
            if "LNK" == filename[-3:].upper():
                filename = QFile.symLinkTarget(filename)
            try:
                self.set_qimageimage = QImage(filename)
            except Exception:
                pass

    def save_image_to_file(self):
        image_file, image_type = q2app.q2_app.get_save_file_dialoq(
            "Save image",
            filter="PNG (*.png);;JPG(*.jpg)",
        )
        if image_file:
            self.image.save(image_file)

    def load_image_from_file(self, image_file=""):
        if not os.path.isfile(image_file):
            image_file = q2app.q2_app.get_open_file_dialoq(
                "Load image",
                filter="Images (*.png *.jpg)",
            )[0]
        if image_file:
            self.set_qimage(image=QImage(image_file))

    def get_base64(self):
        ba = QByteArray()
        buffer = QBuffer(ba)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        self.image.save(buffer, "PNG")
        return bytes(ba.toBase64()).decode("utf-8")

    def ensure_base64(self, text):
        try:
            text = text.replace("\n", "").replace(" ", "")
            int(text, 16)
            text = codecs.encode(codecs.decode(text, "hex"), "base64").decode()
        except Exception:
            pass
        finally:
            return text

    def resizeEvent(self, ev):
        rez = super().resizeEvent(ev)
        self.keep_size()
        return rez

    def set_qimage(self, image: QImage = None, image_base64=None):
        if image_base64:
            self.image_base64 = image_base64
            self.image = QImage.fromData(QByteArray.fromBase64(bytes(self.image_base64, "utf8")))
        elif image:
            self.image = image
            self.image_base64 = self.get_base64()
        else:
            self.image = QImage()
            self.image_base64 = None

        self.setPixmap(QPixmap.fromImage(self.image))
        self.keep_size()

    def keep_size(self):
        if (
            self.size().width() < self.image.size().width()
            or self.size().height() < self.image.size().height()
        ):
            self.setPixmap(
                QPixmap.fromImage(self.image).scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
            )

    def set_text(self, text):
        self.set_qimage(image_base64=self.ensure_base64(text))

    def get_text(self):
        return self.image_base64
