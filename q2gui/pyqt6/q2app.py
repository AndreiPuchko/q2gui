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
from PyQt6.QtGui import QFontMetrics, QIcon, QFont, QBrush

from q2gui.pyqt6.q2window import Q2QtWindow
from q2gui.pyqt6.q2window import layout
from q2gui.q2colors import Q2Colors
import q2gui.q2app as q2app


class Q2App(QMainWindow, q2app.Q2App, Q2QtWindow):
    class Q2TabWidget(QTabWidget):
        def __init__(self, parent):
            super().__init__(parent)
            self.main_window: Q2App = parent
            self.addTab(QWidget(), "")
            self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            self.addTabButton = QToolButton(self)
            self.addTabButton.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
            self.addTabButton.setText("+")
            self.addTabButton.clicked.connect(self.addTab)
            self.tabBar().setTabButton(0, QTabBar.ButtonPosition.RightSide, self.addTabButton)
            self.tabBar().setTabEnabled(0, False)
            self.prev_index = None
            self.tab_focus_widget = {}

            self.closeButton = QToolButton(self)
            self.closeButton.setText("x")
            self.closeButton.clicked.connect(self.closeSubWindow)
            self.setCornerWidget(self.closeButton)
            self.currentChanged.connect(self.restore_tab_focus_widget)

        def save_tab_focus_widget(self, widget):
            self.tab_focus_widget[self.currentIndex()] = widget

        def restore_tab_focus_widget(self):
            focus_widget = self.tab_focus_widget.get(self.currentIndex(), self)
            if focus_widget:
                focus_widget.setFocus()

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
                widget.setBackground(QBrush(int(self.main_window.colors["background"].replace("#", "0x"), 16)))
                widget.form_level = 0
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
        self.q2_tabwidget = self.Q2TabWidget(self)
        self.q2_toolbar = QToolBar(self)
        Q2QtWindow.__init__(self)
        q2app.Q2App.__init__(self)
        if not hasattr(QApplication, "_mw_count"):
            QApplication._mw_count = 0
            QApplication._mw_list = []
        QApplication._mw_count += 1
        QApplication._mw_list.append(self)
        self.closing = False
        self.setCentralWidget(QWidget(self))
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

        self.colors = {
            "color": "#fff",
            "color_disabled": "#777",
            "color_selection": "#000",
            "color_selectted_item": "#111",

            "background": "#282828",
            "background_control": "#555",
            "background_focus": "#005599",
            "background_selection": "#fff",
            "background_selected_item": "#CCC",

            "border": "1px solid #666",
            "border_focus": "2px solid yellow",
        }

        self.set_font(font_size=12)
        self.set_style_sheet("")
        style = """
                * {{
                    color: {color};
                    background-color: {background};
                    border: 1px solid {border};
                }}

                *:disabled {{color: {color_disabled};}}

                QAbstractButton, QTabBar:tab, QLineEdit, QComboBox:!editable
                    {{
                        background-color: {background_control};
                        selection-color: {color_selection};
                        selection-background-color : {background_selection};
                        padding-left: 6px;
                        padding-right: 6px;

                    }}

                QMenu
                    {{
                        color: palette(text);
                        background-color: palette(base);
                        selection-color: palette(highlighttext);
                        selection-background-color: #B0E2FF;
                    }}

                QMenuBar
                    {{
                        background-color: {background};
                    }}

                QMenuBar::item:selected
                    {{
                        color: {color_selection};
                        background-color: {background_selection};
                    }}

                QListView:selected, QWidget:focus, QTabBar:focus
                    {{
                        background-color: {background_focus};
                        border: {border_focus};
                    }}

                QTabWidget::pane
                    {{
                        border: 1px solid {background_selected_item};
                    }}

                QTabBar:tab::selected, QRadioButton:checked
                    {{
                        background-color: {background_selected_item};
                        color: {color_selectted_item};
                        padding-left: 6px;
                        padding-right: 6px;
                        border: none;
                    }}
                QLabel {{border:none;}}

                QTableView
                    {{
                    alternate-background-color:{background};
                    }}

                QHeaderView::section, QTableView:focus
                    {{
                        background-color:{background_control};
                    }}

                QTableView:item::selected
                    {{
                        color: {color};
                        background-color:{background_focus};
                    }}

                QTableView QTableCornerButton::section,
                QTableWidget QTableCornerButton::section
                    {{
                        background-color:{background_control}; 
                        border:none;
                    }}

                QSplitter::handle::vertical  {{
                    background-color: 
                    qlineargradient(x1: 0, y1:0, 
                                    x2: 1, y2:0,
                                    stop: 0 white, 
                                    stop: 0.5 darkblue,
                                    stop: 1 white);
                                }}

                QSplitter::handle::horizontal  {{
                    background-color: 
                    qlineargradient(x1: 0, y1:0,
                                    x2: 0, y2:1,
                                    stop: 0 white, 
                                    stop: 0.5 darkblue, 
                                    stop: 1 white);}}

                QSplitter::handle:vertical   {{height: 4px ; width: 2px;}}

                QWidget {{border-radius:5px; }}

                /*QToolButton {{color:red}}*/
                """.format(
            **self.colors
        )
        self.add_style_sheet(style)

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

    def focus_widget(self):
        return QApplication.focusWidget()

    def get_clipboard_text(self):
        return QApplication.clipboard().text()

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
