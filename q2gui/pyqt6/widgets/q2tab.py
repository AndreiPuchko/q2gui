import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()

from PyQt6.QtWidgets import QTabBar, QTabWidget
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtCore import Qt

from q2gui.pyqt6.q2window import Q2Frame
from q2gui.pyqt6.q2widget import Q2Widget


class Q2TabBar(QTabBar):
    def get_text(self):
        return self.tabText(self.currentIndex())


class q2tab(QTabWidget, Q2Widget, Q2Frame):
    def __init__(self, meta):
        super().__init__(meta)
        self.setTabBar(Q2TabBar())
        self.meta = meta

        self.set_tabbar_position(meta.get("alignment", 7))

        self.next_tab_hotkey = QShortcut(QKeySequence("Ctrl+PgDown"), self)
        self.next_tab_hotkey.activated.connect(self.next_tab)

        self.prev_tab_hotkey = QShortcut(QKeySequence("Ctrl+PgUp"), self)
        self.prev_tab_hotkey.activated.connect(self.prev_tab)

    def set_tabbar_position(self, pos):
        pos = str(pos)
        qss = ""
        if "4" in pos:  # left
            self.setTabPosition(QTabWidget.TabPosition.West)
            if "7" in pos:
                qss = "left"
            elif "1" in pos:
                qss = "right"
            else:
                qss = "center"
        elif "2" in pos:  # bottom
            self.setTabPosition(QTabWidget.TabPosition.South)
            if "1" in pos:
                qss = "left"
            elif "3" in pos:
                qss = "right"
            else:
                qss = "center"
        elif "6" in pos:  # right
            self.setTabPosition(QTabWidget.TabPosition.East)
            if "9" in pos:
                qss = "left"
            elif "3" in pos:
                qss = "right"
            else:
                qss = "center"
        else:
            if "9" in pos:
                qss = "right"
            elif "8" in pos:
                qss = "center"
        if qss:
            self.setStyleSheet("QTabWidget::tab-bar { alignment: %s;}" % qss)

    def next_tab(self):
        self.setCurrentIndex(self.currentIndex() + 1)

    def prev_tab(self):
        self.setCurrentIndex(self.currentIndex() - 1)

    def minimumSizeHint(self):
        self.setMinimumHeight(super().minimumSizeHint().height())
        return super().minimumSizeHint()

    def set_shortcuts_local(self):
        self.next_tab_hotkey.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.prev_tab_hotkey.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)

    def add_tab(self, widget, text=""):
        self.addTab(widget, text)

    def get_text(self):
        return self.tabBar().tabText(self.currentIndex())
