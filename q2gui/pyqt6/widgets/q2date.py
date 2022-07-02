import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()

from PyQt6.QtWidgets import (
    QComboBox,
    QWidget,
    QVBoxLayout,
    QCalendarWidget,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
)

from PyQt6.QtGui import QValidator, QFontMetrics
from PyQt6.QtCore import pyqtSignal, QDate, Qt

from q2gui.pyqt6.q2widget import Q2Widget


class q2date(QComboBox, Q2Widget):
    editingFinished = pyqtSignal()

    def __init__(self, meta):
        super().__init__(meta)
        self.setEditable(True)
        self.lineedit = self.lineEdit()
        self.lineedit.setInputMask("99.99.9999")
        self.lineedit.setStyleSheet("QLineEdit")
        self.set_text(self.meta.get("data"))
        # self.setMinimumWidth(QFontMetrics(self.font()).width("0") * 14)
        self.setMinimumWidth(int(QFontMetrics(self.font()).horizontalAdvance("0") * 14))
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)

        class q2DateValidator(QValidator):
            def validate(self, text, pos):
                if text == "  .  .    ":
                    return (QValidator.State.Acceptable, text, 0)
                else:
                    lt = [x for x in text.replace(" ", "0").split(".")]
                    if int(lt[2]) == 0:  # year
                        lt[2] = QDate.currentDate().toString("yyyy")
                    if int(lt[1]) == 0:  # month
                        lt[1] = QDate.currentDate().toString("MM")
                    elif int(lt[1]) > 12:
                        lt[1] = "12"
                    if int(lt[0]) > 31:  # day
                        lt[0] = "31"
                    elif int(lt[0]) == 0:
                        lt[0] = QDate.currentDate().toString("dd")
                    if pos > 4:
                        mdm = QDate(int(lt[2]), int(lt[1]), 1).daysInMonth()
                        if mdm < int(lt[0]):
                            lt[0] = str(mdm)
                    text = ".".join(lt)
                    return (QValidator.State.Acceptable, text, pos)

        self.lineedit.setValidator(q2DateValidator())
        self.lineedit.editingFinished.connect(self.lineeditEditingFinished)
        self.lineedit.cursorPositionChanged.connect(self.lineeditCursorPositionChanged)
        # q2Widget.__init__(self, meta)

    # def sizeHint(self):
    #     return super().sizeHint()

    def lineeditCursorPositionChanged(self, old, new):
        if old in [3, 4] and (new < 3 or new > 4):
            self.lineedit.setText(self.fixupDay(self.lineedit.text()))
            self.lineedit.setCursorPosition(new)

    def fixupDay(self, text):
        if text != "..":
            lt = text.split(".")
            mdm = QDate(int(lt[2]), int(lt[1]), 1).daysInMonth()
            if mdm < int(lt[0]):
                lt[0] = str(mdm)
            return ".".join(lt)
        else:
            return text

    def lineeditEditingFinished(self):
        if self.lineedit.text() != "..":
            self.lineedit.setText(self.fixupDay(self.lineedit.text()))
        self.editingFinished.emit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.lineedit.setText("  .  .    ")
        elif event.key() == Qt.Key.Key_Insert:
            self.showPopup()
            self.lineedit.setCursorPosition(0)
        elif event.key() in [
            Qt.Key.Key_Enter,
            Qt.Key.Key_Return,
            Qt.Key.Key_Down,
            Qt.Key.Key_PageDown,
            Qt.Key.Key_PageUp,
        ]:
            event.ignore()
            # QApplication.sendEvent(self, QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Tab, Qt.NoModifier))
        elif event.key() in [Qt.Key.Key_Up]:
            event.accept()
            self.focusPreviousChild()
        else:
            return super().keyPressEvent(event)

    def showPopup(self):
        class q2CalendarWidget(QWidget):
            def __init__(self, parent=self):
                super().__init__(parent=parent, flags=Qt.WindowType.Popup)
                self.setLayout(QVBoxLayout())
                self.clndr = QCalendarWidget(self)
                self.clndr.setSelectedDate(QDate.fromString(self.parent().lineedit.text(), "dd.MM.yyyy"))
                self.clndr.activated.connect(self.clndrActivated)
                buttonLayout = QHBoxLayout()

                todayButton = QPushButton("Today")
                todayButton.clicked.connect(self.today)
                buttonLayout.addWidget(todayButton)

                clearButton = QPushButton("Clear")
                clearButton.clicked.connect(self.clear)
                buttonLayout.addWidget(clearButton)

                self.layout().addLayout(buttonLayout)
                self.layout().addWidget(self.clndr)

            def show(self):
                super().show()
                self.clndr.setFocus()

            def clear(self):
                self.parent().lineedit.setText("  .  .    ")
                self.close()

            def today(self):
                self.parent().lineedit.setText(QDate.currentDate().toString("dd.MM.yyyy"))
                self.close()

            def clndrActivated(self, date):
                self.parent().set_text(date.toString("yyyy-MM-dd"))
                clndr.close()

        clndr = q2CalendarWidget()
        clndr.setFont(self.font())
        clndr.move(self.mapToGlobal(self.rect().bottomLeft()))
        clndr.show()

    def set_text(self, text):
        if hasattr(self, "lineedit"):
            self.lineedit.setText(QDate.fromString(f"{text}", "yyyy-MM-dd").toString("dd.MM.yyyy"))
            self.lineedit.setCursorPosition(0)

    def get_text(self):
        if self.lineedit.text() == "..":
            return "0000-00-00"
        else:
            return QDate.fromString(self.lineedit.text(), "dd.MM.yyyy").toString("yyyy-MM-dd")
