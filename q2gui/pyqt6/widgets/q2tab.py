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


from PyQt6.QtWidgets import QTabBar, QTabWidget
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtCore import Qt

from q2gui.pyqt6.q2window import Q2Frame
from q2gui.pyqt6.q2widget import Q2Widget
from q2gui.q2utils import int_


class Q2TabBar(QTabBar, Q2Widget):
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

    def set_enabled(self, mode=True):
        self.tabBar().setEnabled(mode)

    def set_disabled(self, mode=True):
        self.tabBar().setDisabled(mode)

    def set_tab(self, index=0):
        if isinstance(index, str):
            for x in range(self.tabBar().count()):
                if self.tabBar().tabText(x) == index:
                    index = x
                    break
        else:
            index = int_(index)
            if index >= self.count():
                index = self.count() - 1
            elif index < 0:
                index = 0
        self.setCurrentIndex(index)

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
