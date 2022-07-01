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
    QToolBar,
    QFileDialog,
    QTabWidget,
    QTabBar,
    QMdiArea,
    QSizePolicy,
)

from PyQt6.QtCore import QEvent, Qt, QCoreApplication, QTimer
from PyQt6.QtGui import QFontMetrics, QIcon

from q2gui.pyqt6.q2window import Q2QtWindow
from q2gui.pyqt6.q2window import layout
import q2gui.q2app as q2app


class Q2App(QMainWindow, q2app.Q2App, Q2QtWindow):
    class Q2TabWidget(QTabWidget):
        def __init__(self, parent):
            super().__init__(parent)
            self.main_window = parent
            self.addTab(QWidget(), "")
            self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            self.addTabButton = QToolButton(self)
            self.addTabButton.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
            self.addTabButton.setText("+")
            self.addTabButton.clicked.connect(self.addTab)
            self.tabBar().setTabButton(0, QTabBar.ButtonPosition.RightSide, self.addTabButton)
            self.tabBar().setTabEnabled(0, False)

            self.closeButton = QToolButton(self)
            self.closeButton.setText("x")
            self.closeButton.clicked.connect(self.closeSubWindow)
            self.setCornerWidget(self.closeButton)
            self.currentChanged.connect(self._currentChanged)

        def _currentChanged(self, index: int):
            # bug path when subwindow in tab 0 lost focus if we close subwindow in other tab
            if index == 0 and self.currentWidget().subWindowList():
                self.currentWidget().subWindowList()[-1].setFocus()

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
                widget.setOption(QMdiArea.AreaOption.DontMaximizeSubWindowOnActivation)
                widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

            self.insertTab(self.count() - 1, widget, label)
            self.setCurrentIndex(self.count() - 2)
            if self.count() > 1:
                self.main_window.on_new_tab()

    def __init__(self, title=""):
        if QCoreApplication.startingUp():  # one and only QApplication allowed
            self.QApplication = QApplication([])
        QMainWindow.__init__(self)
        if not hasattr(QApplication, "_mw_count"):
            QApplication._mw_count = 0
            QApplication._mw_list = []
        QApplication._mw_count += 1
        QApplication._mw_list.append(self)
        self.closing = False
        self.q2_toolbar = QToolBar(self)
        self.q2_tabwidget = self.Q2TabWidget(self)
        self.setCentralWidget(QWidget(self))
        self.centralWidget().setLayout(layout("v"))
        self.centralWidget().layout().addWidget(self.q2_toolbar)
        self.centralWidget().layout().addWidget(self.q2_tabwidget)
        self.statusBar().setVisible(True)
        self.set_title(title)

        super().__init__(title)
        QApplication.instance().focusChanged.connect(self.focus_changed)

        # replace static methods for instance
        self.get_open_file_dialoq = self._get_open_file_dialoq
        self.get_save_file_dialoq = self._get_save_file_dialoq

    def get_self(self):
        if QApplication.activeWindow():
            return QApplication.activeWindow()
        else:
            return self

    def show_form(self, form=None, modal="modal"):
        if modal == "":  # mdiarea normal window
            self.q2_tabwidget.currentWidget().addSubWindow(form)
            form.show()
        else:  # mdiarea modal window
            prev_focus_widget = QApplication.focusWidget()
            prev_mdi_window = self.q2_tabwidget.currentWidget().activeSubWindow()
            prev_tabbar_text = self.get_tabbar_text()

            if prev_mdi_window:
                prev_mdi_window.setDisabled(True)

            self.q2_tabwidget.currentWidget().addSubWindow(form)

            self.set_tabbar_text(form.window_title)

            if modal == "super":  # real modal dialog
                self.disable_toolbar(True)
                self.disable_menubar(True)
                self.disable_tabbar(True)
            form.exec()

            if modal == "super":  # real modal dialog
                self.disable_toolbar(False)
                self.disable_menubar(False)
                self.disable_tabbar(False)

            if prev_mdi_window:
                prev_mdi_window.setEnabled(True)

            if prev_focus_widget is not None:
                prev_focus_widget.setFocus()
                # print(prev_focus_widget)
            self.set_tabbar_text(prev_tabbar_text)

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

    def focus_widget(self):
        return QApplication.focusWidget()

    def set_style_sheet(self, style=None):
        file_name = self.style_file
        if isinstance(style, str):
            if os.path.isfile(style):
                file_name = style
            else:
                file_name = ""
        if os.path.isfile(file_name):
            try:
                with open(file_name, "r") as style_data:
                    self.setStyleSheet(style_data.read())
            except Exception:
                print(f"File {file_name} reading error...")
        elif isinstance(style, str):
            self.setStyleSheet(style)

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
    def get_open_file_dialoq(header="Open file", path="", filter=""):
        return QFileDialog.getOpenFileName(None, header, path, filter)

    def _get_open_file_dialoq(self, header="Open file", path="", filter=""):
        rez = Q2App.get_open_file_dialoq(header, path, filter)
        # self.QApplication.setActiveWindow(self)
        QApplication.setActiveWindow(self)
        return rez

    @staticmethod
    def get_save_file_dialoq(header="Save file", path="", filter=""):
        return QFileDialog.getSaveFileName(None, header, path, filter)

    def _get_save_file_dialoq(self, header="Save file", path="", filter=""):
        rez = Q2App.get_save_file_dialoq(header, path, filter)
        # self.QApplication.setActiveWindow(self)
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
