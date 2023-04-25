if __name__ == "__main__":
    import sys

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()


# from q2gui import q2form

import os

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QToolButton,
    QPushButton,
    QToolBar,
    QFileDialog,
    QTabWidget,
    QTabBar,
    QMdiArea,
    QSizePolicy,
)

from PyQt6.QtCore import QEvent, Qt, QCoreApplication, QTimer
from PyQt6.QtGui import QFontMetrics, QIcon, QFont, QBrush, QColor

from q2gui.pyqt6.q2window import Q2QtWindow
from q2gui.pyqt6.q2window import layout
from q2gui.pyqt6.q2style import Q2Style

import q2gui.q2app as q2app


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

            self.closeButton = QToolButton(self)
            self.closeButton.setText("❌")
            self.closeButton.clicked.connect(self.closeSubWindow)
            self.setCornerWidget(self.closeButton)
            self.currentChanged.connect(self.restore_tab_focus_widget)

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

        # def _currentChanged(self, index: int):
        #     self.restore_tab_focus_widget()

        def closeSubWindow(self):
            currentTabIndex = self.currentIndex()
            if self.currentWidget().activeSubWindow():
                self.currentWidget().activeSubWindow().close()
            elif self.count() > 2:  # close tab if them >2
                self.setCurrentIndex(currentTabIndex - 1)
                self.removeTab(currentTabIndex)

        def addTab(self, widget=None, label="="):
            if not widget:
                widget = QMdiArea(self)
                widget.setBackground(
                    QBrush(QColor(self.main_window.q2style.get_style("background_disabled")))
                )
                widget.form_level = 0
                widget.setOption(QMdiArea.AreaOption.DontMaximizeSubWindowOnActivation)
                widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

            self.insertTab(self.count() - 1, widget, label)
            self.setCurrentIndex(self.count() - 2)
            if self.count() > 1:
                self.main_window.on_new_tab()

        def set_tabs_backround_color(self):
            for x in range(self.count()):
                if isinstance(self.widget(x), QMdiArea):
                    self.widget(x).setBackground(
                        QBrush(QColor(self.main_window.q2style.get_style("background_disabled")))
                    )

    def __init__(self, title=""):
        if QCoreApplication.startingUp():  # one and only QApplication allowed
            self.QApplication = QApplication([])
        QMainWindow.__init__(self)
        Q2QtWindow.__init__(self)
        self.q2_tabwidget = self.Q2TabWidget(self)
        self.q2_toolbar = QToolBar(self)

        self.Q2Style = Q2Style
        q2app.Q2App.__init__(self)

        if not hasattr(QApplication, "_mw_count"):
            QApplication._mw_count = 0
            QApplication._mw_list = []
        QApplication._mw_count += 1
        QApplication._mw_list.append(self)
        self.closing = False
        self.setCentralWidget(QWidget(self))
        self.centralWidget().setObjectName("central_widget")
        self.centralWidget().setLayout(layout("v"))
        self.centralWidget().layout().addWidget(self.q2_toolbar)
        self.centralWidget().layout().addWidget(self.q2_tabwidget)
        self.statusBar().setVisible(True)
        self.set_title(title)

        # super().__init__(title)
        QApplication.instance().focusChanged.connect(self.focus_changed)
        QApplication.instance().focusChanged.connect(self.save_tab_focus_widget)

        # replace static methods for instance
        self.get_open_file_dialoq = self._get_open_file_dialoq
        self.get_save_file_dialoq = self._get_save_file_dialoq
        self._last_get_file_path = None

    def set_font(self, font_name="", font_size=12):
        QApplication.setFont(QFont(font_name, font_size))

    def save_tab_focus_widget(self):
        self.q2_tabwidget.save_tab_focus_widget(self.focus_widget())

    def get_self(self):
        if QApplication.activeWindow():
            return QApplication.activeWindow()
        else:
            return self

    def eventFilter(self, obj, ev: QEvent):
        if ev.type() == QEvent.Type.Close:
            if obj.heap.prev_mdi_window:
                obj.heap.prev_mdi_window.setEnabled(True)

            if obj.heap.prev_focus_widget is not None and not isinstance(obj.heap.prev_focus_widget, QTabBar):
                # print(obj.heap.prev_focus_widget)
                try:
                    obj.heap.prev_focus_widget.setFocus()
                except Exception:
                    pass
            self.set_tabbar_text(obj.heap.prev_tabbar_text)
            if obj.heap.modal == "super":  # real modal dialog
                self.disable_toolbar(False)
                self.disable_menubar(False)
                self.disable_tabbar(False)

        return super().eventFilter(obj, ev)

    def show_form(self, form=None, modal="modal"):
        form.heap = q2app.Q2Heap()
        form.heap.modal = modal
        form.heap.prev_mdi_window = self.q2_tabwidget.currentWidget().activeSubWindow()
        form.heap.prev_focus_widget = QApplication.focusWidget()
        form.heap.prev_tabbar_text = self.get_tabbar_text()

        self.q2_tabwidget.currentWidget().addSubWindow(form)
        form.installEventFilter(self)

        if modal != "" and form.heap.prev_mdi_window:  # mdiarea normal window
            form.heap.prev_mdi_window.setDisabled(True)

        self.set_tabbar_text(form.window_title)

        if modal == "super":  # real modal dialog
            self.disable_toolbar(True)
            self.disable_menubar(True)
            self.disable_tabbar(True)
        if modal == "":  # mdiarea normal window
            form.show()
        else:
            form.exec()

    def disable_current_form(self, mode=True):
        if self.q2_tabwidget.currentWidget().subWindowList():
            prev_mdi_window = self.q2_tabwidget.currentWidget().subWindowList()[-1]
            if prev_mdi_window:
                prev_mdi_window.setDisabled(mode)
                prev_mdi_window.setFocus()

    def build_menu(self):
        self.menu_list = super().reorder_menu(self.menu_list)
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
                self._main_menu[_path].triggered.connect(x["WORKER"])

                icon = self.get_icon(x["ICON"])
                if icon:
                    self._main_menu[_path].setIcon(QIcon(icon))

                if x["TOOLBAR"]:
                    button = QToolButton(self)
                    button.setText(topic)
                    button.setDefaultAction(self._main_menu[_path])
                    self.q2_toolbar.addAction(self._main_menu[_path])
            else:
                self._main_menu[_path] = node.addMenu(topic)
        # Show as context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.addActions(self.menuBar().actions())

    def set_color_mode(self, color_mode=None):
        q2app.Q2App.set_color_mode(self, color_mode)
        self.q2_tabwidget.set_tabs_backround_color()

    def focus_widget(self):
        return QApplication.focusWidget()

    def get_clipboard_text(self):
        return QApplication.clipboard().text()

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

    def show_tabbar(self, mode=True):
        q2app.Q2App.show_tabbar(self)
        if mode:
            self.q2_tabwidget.tabBar().show()
        else:
            self.q2_tabwidget.tabBar().hide()

    def is_tabbar_visible(self):
        return self.q2_tabwidget.tabBar().isVisible()

    def get_tabbar_text(self):
        return self.q2_tabwidget.tabBar().tabText(self.q2_tabwidget.currentIndex())

    def show_statusbar_mess(self, text=""):
        self.statusBar().showMessage(f"{text}")

    def set_tabbar_text(self, text=""):
        self.q2_tabwidget.tabBar().setTabText(self.q2_tabwidget.currentIndex(), text)

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
            pass
        self.process_events()
        self.add_new_tab()
        self.process_events()
        self.on_start()

    def keyboard_modifiers(self):
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
        QTimer.singleShot(111, self._wait_for_show)
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
        super().close()
        QApplication._mw_count -= 1
        QMainWindow.close(self)
        if QApplication._mw_count <= 0:
            os._exit(0)
