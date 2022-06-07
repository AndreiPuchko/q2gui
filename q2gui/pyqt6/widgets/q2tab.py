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

        self.next_tab_hotkey = QShortcut(QKeySequence("Ctrl+PgDown"), self)
        self.next_tab_hotkey.activated.connect(lambda tab=self: self.setCurrentIndex(self.currentIndex()+1))

        self.prev_tab_hotkey = QShortcut(QKeySequence("Ctrl+PgUp"), self)
        self.prev_tab_hotkey.activated.connect(lambda tab=self: tab.setCurrentIndex(tab.currentIndex() - 1))

    def set_shortcuts_local(self):
        self.next_tab_hotkey.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.prev_tab_hotkey.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)

    def add_tab(self, widget, text=""):
        self.addTab(widget, text)

    def get_text(self):
        return self.tabBar().tabText(self.currentIndex())
