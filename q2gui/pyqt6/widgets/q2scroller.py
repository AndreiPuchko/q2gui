import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()

from PyQt6.QtWidgets import QScrollArea


class q2scroller(QScrollArea):
    def __init__(self, meta):
        super().__init__(None)
        self.meta = meta
        self.setWidgetResizable(True)
        self.setWidget(self.meta["widget"])
