import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()

from PyQt6.QtWidgets import QLineEdit

from q2gui.pyqt6.q2widget import Q2Widget
from q2gui.q2utils import int_, num
from q2gui import q2app


class q2line(QLineEdit, Q2Widget):
    def __init__(self, meta):
        super().__init__(meta)
        self.last_text_len = 0
        self.last_cur_pos = 0
        # if self.meta.get("pic"):
        self.TS = " "  # thousands separator
        self.DS = "."  # decimal separator

        if self.meta.get("num"):
            self.declen = int_(self.meta.get("datadec", 0))
            if self.meta.get("pic") == "F":  # financial
                self.formatstring = q2app.FINANCIAL_FORMAT % self.declen
            else:
                self.formatstring = "{:.%sf}" % self.declen
            self.textChanged.connect(self.format_decimal)
            self.cursorPositionChanged.connect(self.track_cursor)
            self.textChanged.emit("")

    def track_cursor(self, old, new):
        self.last_cur_pos = new

    def get_text(self):
        if self.meta.get("num"):
            return self.text().replace(self.TS, "")
        else:
            return super().get_text()

    def format_decimal(self):
        text = self.text()

        self.blockSignals(True)
        cursor_pos = self.cursorPosition()
        cursor_pos_right = len(text) - cursor_pos

        negative = text.count("-") == 1 and text.count("+") == 0
        # divide text by cursor pos
        right_text = text[cursor_pos:]
        left_text = text[:-cursor_pos_right] if cursor_pos_right else text

        if left_text.endswith(","):  # replace comma with point
            left_text = left_text[:-1] + self.DS

        # TS removed
        if left_text and len(text) < self.last_text_len and len(right_text) > 3:
            if (
                right_text[3] in [self.TS, self.DS]
                and left_text[-1] != self.TS
                and cursor_pos - self.last_cur_pos < 0
            ):
                left_text = left_text[:-1]  # remove TS
        # remove non-digit chars and change cursor position
        left_text = "".join([x for x in left_text if x in "0123456789., "])
        text = left_text + right_text

        if self.declen == 0:
            text = text.replace(".", "")
        else:  # for decimal only
            if self.DS not in text:
                text += "."
                cursor_pos_right = self.declen

            if text == "":  # empty text - just 0
                text = "0." + "0" * self.declen
            elif text.count(self.DS) == 0:  # DS deleted
                text = text[:-2] + self.DS + text[-2:]
            elif text.count(self.DS) > 1:  # entered decimal_separator - move cursor postion
                text = left_text[:-1] + right_text
                if "." in right_text:  # added DS left from DS
                    cursor_pos_right = self.declen
                else:
                    cursor_pos_right = self.declen + 1
            else:
                spl = text.split(self.DS)
                if cursor_pos_right <= self.declen:  # cursor in decimal part
                    if len(spl[1]) < self.declen:  # deleted from decimal part
                        text += "0"
                        cursor_pos_right += 1
                    elif len(spl[1]) > self.declen:  # decimal part entered
                        text = text[: -(len(spl[1]) - self.declen)]
                        cursor_pos_right -= 1
                else:  # cursor left of DS
                    if len(spl[0]) == 2 and spl[0][-1] == "0":
                        # 0 only was left from DS-cut 0
                        text = spl[0][:-1] + self.DS + spl[1]
                        cursor_pos_right -= 1

        text = self.formatstring.format(num(text.replace(self.TS, ""))).replace(",", self.TS)
        cursor_pos = len(text) - cursor_pos_right
        if negative:
            text = f"-{text}"
            cursor_pos += 1

        self.setText(text)
        self.setCursorPosition(cursor_pos)
        self.last_text_len = len(text)
        self.last_cur_pos = cursor_pos
        self.blockSignals(False)
