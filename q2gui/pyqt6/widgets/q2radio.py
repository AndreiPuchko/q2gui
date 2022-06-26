import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()


from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QRadioButton, QSizePolicy

from q2gui.pyqt6.q2window import q2_align
from q2gui.pyqt6.q2widget import Q2Widget
from q2gui.q2utils import int_


class q2radio(QFrame, Q2Widget):
    def __init__(self, meta):
        super().__init__(meta)
        self.setLayout(QVBoxLayout() if "v" in meta.get("control") else QHBoxLayout())
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.layout().setAlignment(q2_align["7"])
        # self.layout().setSpacing(0)
        # self.setContentsMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.button_list = []
        for item in meta.get("pic", "").split(";"):
            button = q2RadioButton(item, self)
            self.button_list.append(button)
            self.layout().addWidget(button)

        self.button_list[0].setChecked(True)

    def set_text(self, text):
        if hasattr(self, "button_list"):
            if self.meta.get("num"):
                index = int_(text)
                index = index - 1 if index else 0
            else:
                index_list = [
                    x for x in range(len(self.button_list)) if self.button_list[x].get_text() == text
                ]
                if index_list:
                    index = index_list[0]
                else:
                    index = 0
            self.button_list[index].setChecked(True)

    def get_text(self):
        index_list = [x for x in range(len(self.button_list)) if self.button_list[x].isChecked()]
        if index_list:
            index = index_list[0]
            if self.meta.get("num"):
                return str(index + 1)
            else:
                return self.button_list[index].get_text()
        else:
            return ""


class q2RadioButton(QRadioButton):
    def __init__(self, text, radio: q2radio):
        super().__init__(text)
        self.radio = radio
        self.toggled.connect(self.value_changed)
        self.setContentsMargins(0, 0, 0, 0)

    def value_changed(self, value):
        return self.radio.valid()

    def get_text(self):
        return self.text()
