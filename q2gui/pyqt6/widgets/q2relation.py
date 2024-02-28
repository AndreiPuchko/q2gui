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

import sys



from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt

import q2gui.q2app as q2app
from q2gui.q2form import Q2Form
from q2gui.q2utils import num
from q2gui.pyqt6.q2widget import Q2Widget
from q2gui.pyqt6.q2window import Q2Frame
from q2gui.pyqt6.widgets.q2line import q2line
from q2gui.pyqt6.widgets.q2button import q2button
from q2gui.pyqt6.widgets.q2lookup import q2lookup
from q2gui.q2model import Q2Model
from q2db.db import Q2Db


class q2relation(QFrame, Q2Widget, Q2Frame):
    def __init__(self, meta):
        super().__init__(meta)
        Q2Frame.__init__(self, "h")
        self.meta = meta

        self.get = q2line(meta)
        self.filter_string = ""

        self.get.textChanged.connect(self.get_text_changed)
        self.get.editingFinished.connect(self.edit_done)
        self.button = q2button(
            {
                "label": "?",
                "datalen": 3,
                "valid": self.show_related_form,
                # "when": self.when,
                "form": self.meta["form"],
            }
        )
        self.say = q2line({"disabled": "*"})
        self.to_form = None
        if self.meta.get("to_form"):
            if isinstance(self.meta.get("to_form"), Q2Form):
                self.to_form: Q2Form = self.meta.get("to_form")
            else:
                self.to_form: Q2Form = self.meta.get("to_form")()
            # self.to_form.max_child_level = 0
            self.to_form.title += " ."

        self.add_widget(self.get)
        self.add_widget(self.button)
        self.add_widget(self.say)
        self.set_text(self.meta.get("data", ""))
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocusProxy(self.get)
        # self.get_valid()

    def show_related_form(self):
        if isinstance(self.to_form, Q2Form):
            self.to_form.add_action(
                q2app.ACTION_SELECT_TEXT,
                self.show_related_form_result,
                hotkey="Enter",
                tag="select",
                icon=q2app.ACTION_SELECT_ICON,
            )

            def seek():
                if self.filter_string:
                    self.to_form.model.cursor.set_where(self.filter_string)
                    self.to_form.model.cursor.refresh()

                row = self.to_form.model.cursor.seek_row({self.meta["to_column"]: self.get_text()})
                self.to_form.set_grid_index(row)

            self.to_form.before_grid_show = seek
            self.get.when()
            self.to_form.show_mdi_modal_grid()
            # self.set_related()

    def show_related_form_result(self):
        if self.to_form:
            self.get.set_focus()
            self.get.set_text(self.to_form.r.__getattr__(self.meta["to_column"]))
            self.to_form.close()
            self.get_valid()
            self.get.valid()

    def edit_done(self):
        self.get_valid()

    def get_valid(self):
        value = self.get.get_text()
        if self.meta.get("num") and num(value) == 0:
            return True
        elif value == "":
            return True
        return self.set_related()

    def get_related(self):
        rel = None
        if self.meta["form"].model:
            rel = self.meta["form"].model._get_related(
                self.get.text(), self.meta, do_not_show_value=1, reset_cache=1
            )
        elif self.meta["form"].db:  # datasource provided
            rel = self.meta["form"].db.get(
                self.meta["to_table"],
                f"{self.meta['to_column']}='{self.get.text()}'",
                self.meta["related"],
            )
        return rel

    def set_related(self):
        rel = self.get_related()
        if rel == "":
            rel = None
            self.say.set_text("")
            self.show_related_form()
            return True

        if rel is None:
            self.say.set_text("")
            return False
        else:
            self.say.set_text(rel)
            return True

    def set_text(self, text):
        if hasattr(self, "get"):
            self.get.set_text(text)
            self.get_valid()

    def get_text(self):
        return self.get.get_text()

    def get_text_changed(self, text):
        if "*" in text and self.meta.get("num") or text.startswith("*"):
            lookup_widget = q2_realtion_lookup(self, "")
            lookup_widget.show(self.meta)

    def set_focus(self):
        self.get.setFocus()

    def set_disabled(self, arg=True):
        if hasattr(self, "get"):
            self.get.set_disabled(arg)
            self.button.set_disabled(arg)
            # self.set_disabled(arg)

    def set_enabled(self, arg=True):
        if hasattr(self, "get"):
            self.get.set_enabled(arg)
            self.button.set_enabled(arg)
            # self.set_enabled(arg)

    def is_enabled(self):
        return self.get.is_enabled()


class q2_realtion_lookup(q2lookup):
    def __init__(self, parent, text):
        super().__init__(parent, text)

    def lookup_search(self):
        self.lookup_list.clear()
        if self.parent().to_form:
            q2_db: Q2Db = self.parent().to_form.model.cursor.q2_db
        else:
            q2_db: Q2Db = self.parent().meta["form"].db

        sql = "select {to_column} as tocol, {related} as recol from {to_table}".format(**self.meta)

        related = self.meta.get("related")

        # cond_list = self.parent().to_form.model.parse_lookup_text(self.lookup_edit.get_text())
        cond_list = Q2Model().parse_lookup_text(self.lookup_edit.get_text())
        where = " and ".join(
            [f"{related} {'' if x[0] == '+' else 'not'} like '%{x[1]}%' " for x in cond_list]
        )
        if where:
            sql += f" where {where}"
        cursor = q2_db.cursor(sql)
        self.found_rows = [x for x in cursor.records()]
        for x in self.found_rows:
            self.lookup_list.addItem(f"""{x["recol"]} ({x["tocol"]})""")

    def lookup_list_selected(self):
        self.parent().set_text(self.found_rows[self.lookup_list.currentRow()]["tocol"])
        self.close()

    def set_geometry(self):
        parent = self.parent()
        self.setFixedWidth(parent.width())
        self.move(parent.mapToGlobal(parent.rect().topLeft()))

    def show(self, meta):
        self.meta = meta
        return super().show()
