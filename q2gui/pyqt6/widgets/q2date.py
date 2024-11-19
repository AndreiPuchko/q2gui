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


from PyQt6.QtWidgets import (
    QComboBox,
    QWidget,
    QVBoxLayout,
    QCalendarWidget,
    QHBoxLayout,
    QPushButton,
)

from PyQt6.QtGui import QValidator, QFontMetrics
from PyQt6.QtCore import QEvent, pyqtSignal, QDate, Qt

from q2gui.pyqt6.q2widget import Q2Widget
import re
import datetime


class q2date(QComboBox, Q2Widget):
    editingFinished = pyqtSignal()

    def __init__(self, meta):
        super().__init__(meta)
        self.setEditable(True)
        self.lineedit = self.lineEdit()
        if self.meta.get("readonly"):
            self.lineedit.setReadOnly(True)
        self.lineedit.setInputMask("99.99.9999")
        self.set_text(self.meta.get("data"))

        class q2DateValidator(QValidator):
            def validate(self, text, pos):
                if text == "  .  .    ":
                    return (QValidator.State.Acceptable, text, 0)
                else:
                    lt = [x for x in text.replace(" ", "0").split(".")]
                    if int(lt[2]) == 0:  # year
                        lt[2] = QDate.currentDate().toString("yyyy")

                    if int(lt[1]) == 0 and pos != 4:  # month
                        lt[1] = QDate.currentDate().toString("MM")
                    elif int(lt[1]) > 12:
                        lt[1] = "12"

                    if int(lt[0]) > 31:  # day
                        lt[0] = "31"
                    elif int(lt[0]) == 0:
                        lt[0] = "01"
                    elif int(lt[0]) < 4 and len(lt[0]) > 2:
                        lt[0] = f"{int(lt[0])}0"
                    
                    if pos > 9:
                        mdm = QDate(int(lt[2]), int(lt[1]), 1).daysInMonth()
                        if mdm < int(lt[0]):
                            lt[0] = str(mdm)
                    text = ".".join(lt)
                    return (QValidator.State.Acceptable, text, pos)

        self.lineedit.setValidator(q2DateValidator())
        self.lineedit.editingFinished.connect(self.lineeditEditingFinished)
        self.lineedit.cursorPositionChanged.connect(self.lineeditCursorPositionChanged)

    def changeEvent(self, e):
        if e.type() == QEvent.Type.StyleChange:
            self.setMinimumWidth(int(QFontMetrics(self.font()).horizontalAdvance("0") * 16))
        return super().changeEvent(e)

    def lineeditCursorPositionChanged(self, old, new):
        if old in [3, 4] and (new < 3 or new > 4):
            # self.lineedit.setText(self.fixupDay(self.lineedit.text()))
            self.lineedit.setCursorPosition(new)
        elif new == 10:
            self.lineedit.setCursorPosition(9)

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
        elif event.key() == Qt.Key.Key_End:
            self.lineedit.setCursorPosition(9)
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
        if self.meta.get("readonly"):
            return

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
            self.lineedit.setText(extract_date(text))
            # self.lineedit.setText(QDate.fromString(f"{text}", "yyyy-MM-dd").toString("dd.MM.yyyy"))
            self.lineedit.setCursorPosition(0)

    def get_text(self):
        if self.lineedit.text() == "..":
            return "0000-00-00"
        else:
            return QDate.fromString(self.lineedit.text(), "dd.MM.yyyy").toString("yyyy-MM-dd")


def extract_date(text):
    if text == "":
        return ""
    elif text == "0000-00-00":
        return "  .  .    "
    splited_text = re.split(r"[/,/.\s/-]+", text.strip())

    today = datetime.date.today()
    month = None
    year = None
    day = 1
    if len(splited_text) >= 1:  # day
        if len(splited_text[0]) == 4:
            year = splited_text[0]
        elif len(splited_text[0]) < 3:
            day = splited_text[0]

    if len(splited_text) > 1:
        # if month > int(spl[1]):
        #     year = year - 1
        month = int(splited_text[1])
        if month > today.month and len(splited_text) < 3 and year is None:
            year = today.year - 1

    if len(splited_text) > 2:
        if len(splited_text[2]) == 4:
            year = splited_text[2]
        elif len(splited_text[2]) < 3 and len(splited_text[0]) == 4:
            day = splited_text[2]
        else:
            day = splited_text[0]
    if year is None and len(splited_text) == 3:
        if len(splited_text[2]) == 1:
            year = int(splited_text[2]) + today.year // 10 * 10
        else:
            year = int(splited_text[2]) + 2000

    if year is None:
        year = today.year if month != 12 else (today.year - 1)
    if month is None:
        month = (today.month - 1) if today.month > 1 else 12
    date = datetime.date(day=int(day), month=int(month), year=int(year))
    return date.strftime("%d-%m-%Y")
