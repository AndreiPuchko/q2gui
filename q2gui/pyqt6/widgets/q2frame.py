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


from PyQt6.QtWidgets import QGroupBox, QSplitter
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QSize


from q2gui.pyqt6.q2window import Q2Frame, q2_align
from q2gui.pyqt6.q2widget import Q2Widget
from q2gui.q2utils import int_


class q2frame(QGroupBox, Q2Widget, Q2Frame):
    def __init__(self, meta):
        super().__init__(meta)
        Q2Frame.__init__(self, meta.get("column", "/v")[1])
        self.meta = meta
        self.splitter = None
        self.scroller = None
        self.grid_width = None
        self.grid_current_row = 0
        self.grid_current_column = 0
        self.grid_alignment = str(self.meta.get("alignment", "7"))
        column = meta.get("column", "")
        if column[2:3] == "s":  # Splitter!
            self.splitter = q2splitter()
            if column.startswith("/v"):
                self.splitter.setOrientation(Qt.Orientation.Vertical)
            self.layout().addWidget(self.splitter)

        if column.startswith("/g"):
            if cw:=int_(meta.get("pic", 0)):
                self.grid_width = cw
            elif (cw := int_(column[2:])):
                self.grid_width = cw

        if meta.get("label") not in ("", "-") and not meta.get("check"):
            self.set_title(meta.get("label"))
            self.setObjectName("title")
        if meta.get("label", "") == "":
            self.hide_border()
        elif meta.get("label", "") == "-":
            self.setObjectName("title")

    def hide_border(self):
        self.setObjectName("grb")
        self.set_title("")
        self.add_style_sheet(" QGroupBox#grb {border:0} ")

    def set_title(self, title):
        self.setTitle(title)

    def can_get_focus(self):
        return False

    def get_widget_count(self):
        return self.layout().count()

    def add_widget(self, widget=None, label=None):
        if self.splitter is not None:
            self.splitter.addWidget(widget)
            if hasattr(widget, "meta"):
                self.splitter.setStretchFactor(self.splitter.count() - 1, int_(widget.meta.get("stretch", 0)))
        else:
            if self.frame_mode == "g":
                if grow := int_(widget.meta.get("grid_row", 0)):
                    if grow > 0:
                        self.grid_current_row = grow
                    else:
                        self.grid_current_row += 1
                        self.grid_current_column = 0
                if gcol := int_(widget.meta.get("grid_column", 0)):
                    self.grid_current_column = gcol
                grow_span = max(int_(widget.meta.get("grid_row_span", 1)), 1)
                gcol_span = max(int_(widget.meta.get("grid_column_span", 1)), 1)
                self.layout().addWidget(
                    widget,
                    self.grid_current_row,
                    self.grid_current_column,
                    grow_span,
                    gcol_span,
                    q2_align[self.grid_alignment]
                )
                self.grid_current_column += 1
                if self.grid_width and self.grid_current_column >= self.grid_width:
                    self.grid_current_row += 1
                    self.grid_current_column = 0
            else:
                return super().add_widget(widget=widget, label=label)


class q2splitter(QSplitter):
    def __init__(self):
        super().__init__()
        # self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))

    def get_sizes(self):
        return ",".join([f"{x}" for x in self.sizes()])

    def set_sizes(self, sizes):
        if sizes == "":
            init_sizes = [int_(self.widget(x).meta.get("stretch", 1)) for x in range(self.count())]
            init_sizes = [x if x > 0 else 1 for x in init_sizes]
            if sum(init_sizes):
                widget_size = (
                    self.width() if self.orientation() is Qt.Orientation.Horizontal else self.height()
                )
                init_sizes = [str(int(x * widget_size / sum(init_sizes))) for x in init_sizes]
                for x in range(self.count()):
                    widgget = self.widget(x)
                    if widgget.meta.get("control") == "toolbar":
                        init_sizes[x] = str(widgget.sizeHint().height())
                sizes = ",".join(init_sizes)
        else:
            if (delta := self.count() - len(sizes.split(","))) > 0:
                nsizes = [int_(x) for x in sizes.split(",")]
                oldsize = sum(nsizes)
                nsizes = [int_(x / 2) for x in nsizes]
                deltasize = oldsize - sum(nsizes)
                sizes = ",".join([f"{x}" for x in nsizes])
                for x in range(delta):
                    sizes += f",{int_(deltasize/delta)}"
        if sizes:
            sizes = [int(x) for x in sizes.split(",")]
            self.setSizes(sizes)

    def showEvent(self, ev):
        self.updateGeometry()
        return super().showEvent(ev)

    def sizeHint(self):
        if self.isVisible():
            return QSize(99999, 99999)
        else:
            return super().sizeHint()
