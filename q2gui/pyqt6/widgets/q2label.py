import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt

from q2gui.pyqt6.q2widget import Q2Widget

vertical_align_dict = {
    "top": Qt.AlignmentFlag.AlignTop,
    "middle": Qt.AlignmentFlag.AlignVCenter,
    "bottom": Qt.AlignmentFlag.AlignBottom,
}

horizontal_align_dict = {
    "left": Qt.AlignmentFlag.AlignLeft,
    "center": Qt.AlignmentFlag.AlignHCenter,
    "justify": Qt.AlignmentFlag.AlignJustify,
    "right": Qt.AlignmentFlag.AlignRight,
}


class q2label(QLabel, Q2Widget):
    def __init__(self, meta={}):
        super().__init__({"label": meta.get("label", ""), "dblclick": meta.get("dblclick")})
        # super().__init__(meta)
        self.set_text(self.meta["label"])
        self.setWordWrap(True)
        self.set_maximum_height(int(self.get_default_height() * 1.5))

    def set_style_sheet(self, style_text):
        super().set_style_sheet(style_text)

        if "vertical-align" in style_text or "text-align" in style_text:
            if isinstance(style_text, str):
                style_dict = {
                    x[0].strip().replace("{", ""): x[1].strip().replace("}", "")
                    for x in [x.split(":") for x in style_text.split(";") if ":" in x]
                }
            else:
                style_dict = style_text
            CA = vertical_align_dict.get(style_dict.get("vertical-align", "top"), Qt.AlignmentFlag.AlignTop)
            CA |= horizontal_align_dict.get(style_dict.get("text-align", "left"), Qt.AlignmentFlag.AlignLeft)

            self.setAlignment(CA)
