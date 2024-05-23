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


# from q2gui import q2form

import os

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QToolButton,
    QToolBar,
    QFileDialog,
    QTabWidget,
    QTabBar,
    QSplitter,
    QMdiArea,
    QMdiSubWindow,
    QHBoxLayout,
)

from PyQt6.QtCore import QEvent, Qt, QCoreApplication, QTimer, QRectF
from PyQt6.QtGui import (
    QFontMetrics,
    QIcon,
    QFont,
    QBrush,
    QColor,
    QShortcut,
    QKeySequence,
    QAction,
    QPixmap,
    QPainter,
)

from q2gui.pyqt6.q2window import Q2QtWindow
from q2gui.pyqt6.q2style import Q2Style
from q2gui.pyqt6.widgets.q2frame import q2frame
from q2gui.pyqt6.widgets.q2text import q2text
from q2gui.pyqt6.widgets.q2button import q2button
from q2gui.q2utils import int_


import q2gui.q2app as q2app


class stdout_widget(q2frame):
    def __init__(self, mode="h"):
        super().__init__({"column": "/h", "label": "Output"})
        self.stdout_widget = q2text(self.make_meta({}))

        self.toolbar_frame = q2frame({"column": "/v"})
        self.closeButton = q2button(self.make_meta(column="hide", label="❌", mess="Hide output"))
        self.closeButton.clicked.connect(lambda: self.hide())

        self.cleanButton = q2button(self.make_meta(label="🧹", mess="Clean output"))
        self.cleanButton.clicked.connect(lambda: [self.stdout_widget.clear(), self.stdout_widget.set_focus()])

        self.toolbar_frame.insert_widget(widget=self.closeButton)
        self.toolbar_frame.insert_widget(widget=self.cleanButton)

        self.insert_widget(widget=self.stdout_widget)
        self.insert_widget(widget=self.toolbar_frame)
        self.setVisible(False)
        self.setStyleSheet("margin: 0.5em 2px 2px 2px; padding:1px")

    def write(self, text):
        if not self.isVisible():
            self.setVisible(True)
        from PyQt6.QtGui import QTextCursor

        self.stdout_widget.moveCursor(QTextCursor.MoveOperation.End)
        q2app.q2_app.process_events()
        self.stdout_widget.insertPlainText(text)


class Q2Toolbars:
    def __init__(self, q2_app):
        self.toolbars = {}
        self.q2_app: Q2App = q2_app
        self.visible = True

    def clear(self):
        for toolbar in self.toolbars:
            x, y = self.toolbars[toolbar].pos().x(), self.toolbars[toolbar].pos().y()
            floating = self.toolbars[toolbar].isFloating()
            area = self.q2_app.toolBarArea(self.toolbars[toolbar]).value
            # orientation = self.toolbars[toolbar].orientation().value
            self.q2_app.settings.set(f"toolbar-{toolbar}", "x", f"{x}")
            self.q2_app.settings.set(f"toolbar-{toolbar}", "y", f"{y}")
            self.q2_app.settings.set(f"toolbar-{toolbar}", "floating", f"{floating}")
            self.q2_app.settings.set(f"toolbar-{toolbar}", "area", f"{area}")
            # self.q2_app.settings.set(f"toolbar-{toolbar}", "orientation", f"{orientation}")
            self.toolbars[toolbar].clear()
            self.q2_app.removeToolBar(self.toolbars[toolbar])
        self.toolbars = {}

    def move(self, pos, old_pos):
        delta_x = pos.x() - old_pos.x()
        delta_y = pos.y() - old_pos.y()

        for toolbar in self.toolbars:
            if self.toolbars[toolbar].isFloating():
                pos_x = self.toolbars[toolbar].pos().x()
                pos_y = self.toolbars[toolbar].pos().y()
                self.toolbars[toolbar].move(pos_x + delta_x, pos_y + delta_y)

    def addAction(self, action, toolbar=""):
        if toolbar not in self.toolbars:
            self.toolbars[toolbar] = QToolBar()
            x = int_(self.q2_app.settings.get(f"toolbar-{toolbar}", "x", None))
            y = int_(self.q2_app.settings.get(f"toolbar-{toolbar}", "y", None))
            floating = self.q2_app.settings.get(f"toolbar-{toolbar}", "floating", None)
            area = self.q2_app.settings.get(f"toolbar-{toolbar}", "area", None)
            # orientation = self.q2_app.settings.get(f"toolbar-{toolbar}", "orientation", None)
            if area:
                if area == "ToolBarArea.TopToolBarArea":
                    area = Qt.ToolBarArea.TopToolBarArea
                elif area == "ToolBarArea.BottomToolBarAre":
                    area = Qt.ToolBarArea.BottomToolBarArea
                elif area == "ToolBarArea.LeftToolBarArea":
                    area = Qt.ToolBarArea.LeftToolBarArea
                elif area == "ToolBarArea.RightToolBarArea":
                    area = Qt.ToolBarArea.RightToolBarArea
                elif area.isdigit():
                    area = int(area)
                    if area == Qt.ToolBarArea.TopToolBarArea.value:
                        area = Qt.ToolBarArea.TopToolBarArea
                    elif area == Qt.ToolBarArea.BottomToolBarArea.value:
                        area = Qt.ToolBarArea.BottomToolBarArea
                    elif area == Qt.ToolBarArea.LeftToolBarArea.value:
                        area = Qt.ToolBarArea.LeftToolBarArea
                    elif area == Qt.ToolBarArea.RightToolBarArea.value:
                        area = Qt.ToolBarArea.RightToolBarArea
                    else:
                        area = Qt.ToolBarArea.TopToolBarArea
            if area is not None:
                self.q2_app.addToolBar(area, self.toolbars[toolbar])
            else:
                self.q2_app.addToolBar(self.toolbars[toolbar])
            if floating == "True":
                self.toolbars[toolbar].setWindowFlags(
                    Qt.WindowType.Tool
                    | Qt.WindowType.FramelessWindowHint
                    | Qt.WindowType.X11BypassWindowManagerHint
                )
                self.toolbars[toolbar].move(int(x), int(y))
                self.toolbars[toolbar].setOrientation(Qt.Orientation.Horizontal)
        if isinstance(action, QAction):
            self.toolbars[toolbar].addAction(action)
        elif isinstance(action, QToolButton):
            self.toolbars[toolbar].addWidget(action)

    def isVisible(self):
        return self.visible

    def isEnabled(self):
        toolbars_flag = [self.toolbars[x].isEnabled() for x in self.toolbars]
        if toolbars_flag:
            return max(toolbars_flag)
        else:
            return False

    def hide(self):
        for x in self.toolbars:
            self.toolbars[x].hide()
        self.visible = False

    def show(self):
        for x in self.toolbars:
            self.toolbars[x].show()
        self.visible = True

    def setDisabled(self, mode):
        for x in self.toolbars:
            self.toolbars[x].setDisabled(mode)


class Q2App(QMainWindow, q2app.Q2App, Q2QtWindow):
    class Q2TabWidget(QTabWidget):
        def __init__(self, parent):
            super().__init__(parent)
            self.main_window: Q2App = parent
            self.addTab(QWidget(), "+")
            self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            self.setObjectName("main_tab_widget")
            self.prev_index = None
            self.tab_focus_widget = {}
            self.tabBar().setObjectName("main_tab_bar")

            self.corner_widget = QWidget()
            self.corner_widget.setLayout(QHBoxLayout())

            self.closeButton = QToolButton(self)
            self.closeButton.setText("❌")
            self.closeButton.setContentsMargins(0, 0, 0, 0)
            self.closeButton.clicked.connect(self.closeSubWindow)

            self.restore_button = QToolButton(self)
            self.restore_button.setText("🗗")
            self.restore_button.setContentsMargins(0, 0, 0, 0)
            self.restore_button.clicked.connect(self.show_mdi_normal)
            self.show_mdi_normal_button(False)

            self.corner_widget.layout().setContentsMargins(0, 0, 0, 0)
            self.corner_widget.layout().setAlignment(Qt.AlignmentFlag.AlignRight)
            self.corner_widget.layout().addWidget(self.restore_button)
            self.corner_widget.layout().addWidget(self.closeButton)
            self.setCornerWidget(self.corner_widget)

            self.currentChanged.connect(self.restore_tab_focus_widget)

        def hide(self) -> None:
            self.tabBar().setDisabled(True)
            self.tabBar().setTabVisible(self.tabBar().count() - 1, False)
            # self.tabBar().hide()
            # self.closeButton.hide()
            # return super().hide()

        def show(self) -> None:
            self.tabBar().setEnabled(True)
            self.tabBar().setTabVisible(self.tabBar().count() - 1, True)
            self.setUpdatesEnabled(False)
            self.tabBar().hide()
            self.tabBar().show()
            self.setUpdatesEnabled(True)
            # self.tabBar().show()
            # self.closeButton.show()
            # return super().show()

        def save_tab_focus_widget(self, widget):
            self.tab_focus_widget[self.currentIndex()] = widget

        def restore_tab_focus_widget(self):
            if self.currentIndex() == self.count() - 1:
                self.addTab()
                return
            focus_widget = self.tab_focus_widget.get(self.currentIndex(), self)
            if focus_widget:
                try:
                    focus_widget.setFocus()
                except Exception:
                    pass

        def closeSubWindow(self):
            currentTabIndex = self.currentIndex()
            if self.currentWidget().activeSubWindow():
                self.currentWidget().activeSubWindow().close()
            elif self.count() > 2:  # close tab if them >2
                self.setCurrentIndex(currentTabIndex - 1)
                self.removeTab(currentTabIndex)

        def show_mdi_normal(self):
            self.currentWidget().activeSubWindow().showNormal()
            self.currentWidget().activeSubWindow().setWindowFlag(Qt.WindowType.FramelessWindowHint, False)

        def show_mdi_normal_button(self, mode=False):
            self.restore_button.setVisible(mode)

        def get_subwindow_count(self):
            return sum([len(self.widget(x).subWindowList()) for x in range(self.count() - 1)])

        def addTab(self, widget=None, label=" = "):
            if not widget:
                widget = QMdiArea(self)
                self.set_tab_background(widget)
                widget.form_level = 0
                widget.setOption(QMdiArea.AreaOption.DontMaximizeSubWindowOnActivation)
                widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

            self.insertTab(self.count() - 1, widget, label)
            self.setCurrentIndex(self.count() - 2)
            if self.count() > 1:
                self.main_window.on_new_tab()

        def set_tab_background(self, widget):
            if isinstance(widget, QMdiArea):
                if self.main_window.q2style.color_mode == "clean":
                    widget.setBackground(QBrush(QApplication.palette().dark()))
                else:
                    widget.setBackground(
                        QBrush(QColor(self.main_window.q2style.get_style("background_disabled")))
                    )

        def set_tabs_backround(self):
            for x in range(self.count()):
                self.set_tab_background(self.widget(x))

    def __init__(self, title=""):
        if QCoreApplication.startingUp():  # one and only QApplication allowed
            self.QApplication = QApplication([])
            self.QApplication.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeMenuBar)
        QMainWindow.__init__(self)
        Q2QtWindow.__init__(self)
        self.q2_tabwidget = self.Q2TabWidget(self)
        # self.q2_toolbar = QToolBar(self)
        self.q2_toolbar = Q2Toolbars(self)
        self.stdout_widget = stdout_widget()

        self.Q2Style = Q2Style
        q2app.Q2App.__init__(self)

        if not hasattr(QApplication, "_mw_count"):
            QApplication._mw_count = 0
            QApplication._mw_list = []
        QApplication._mw_count += 1
        QApplication._mw_list.append(self)
        self.closing = False

        self.central_widget = QSplitter(Qt.Orientation.Vertical)
        self.setCentralWidget(self.central_widget)
        self.centralWidget().setObjectName("central_widget")

        # self.addToolBar(self.q2_toolbar)

        self.central_widget.addWidget(self.q2_tabwidget)
        self.central_widget.addWidget(self.stdout_widget)
        self.central_widget.setSizes([10])

        self.statusBar().setVisible(True)
        self.set_title(title)

        QApplication.instance().focusChanged.connect(self.focus_changed)
        QApplication.instance().focusChanged.connect(self.save_tab_focus_widget)

        self.next_tab_shortcut = QShortcut(QKeySequence("Ctrl+Tab"), self)
        self.prev_tab_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Tab"), self)
        self.next_tab_shortcut.activated.connect(
            lambda: (
                self.q2_tabwidget.setCurrentIndex(self.q2_tabwidget.currentIndex() + 1)
                if self.q2_tabwidget.tabBar().isVisible()
                else None
            )
        )
        self.prev_tab_shortcut.activated.connect(
            lambda: (
                self.q2_tabwidget.setCurrentIndex(self.q2_tabwidget.currentIndex() - 1)
                if self.q2_tabwidget.tabBar().isVisible()
                else None
            )
        )

        # replace static methods for instance
        self.get_open_file_dialoq = self._get_open_file_dialoq
        self.get_save_file_dialoq = self._get_save_file_dialoq
        self._last_get_file_path = None

    def set_clipboard(self, text):
        QApplication.clipboard().setText(text)

    def get_stdout_height(self):
        return self.stdout_widget.height()

    def set_font(self, font_name="", font_size=12):
        QApplication.setFont(QFont(font_name, font_size))

    def save_tab_focus_widget(self):
        self.q2_tabwidget.save_tab_focus_widget(self.focus_widget())

    def get_self(self):
        if QApplication.activeWindow():
            return QApplication.activeWindow()
        else:
            return self

    def subwindow_count_changed(self):
        return self.q2_tabwidget.get_subwindow_count()

    def disable_menu(self, menu_path=""):
        action = self._main_menu.get(menu_path)
        if action:
            action.setDisabled(True)

    def enable_menu(self, menu_path=""):
        action = self._main_menu.get(menu_path)
        if action:
            action.setEnabled(True)

    def eventFilter(self, obj, ev: QEvent):
        if ev.type() == QEvent.Type.Close:
            if not obj.isEnabled():
                ev.ignore()
                return True
        return super().eventFilter(obj, ev)

    def moveEvent(self, ev):
        self.q2_toolbar.move(ev.pos(), ev.oldPos())
        return super().moveEvent(ev)

    def show_form(self, form=None, modal="modal"):
        # form.heap = q2app.Q2Heap()
        form.heap.modal = modal
        form.heap.prev_mdi_window = self.q2_tabwidget.currentWidget().activeSubWindow()
        form.heap.prev_focus_widget = QApplication.focusWidget()
        form.heap.prev_tabbar_text = self.get_tabbar_text()

        form_mdi_subwindow: QMdiSubWindow = self.q2_tabwidget.currentWidget().addSubWindow(form)
        form_mdi_subwindow.setWindowIcon(self.windowIcon())
        tmp_icon = QPixmap(1, 1)
        tmp_icon.fill(Qt.GlobalColor.transparent)
        form_mdi_subwindow.setWindowIcon(QIcon(tmp_icon))

        form.installEventFilter(self)
        self.subwindow_count_changed()

        if modal != "" and form.heap.prev_mdi_window:  # mdiarea normal window
            form.heap.prev_mdi_window.setDisabled(True)

        self.set_tabbar_text(form.window_title)

        if modal == "":  # mdiarea normal window
            form.show()
        else:
            if modal == "super":  # real modal dialog
                form.heap.prev_toolbar_enabled = self.is_toolbar_enabled()
                form.heap.prev_menubar_enabled = self.is_menubar_enabled()
                form.heap.prev_tabbar_enabled = self.is_tabbar_enabled()
                self.disable_toolbar(True)
                self.disable_menubar(True)
                self.disable_tabbar(True)
            form.exec()
            if modal == "super":  # real modal dialog
                self.enable_toolbar(form.heap.prev_toolbar_enabled)
                self.enable_menubar(form.heap.prev_menubar_enabled)
                self.enable_tabbar(form.heap.prev_tabbar_enabled)
        self.subwindow_count_changed()

    def dpi(self):
        return self.physicalDpiX()

    def disable_current_form(self, mode=True):
        if self.q2_tabwidget.currentWidget().subWindowList():
            prev_mdi_window = self.q2_tabwidget.currentWidget().subWindowList()[-1]
            if prev_mdi_window:
                prev_mdi_window.setDisabled(mode)
                prev_mdi_window.setFocus()

    def build_menu(self):
        # self.menu_list = super().reorder_menu(self.menu_list)
        super().build_menu()
        self._main_menu = {}
        QMainWindow.menuBar(self).clear()
        self.q2_toolbar.clear()
        QMainWindow.menuBar(self).show()
        for x in self.menu_list:
            _path = x["TEXT"]
            if _path == "" or _path in self._main_menu:
                continue
            prevNode = "|".join(_path.split("|")[:-1])
            topic = _path.split("|")[-1]
            if _path.count("|") == 0:  # first in chain - menu bar
                node = QMainWindow.menuBar(self)
            else:
                node = self._main_menu.get(prevNode)
                if node is None:
                    node = QMainWindow.menuBar(self)
            if _path.endswith("-"):
                node.addSeparator()
            elif x["WORKER"]:
                self._main_menu[_path] = node.addAction(topic)
                self._main_menu[_path].setMenuRole(QAction.MenuRole.NoRole)
                self._main_menu[_path].triggered.connect(x["WORKER"])

                self._main_menu[_path].setIcon(self.get_engine_icon(x["ICON"]))

                if x["TOOLBAR"]:
                    self.q2_toolbar.addAction(self._main_menu[_path], _path.split("|")[0])
            else:
                self._main_menu[_path] = node.addMenu(topic)
        # Show as context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        for a in self.actions():
            self.removeAction(a)
        self.addActions(self.menuBar().actions())

    def get_engine_icon(self, icon_text):
        if icon_text is None:
            return QIcon()
        elif self.get_icon(icon_text):
            return QIcon(self.get_icon(icon_text))
        tmp_icon = self.get_icon(q2app.GRID_ACTION_ICON)
        icon_size = QIcon(tmp_icon).availableSizes()[0].width()
        font = QFont("Arial")
        font.setWeight(QFont.Weight.Bold)
        font.setPixelSize(icon_size)

        if len(icon_text) == 1:
            pix = QPixmap(icon_size, icon_size)
            pix.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pix)
            painter.setFont(font)
            painter.drawText(
                QRectF(0, 0, icon_size, icon_size),
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter,
                icon_text[:1],
            )
            del painter
            return QIcon(pix)
        else:
            return QIcon()

    def set_color_mode(self, color_mode=None):
        q2app.Q2App.set_color_mode(self, color_mode)
        self.q2_tabwidget.set_tabs_backround()

    def focus_widget(self):
        return QApplication.focusWidget()

    def get_clipboard_text(self):
        return QApplication.clipboard().text()

    def set_clipboard_text(self, text):
        return QApplication.clipboard().setText(text)

    def set_style_sheet(self, style=None):
        if os.path.isfile(self.style_file):
            try:
                with open(self.style_file, "r") as style_data:
                    local_style = style_data.read()
            except Exception:
                local_style = ""
        else:
            local_style = ""
        self.setStyleSheet(style + local_style)

    def add_style_sheet(self, style):
        current_style = self.styleSheet() + f"{style}"
        self.setStyleSheet(current_style)

    def lock(self):
        self.menuBar().setDisabled(True)
        self.q2_toolbar.setDisabled(True)
        self.q2_tabwidget.setDisabled(True)

    def unlock(self):
        self.menuBar().setDisabled(False)
        self.q2_toolbar.setDisabled(False)
        self.q2_tabwidget.setDisabled(False)

    def set_icon(self, icon_path):
        self.icon = icon_path
        self.setWindowIcon(QIcon(self.icon))

    def process_events(self):
        QApplication.processEvents()

    def show_menubar(self, mode=True):
        q2app.Q2App.show_menubar(self)
        if mode:
            QMainWindow.menuBar(self).show()
        else:
            QMainWindow.menuBar(self).hide()

    def is_menubar_visible(self):
        return QMainWindow.menuBar(self).isVisible()

    def is_menubar_enabled(self):
        return QMainWindow.menuBar(self).isEnabled()

    def show_toolbar(self, mode=True):
        q2app.Q2App.show_toolbar(self)
        if mode:
            self.q2_toolbar.show()
        else:
            self.q2_toolbar.hide()

    def disable_toolbar(self, mode=True):
        self.q2_toolbar.setDisabled(True if mode else False)

    def disable_menubar(self, mode=True):
        QMainWindow.menuBar(self).setDisabled(True if mode else False)

    def disable_tabbar(self, mode=True):
        self.q2_tabwidget.tabBar().setDisabled(True if mode else False)

    def is_toolbar_visible(self):
        return self.q2_toolbar.isVisible()

    def is_toolbar_enabled(self):
        return self.q2_toolbar.isEnabled()

    def show_tabbar(self, mode=True):
        q2app.Q2App.show_tabbar(self)
        if mode:
            self.q2_tabwidget.show()
        else:
            self.q2_tabwidget.hide()

    def is_tabbar_visible(self):
        return self.q2_tabwidget.tabBar().isEnabled()

    def is_tabbar_enabled(self):
        return self.q2_tabwidget.tabBar().isEnabled()

    def get_tabbar_text(self):
        return self.q2_tabwidget.tabBar().tabText(self.q2_tabwidget.currentIndex())

    def show_statusbar_mess(self, text=""):
        self.statusBar().showMessage(f"{text}")

    def clear_statusbar(self):
        self.statusBar().clearMessage()

    def get_statusbar_mess(self):
        return self.statusBar().currentMessage()

    def set_tabbar_text(self, text=""):
        # text = text.strip().split("\n")[0][:50]
        self.q2_tabwidget.tabBar().setTabText(self.q2_tabwidget.currentIndex(), text)
        self.setUpdatesEnabled(False)
        self.q2_tabwidget.tabBar().hide()
        self.q2_tabwidget.tabBar().show()
        self.setUpdatesEnabled(True)

    def show_statusbar(self, mode=True):
        q2app.Q2App.show_statusbar(self)
        if mode:
            self.statusBar().show()
        else:
            self.statusBar().hide()

    def is_statusbar_visible(self):
        return self.statusBar().isVisible()

    def get_char_width(self, char="w"):
        return QFontMetrics(self.font()).horizontalAdvance(char)

    def get_char_height(self):
        return QFontMetrics(self.font()).height()

    @staticmethod
    def get_open_file_dialoq(header=q2app.DIALOG_OPEN_FILE_TITLE, path="", filter=""):
        if path == "":
            path = os.path.expanduser("~/Desktop")
        rez = QFileDialog.getOpenFileName(None, header, path, filter)
        return rez

    def _get_open_file_dialoq(self, header=q2app.DIALOG_OPEN_FILE_TITLE, path="", filter=""):
        if self._last_get_file_path and not path:
            path = self._last_get_file_path
        rez = Q2App.get_open_file_dialoq(header, path, filter)
        if rez:
            self._last_get_file_path = os.path.dirname(rez[0])
        QApplication.setActiveWindow(self)
        return rez

    @staticmethod
    def get_save_file_dialoq(header=q2app.DIALOG_SAVE_FILE_TITLE, path="", filter="", confirm_overwrite=True):
        if path == "":
            path = os.path.expanduser("~/Desktop")
        if confirm_overwrite:
            rez = QFileDialog.getSaveFileName(None, header, path, filter)
        else:
            rez = QFileDialog.getSaveFileName(
                None, header, path, filter, options=QFileDialog.Option.DontConfirmOverwrite
            )
        return rez

    def _get_save_file_dialoq(
        self, header=q2app.DIALOG_SAVE_FILE_TITLE, path="", filter="", confirm_overwrite=True
    ):
        if self._last_get_file_path and not path:
            path = self._last_get_file_path
        rez = Q2App.get_save_file_dialoq(header, path, filter, confirm_overwrite)
        if rez:
            self._last_get_file_path = os.path.dirname(rez[0])
        QApplication.setActiveWindow(self)
        return rez

    def _wait_for_show(self):
        while QApplication.activeWindow() is None:
            QTimer.singleShot(100, self._wait_for_show)
            return
        self.process_events()
        self.add_new_tab()
        self.process_events()
        self.on_start()

    def keyboard_modifiers(self):
        self.process_events()
        modifiers = QApplication.keyboardModifiers()
        rez = []
        if modifiers == Qt.KeyboardModifier.ShiftModifier:
            rez.append("shift")
        elif modifiers == Qt.KeyboardModifier.ControlModifier:
            rez.append("control")
        elif modifiers == (Qt.KeyboardModifier.AltModifier):
            rez.append("alt")
        return "+".join(rez)

    def save_geometry(self, settings):
        Q2QtWindow.save_geometry(self, settings)

    def run(self):
        # self.restore_geometry(self.settings)
        Q2QtWindow.restore_geometry(self, self.settings)
        self.show()
        super().run()
        self._wait_for_show()
        if len(QApplication.allWindows()) == 1:
            QApplication.instance().exec()

    def add_new_tab(self):
        self.q2_tabwidget.addTab()

    def show(self):
        QMainWindow.show(self)

    def on_new_tab(self):
        return super().on_new_tab()

    def showEvent(self, event):
        event.accept()
        super().showEvent(event)

    def closeEvent(self, event: QEvent):
        if not self.closing:
            self.close()
        event.accept()

    def close(self):
        self.closing = True
        self.q2_toolbar.clear()
        super().close()
        QApplication._mw_count -= 1
        QMainWindow.close(self)
        if QApplication._mw_count <= 0:
            os._exit(0)
