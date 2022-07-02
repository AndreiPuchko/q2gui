if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from demo.demo import demo

    demo()

from PyQt6.QtWidgets import QDialog, QMdiSubWindow, QApplication, QApplication
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QKeySequence, QKeyEvent


import q2gui.q2app as q2app
import q2gui.q2form as q2form
import q2gui.pyqt6.widgets

from q2gui.pyqt6.q2app import Q2QtWindow
from q2gui.q2utils import num

import q2gui.q2dialogs
# from q2gui.q2dialogs import q2Mess, q2Wait, q2AskYN

from q2gui.pyqt6.q2widget import Q2Widget


class Q2Form(q2form.Q2Form):
    def __init__(self, title=""):
        super().__init__(title=title)
        self._Q2FormWindow_class = Q2FormWindow
        self._q2dialogs = q2gui.q2dialogs
        self.q2_app = QApplication.activeWindow()
        self.on_init()


class Q2FormWindow(QDialog, q2form.Q2FormWindow, Q2QtWindow, Q2Widget):
    def __init__(self, q2_form: Q2Form, title=""):
        super().__init__(q2_form)
        title = title if title else q2_form.title
        Q2QtWindow.__init__(self, title)
        self._widgets_package = q2gui.pyqt6.widgets

    def restore_geometry(self, settings):
        paw = self.parent()

        if paw is not None:
            # save default == minimal size
            sizeBefore = paw.size()

            if self.q2_form.do_not_save_geometry:
                width, height = 1, 1
            else:
                width = num(settings.get(self.window_title, "width", "-1"))
                height = num(settings.get(self.window_title, "height", "-1"))

            if -1 in [width, height]:  # bad settings or first run
                if self.mode != "grid" and sum(self.q2_form.init_size) > 0:
                    # init size given
                    width, height = self.get_init_size()
                else:
                    width = paw.parent().size().width() * 0.9 if self.mode == "grid" else 0.5
                    height = paw.parent().size().height() * 0.9 if self.mode == "grid" else 0.5

            paw.resize(int(width), int(height))

            sizeAfter = paw.size()
            self.expand_size(paw, sizeBefore, sizeAfter)

            if self.q2_form.do_not_save_geometry:
                left, top = self.center_pos()
            else:
                left = num(settings.get(self.window_title, "left", "-1"))
                top = num(settings.get(self.window_title, "top", "-1"))
                if -1 in [left, top]:  # bad settings or first run
                    left, top = self.center_pos()

            paw.move(int(left), int(top))

            self.fit_size_and_pos(paw)

            if not self.q2_form.do_not_save_geometry:
                if num(settings.get(self.window_title, "is_max", "0")):
                    self.showMaximized()
                    paw.move(0, 0)

    def center_pos(self):
        left = int((self.parent().parent().size().width() - self.parent().size().width()) / 2)
        top = int ((self.parent().parent().size().height() - self.parent().size().height()) / 2)
        return left, top

    def expand_size(self, paw, sizeBefore, sizeAfter):
        wDelta = 0 if sizeBefore.width() < sizeAfter.width() else sizeBefore.width() - sizeAfter.width()
        hDelta = 0 if sizeBefore.height() < sizeAfter.height() else sizeBefore.height() - sizeAfter.height()
        if wDelta or hDelta:
            paw.resize(paw.size().width() + wDelta, paw.size().height() + hDelta)

    def get_init_size(self):
        w, h = self.q2_form.init_size
        parent_size = self.parent().parent().size()
        return [int(parent_size.width() * w / 100), int(parent_size.height() * h / 100)]

    def fit_size_and_pos(self, paw):
        """ensure form fits outside window"""
        parent_size = paw.parent().size()

        size = paw.size()
        original_size = paw.size()

        pos = paw.pos()
        orginal_pos = paw.pos()
        # width
        if parent_size.width() - (size.width()) < 0:
            size.setWidth(parent_size.width())
        if pos.x() + size.width() > parent_size.width():
            pos.setX(parent_size.width() - size.width())
        if pos.x() < 0:
            pos.setX(0)
        # height
        if parent_size.height() - (size.height()) < 0:
            size.setHeight(parent_size.height())

        if pos.y() + size.height() > parent_size.height():
            pos.setY(parent_size.height() - size.height())
        if pos.y() < 0:
            pos.setY(0)
        if orginal_pos != pos:
            paw.move(pos)
        if size != original_size:
            paw.resize(size)

    def set_position(self, left, top):
        left = int(left)
        top = int(top)
        paw = self.parent()
        if paw is not None:
            paw.move(left, top)
        else:
            self.move(left, top)

    def set_size(self, w, h):
        w = int(w)
        h = int(h)
        paw = self.parent()
        if paw is not None:
            paw.resize(w, h)
        else:
            self.resize(w, h)

    def get_position(self):
        parent_mdi_sub_window = self.parent()
        if parent_mdi_sub_window is not None:
            return (parent_mdi_sub_window.pos().x(), parent_mdi_sub_window.pos().y())

    def showEvent(self, event=None):
        if self.shown:
            return
        if self not in self.q2_form.form_stack:
            self.q2_form.form_stack.append(self)

        if not self.q2_form.i_am_child:
            for widget_name in self.widgets:
                widget = self.widgets[widget_name]
                if widget.focusPolicy() == Qt.FocusPolicy.NoFocus:
                    continue
                if hasattr(widget, "isReadOnly") and widget.isReadOnly():
                    continue
                if widget.isEnabled():
                    widget.setFocus()
                    break

        if event:
            event.accept()

        self.q2_form.form_is_active = True
        # if self.mode == "form":
        #     self.q2_form.form_is_active = True
        #     if self.q2_form.before_form_show() is False:
        #         # self.close()
        #         self.q2_form.close()
        #         return

        if not isinstance(self.parent(), QMdiSubWindow):
            self.escapeEnabled = False

        self.shown = True
        self.restore_geometry(q2app.q2_app.settings)

        # if self.mode == "form":
        #     self.parent().setWindowFlag(Qt.WindowMaximizeButtonHint, False)

        if hasattr(self.parent(), "setWindowFlag"):
            self.parent().setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint, False)

            if self.q2_form.hide_title:
                self.parent().setWindowFlags(
                    Qt.WindowType.CustomizeWindowHint
                    | Qt.WindowType.FramelessWindowHint
                    | Qt.WindowType.WindowStaysOnBottomHint
                    | Qt.WindowType.WindowCloseButtonHint
                )
        if self.q2_form.maximized:
            self.showMaximized()
        if self.mode == "form":
            self.q2_form.after_form_show()
        elif self.mode == "grid":
            self.q2_form.after_grid_show()

    def keyPressEvent(self, event: QEvent):
        key = event.key()
        try:
            keyText = QKeySequence(key).toString()
        except Exception:
            keyText = ""
        if key == Qt.Key.Key_Escape and self.escapeEnabled:
            self.close()
        elif key == Qt.Key.Key_Escape and not self.escapeEnabled:
            event.ignore()
            # return
        elif self.mode == "form" and key in (Qt.Key.Key_Up,):
            QApplication.sendEvent(
                self, QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Tab, Qt.KeyboardModifier.ShiftModifier)
            )
        elif self.mode == "form" and key in (Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Down):
            QApplication.sendEvent(self, QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Tab, event.modifiers()))
        elif self.mode == "grid" and key in (Qt.Key.Key_Return,):
            self.q2_form.grid_double_clicked()
        elif keyText in self.hotkey_widgets:  # is it form hotkey
            for widget in self.hotkey_widgets[keyText]:
                if widget.is_enabled() and hasattr(widget, "valid"):
                    widget.valid()
                    return

    def close(self):
        # print("close event", self)
        super().close()
        if self.parent() is not None:
            if isinstance(self.parent(), QMdiSubWindow):
                self.parent().close()
                # QDialog.close(self)
        else:
            QDialog.close(self)

    def closeEvent(self, event=None):
        super().close()
        self.q2_form._close()
        self.q2_form.form_is_active = False
        if event:
            event.accept()

    def set_style_sheet(self, css):
        self.setStyleSheet(css)


# Tells the module which engine to use
q2gui.q2dialogs.Q2Form = Q2Form
# q2Mess
# q2Wait
# q2AskYN
