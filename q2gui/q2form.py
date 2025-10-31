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


import q2gui.q2app as q2app
from q2gui.q2model import Q2Model, Q2CursorModel
from q2gui.q2utils import int_, num, nums
import re
import html
import json
import gettext

_ = gettext.gettext


VIEW = "VIEW"
NEW = "NEW"
COPY = "COPY"
EDIT = "EDIT"
NO_DATA_WIDGETS = ("button", "toolbutton", "frame", "label")
NO_LABEL_WIDGETS = ("button", "toolbutton", "frame", "label", "check")


class Q2Form:
    def __init__(self, title=""):
        super().__init__()
        self.title = title.strip().split("\n")[0][:50]
        self.name = title
        self.form_stack = []
        self.style_sheet = ""

        self.hide_title = False
        self.maximized = False
        self.init_size = [0, 0]

        self.heap = q2app.Q2Heap()
        self.actions = q2app.Q2Actions()
        self.grid_navi_actions = []
        self.controls = q2app.Q2Controls()
        self.system_controls = q2app.Q2Controls()
        self.model = None
        self.db = None
        self.q2_app = q2app.q2_app
        if hasattr(self.q2_app, "db"):
            self.db = q2app.q2_app.db
        self._model_record = {}  # contains the data of the currently edited record

        # Shortcuts to elements
        self.s = Q2FormData(self)  # widgets data by name
        self.w = Q2FormWidget(self)  # widgets by name
        self.a = Q2FormAction(self)  # Actions by text
        self.r = Q2ModelData(self)  # Grid data by name
        self.c = self.controls.c  # control dict

        self.prev_form = None
        self.children_forms = []  # forms inside this form
        self.i_am_child = None
        self.max_child_level = 1  # max depth for child forms

        self.ok_button = False
        self.cancel_button = False
        self.ok_pressed = None

        self.show_grid_action_top = True
        self.do_not_save_geometry = False

        # Must be redefined in any subclass
        self._Q2FormWindow_class = Q2FormWindow
        self._q2dialogs = None

        self._in_close_flag = False
        self.last_closed_form = None
        self.last_closed_form_widgets_text = {}

        self.grid_form = None
        self.crud_form = None
        self.crud_mode = ""

        self.no_view_action = False

        self.current_row = -1
        self.current_column = -1
        self.last_current_row = -1
        self.last_current_column = -1

        # Must be called in subclass
        # self.on_init()
        pass

    def on_init(self):
        pass

    def run_action(self, text=""):
        for x in self.actions:
            if text == x["text"]:
                x["_worker"]()

    def disable_action(self, text="", mode=True):
        self.actions.set_disabled(text, mode)

    def enable_action(self, text="", mode=True):
        self.actions.set_enabled(text, mode)

    def run(self, order="", where=""):
        if self.model:
            need_refresh = False
            if order:
                need_refresh = True
                self.model.set_order(order)
            if where:
                need_refresh = True
                self.model.set_where(where)
            if need_refresh:
                self.model.refresh()
            self.show_mdi_modal_grid()
        else:
            self.show_mdi_modal_form()
        return self

    def show_progressbar(self, title="", count=""):
        return self._q2dialogs.Q2WaitShow(title, count)

    def show_(self):
        for x in self.widgets():
            if hasattr(self.widgets()[x], "show_"):
                self.widgets()[x].show_()
        self.form_refresh()
        # for x in self.controls:
        #     if x.get("show") and x.get("column") in self.widgets():
        #         self.widgets()[x.get("column")].set_text(x["show"](mode="form"))

    def set_model(self, model):
        self.model: Q2Model = model
        self.model.q2_form = self
        self.model.build()
        return self.model

    def set_cursor(self, cursor):
        self.set_model(Q2CursorModel(cursor))

    def refresh(self, soft=None):
        row = self.current_row
        col = self.current_column
        if soft:
            self.model.refresh()
            self.refresh_children()
        else:
            self._q2dialogs.q2working(
                # lambda: (self.model.refresh(), self.refresh_children()), _("Refreshing...")
                lambda: (self.model.refresh(),), _("Refreshing...")
            )
        self.q2_app.show_statusbar_mess(self.model.row_count())
        self.set_grid_index(row, col)
        if self.model.refreshed:
            #     self.form_refresh()
            self.model.refreshed = False

    def form_refresh(self):
        pass

    def widget(self):
        if self.form_stack:
            return self.form_stack[-1]

    def widgets(self):
        if self.form_stack:
            return self.form_stack[-1].widgets
        else:
            return {}

    def widgets_list(self):
        return [self.form_stack[-1].widgets[x] for x in self.form_stack[-1].widgets]

    def focus_widget(self):
        return q2app.q2_app.focus_widget()

    def close(self):
        if self.form_stack:
            self.last_closed_form = self.form_stack[-1]
            self.save_closed_form_text()
            self.form_stack[-1].close()
            # self.q2_app.process_events()

    def save_closed_form_text(self):
        self.last_closed_form_widgets_text = {
            x: self.last_closed_form.widgets[x].get_text()
            for x in self.last_closed_form.widgets
            if hasattr(self.last_closed_form.widgets[x], "get_text")
        }

    def _close(self, q2form_window=None):
        if self._in_close_flag:
            return
        self._in_close_flag = True
        if self.form_stack:
            self.last_closed_form = self.form_stack[-1]
            self.form_stack[-1].save_splitters()
            self.save_closed_form_text()
        if q2form_window is not None and q2form_window.is_crud is None:
            self.after_form_closed()
        self._in_close_flag = False

    def show_form(self, title="", modal="modal"):
        self.get_form_widget(title).show_form(modal)

    def show_mdi_form(self, title=""):
        form_widget = self.get_form_widget(title)
        form_widget.show_form(modal="")

    def show_mdi_modal_form(self, title=""):
        form_widget = self.get_form_widget(title)
        form_widget.show_form("modal")

    def show_app_modal_form(self, title=""):
        self.get_form_widget(title).show_form(modal="super")

    def show_grid(self, title="", modal=""):
        self.get_grid_widget(title).show_form(modal)

    def show_mdi_grid(self, title=""):
        self.get_grid_widget(title).show_form(modal="")

    def show_mdi_modal_grid(self, title=""):
        self.get_grid_widget(title).show_form(modal="modal")

    def show_app_modal_grid(self, title=""):
        self.get_grid_widget(title).show_form(modal="super")

    def get_form_widget(self, title=""):
        form_widget = self._Q2FormWindow_class(self, title)
        form_widget.build_form()
        return form_widget

    def get_grid_widget(self, title=""):
        self.grid_form = self._Q2FormWindow_class(self, title)
        self.model.build()
        self.get_grid_crud_actions()
        self.before_grid_build()
        self.grid_form.build_grid()
        return self.grid_form

    def get_widget(self):
        if self.model is not None:
            return self.get_grid_widget()
        else:
            return self.get_form_widget()

    def get_grid_crud_actions(self):
        is_crud = self.a.__getattr__("/crud")

        tmp_actions = q2app.Q2Actions()
        if not self.no_view_action:
            self.add_action_view(tmp_actions)
        if is_crud and not self.model.readonly:
            self.add_action_new(tmp_actions)
            self.add_action_copy(tmp_actions)
            self.add_action_edit(tmp_actions)
            tmp_actions.add_action(text="-")
            self.add_action_delete(tmp_actions)
            tmp_actions.add_action(text="-")

        if "seq" in self.model.columns:
            self.add_action_seq()

        for x in self.actions:
            if x.get("text").startswith("/"):
                continue
            tmp_actions.append(x)
        self.actions = tmp_actions

    def before_form_build(self):
        pass

    def before_grid_build(self):
        pass

    def add_action_view(self, actions=None):
        if actions is None:
            actions = self.actions
        actions.add_action(
            text=q2app.ACTION_VIEW_TEXT,
            worker=lambda: self.show_crud_form(VIEW),
            icon=q2app.ACTION_VIEW_ICON,
            hotkey=q2app.ACTION_VIEW_HOTKEY,
            eof_disabled=1,
            tag="view",
        )

    def add_action_delete(self, actions=None):
        if actions is None:
            actions = self.actions
        actions.add_action(
            text=q2app.ACTION_REMOVE_TEXT,
            worker=self.crud_delete,
            icon=q2app.ACTION_REMOVE_ICON,
            hotkey=q2app.ACTION_REMOVE_HOTKEY,
            eof_disabled=1,
            tag="red",
        )

    def add_action_copy(self, actions=None):
        if actions is None:
            actions = self.actions
        actions.add_action(
            text=q2app.ACTION_COPY_TEXT,
            worker=lambda: self.show_crud_form(COPY),
            icon=q2app.ACTION_COPY_ICON,
            hotkey=q2app.ACTION_COPY_HOTKEY,
            eof_disabled=1,
        )

    def add_action_edit(self, actions=None):
        if actions is None:
            actions = self.actions
        actions.add_action(
            text=q2app.ACTION_EDIT_TEXT,
            worker=lambda: self.show_crud_form(EDIT),
            icon=q2app.ACTION_EDIT_ICON,
            hotkey=q2app.ACTION_EDIT_HOTKEY,
            eof_disabled=1,
            tag="edit",
        )

    def add_action_new(self, actions=None):
        if actions is None:
            actions = self.actions
        actions.add_action(
            text=q2app.ACTION_NEW_TEXT,
            worker=lambda: self.show_crud_form(NEW),
            icon=q2app.ACTION_NEW_ICON,
            hotkey=q2app.ACTION_NEW_HOTKEY,
        )

    def add_action_seq(self, actions=None):
        if actions is None:
            actions = self.actions
        actions.add_action(
            "Move up", self.move_seq_up, icon="arrow-up.png", eof_disabled=1, hotkey="Ctrl+Alt+Up"
        )
        actions.add_action(
            "Move down", self.move_seq_down, icon="arrow-down.png", eof_disabled=1, hotkey="Ctrl+Alt+Down"
        )
        actions.add_action(
            q2app.ACTION_RENUMBER_TEXT,
            self.seq_renumber,
            icon=q2app.ACTION_RENUMBER_ICON,
            hotkey=q2app.ACTION_RENUMBER_HOTKEY,
            eof_disabled=1,
        )
        actions.add_action("-")

    def move_seq_up(self):
        selected_row = sorted(self.get_grid_selected_rows())
        if selected_row[0] == 0:
            return

        for row in selected_row:
            self.set_grid_index(row)
            nr = self.model.get_record(self.current_row - 1)
            cr = self.model.get_record(self.current_row)
            if nr["seq"] == cr["seq"]:
                nr["seq"] = "%s" % (int_(nr["seq"]) - 1)
            else:
                nr["seq"], cr["seq"] = cr["seq"], nr["seq"]
            self.model.update(nr)
            self.model.update(cr)
        self.refresh(True)
        self.set_grid_index(selected_row[0])
        self.set_grid_selected_rows([x - 1 for x in selected_row])

    def move_seq_down(self):
        selected_row = sorted(self.get_grid_selected_rows())
        selected_row.reverse()
        if selected_row[0] == self.model.row_count() - 1:
            return

        for row in selected_row:
            self.set_grid_index(row)
            nr = self.model.get_record(self.current_row + 1)
            cr = self.model.get_record(self.current_row)
            if nr["seq"] == cr["seq"]:
                nr["seq"] = "%s" % (int_(nr["seq"]) + 1)
            else:
                nr["seq"], cr["seq"] = cr["seq"], nr["seq"]
            self.model.update(nr)
            self.model.update(cr)
        self.refresh(True)
        self.set_grid_index(selected_row[0])
        self.set_grid_selected_rows([x + 1 for x in selected_row])

    def seq_renumber(self):
        curr_row = self.current_row
        pk = self.model.get_meta_primary_key()
        wait = self._q2dialogs.Q2WaitShow(self.model.row_count(), _("Renumber sequence"))
        for x in range(self.model.row_count()):
            wait.step(1000)
            self.set_grid_index(x)
            # dic = {pk: self.model.get_record(x)[pk]}
            dic = {pk: self.r.__getattr__(pk)}
            dic["seq"] = x + 1
            self.model.update(dic, refresh=False)
        wait.close()
        self.refresh(True)
        self.set_grid_index(curr_row)

    def is_grid_updateable(self):
        table_name = self.model.get_table_name()
        return table_name != "" and " " not in table_name

    def build_grid_view_auto_form(self):
        # Define layout
        if self.model.records:
            self.add_control("/f", "Frame with form layout")
            # Populate it with the columns from csv
            for x in self.model.records[0]:
                self.add_control(x, x, control="line", datalen=100)
            # Assign data source
            self.model.readonly = True
            self.actions.add_action(text="/view", eof_disabled=1)

            if self.model.filterable:

                def run_filter_data_form():
                    filter_form = self.__class__("Filter Conditions")
                    # Populate form with columns
                    for x in self.controls:
                        filter_form.controls.add_control(
                            column=x["column"],
                            label=x["label"],
                            control=x["control"],
                            check=False if x["column"].startswith("/") else True,
                            datalen=x["datalen"],
                        )

                    def before_form_show():
                        # put previous filter conditions to form
                        for x in self.model.get_where().split(" and "):
                            if "' in " not in x:
                                continue
                            column_name = x.split(" in ")[1].strip()
                            column_value = x.split(" in ")[0].strip()[1:-1]
                            filter_form.w.__getattr__(column_name).set_text(column_value)
                            filter_form.w.__getattr__(column_name).check.set_checked()

                    def valid():
                        # apply new filter to grid
                        filter_list = []
                        for x in filter_form.widgets_list():
                            if x.check and x.check.is_checked():
                                filter_list.append(f"'{x.get_text()}' in {x.meta['column']}")
                        filter_string = " and ".join(filter_list)
                        self.model.set_where(filter_string)

                    filter_form.before_form_show = before_form_show
                    filter_form.valid = lambda: self._q2dialogs.q2working(valid, q2app.MESSAGE_SORTING)
                    filter_form.ok_button = 1
                    filter_form.cancel_button = 1
                    filter_form.add_ok_cancel_buttons()
                    filter_form.show_mdi_modal_form()

                self.actions.add_action("Filter", worker=run_filter_data_form, hotkey="F9", eof_disabled=1)

    def get_table_schema(self):
        rez = []
        if self.model is not None:
            table_name = ""
            table_name = self.model.get_table_name()
            for meta in self.controls:
                meta = q2app.Q2Controls.validate(meta)
                if meta["column"].startswith("/"):
                    continue
                if not meta.get("migrate"):
                    continue
                if meta.get("control") in NO_DATA_WIDGETS:
                    continue
                column = {
                    "table": table_name,
                    "column": meta["column"],
                    "datatype": meta["datatype"],
                    "datalen": meta["datalen"],
                    "datadec": meta["datadec"],
                    "to_table": meta["to_table"],
                    "to_column": meta["to_column"],
                    "related": meta["related"],
                    "pk": meta["pk"],
                    "ai": meta["ai"],
                }
                rez.append(column)
        return rez

    def get_current_record(self):
        if self.model:
            return self.model.get_record(self.current_row)

    def _valid(self):
        if self.valid() is False:
            return
        self.ok_pressed = True
        self.close()

    def add_ok_cancel_buttons(self):
        if not self.ok_button and not self.cancel_button:
            return
        buttons = q2app.Q2Controls()
        buttons.add_control("/")
        buttons.add_control("/h", "-")
        buttons.add_control("/s")
        if self.ok_button:
            buttons.add_control(
                column="_ok_button",
                label=q2app.CRUD_BUTTON_OK_TEXT,
                control="button",
                hotkey="PgDown",
                valid=self._valid,
                tag="_ok_button",
            )
        if self.cancel_button:
            buttons.add_control(
                column="_cancel_button",
                label=q2app.CRUD_BUTTON_CANCEL_TEXT,
                control="button",
                mess=q2app.CRUD_BUTTON_CANCEL_MESSAGE,
                valid=self.close,
                tag="_cancel_button",
            )
        buttons.add_control("/")

        self.system_controls = buttons

    def add_crud_buttons(self, mode):
        buttons = q2app.Q2Controls()
        buttons.add_control("/")
        buttons.add_control("/h", "-", tag="crud_buttons")
        if not self.no_view_action:
            buttons.add_control(
                column="_prev_button",
                label="▲",
                control="button",
                mess="Previous row",
                valid=lambda: self.move_crud_view(8),
                disabled=True if mode is not VIEW else False,
                hotkey="PgUp",
            )
            buttons.add_control(
                column="_next_button",
                label="▼",
                control="button",
                mess="Next row",
                valid=lambda: self.move_crud_view(2),
                disabled=True if mode is not VIEW else False,
                hotkey="PgDown",
            )
            buttons.add_control("/s")

            if self.a.tag("edit"):
                buttons.add_control(
                    column="_edit_button",
                    label=q2app.CRUD_BUTTON_EDIT_TEXT,
                    control="button",
                    mess=q2app.CRUD_BUTTON_EDIT_MESSAGE,
                    valid=self.crud_view_to_edit,
                    disabled=True if mode is not VIEW else False,
                )
                buttons.add_control("/s")
        else:
            buttons.add_control("/s")

        buttons.add_control(
            column="_ok_button",
            label=q2app.CRUD_BUTTON_OK_TEXT,
            control="button",
            mess=q2app.CRUD_BUTTON_OK_MESSAGE,
            disabled=True if mode is VIEW else False,
            hotkey="PgDown",
            valid=self.crud_save,
            tag="_ok_button",
        )

        buttons.add_control(
            column="_cancel_button",
            label=q2app.CRUD_BUTTON_CANCEL_TEXT,
            control="button",
            mess=q2app.CRUD_BUTTON_CANCEL_MESSAGE,
            # valid=self.crud_close,
            valid=self.close,
            tag="_cancel_button",
        )
        buttons.add_control("/")
        self.system_controls = buttons

    def crud_view_to_edit(self):
        self.crud_form.set_title(f"{self.title}.[EDIT]")
        self.w._ok_button.set_enabled(True)
        self.w._prev_button.set_enabled(False)
        self.w._next_button.set_enabled(False)
        self.w._edit_button.set_enabled(False)

    def move_crud_view(self, mode):
        """move current grid record
        up (mode=8) or down (mode=2) - look at numpad to understand why
        and update values in crud_form
        """
        self.move_grid_index(mode)
        self.set_crud_form_data()
        self.before_form_show()

    def crud_delete(self):
        selected_rows = self.get_grid_selected_rows()
        if len(selected_rows) == 1:
            ask_text = q2app.ASK_REMOVE_RECORD_TEXT
        else:
            ask_text = q2app.ASK_REMOVE_RECORDS_TEXT % len(selected_rows)
        waitbar = None
        if selected_rows and self._q2dialogs.q2AskYN(ask_text) == 2:
            show_error_messages = True
            if len(selected_rows) > 10:
                waitbar = self.show_progressbar(q2app.MESSAGE_ROWS_REMOVING, len(selected_rows))
            for row in selected_rows:
                if waitbar:
                    waitbar.step(1000)

                if self.before_delete() is False:
                    continue
                if self.model.delete(row, refresh=False) is not True and show_error_messages:
                    if selected_rows.index(row) == len(selected_rows) - 1:
                        self._q2dialogs.q2Mess(self.model.get_data_error())
                    else:
                        if (
                            self._q2dialogs.q2AskYN(
                                q2app.REMOVE_RECORD_ERROR_TEXT
                                + "<br>"
                                + self.model.get_data_error()
                                + "<br>"
                                + q2app.ASK_ROWS_REMOVING_ERRORS_SUPRESS
                            )
                            == 2
                        ):
                            show_error_messages = False
                self.after_delete()
            if waitbar:
                waitbar.close()
            self.model.refresh()
            if self.model.row_count() < 0:
                self.current_row = -1
                self.current_column = -1
            self.set_grid_index(row)
            self.refresh_children()

    def get_grid_selected_rows(self):
        return self.grid_form.get_grid_selected_rows()

    def set_grid_selected_rows(self, index_list):
        return self.grid_form.set_grid_selected_rows(index_list)

    def before_delete(self):
        pass

    def after_delete(self):
        pass

    def crud_save(self, close_form=True):
        if self.before_crud_save() is False:
            return
        crud_data = self.get_crud_form_data()
        if self.crud_mode in [EDIT, VIEW]:
            rez = self.update_current_row(crud_data)
        else:
            rez = self.model.insert(crud_data, self.current_row, refresh=False)
            if self.crud_mode == COPY:
                self.prepare_copy_children_data()
            self.model.refresh()

        if rez:
            self.set_grid_index(self.model.seek_row(crud_data))
        if rez is False:
            self._q2dialogs.q2Mess(self.model.get_data_error())
        else:
            if self.crud_mode == COPY:
                self.copy_children_data()
            self.after_crud_save()
            if close_form:
                self.close()
                self.crud_form = None

    def prepare_copy_children_data(self):
        self.copy_records = {}
        # for action in self.children_forms:
        for pos, action in enumerate(self.children_forms):
            if int_(action["child_copy_mode"]) == 3:
                continue
            if (
                int_(action["child_copy_mode"]) == 1
                and self._q2dialogs.q2AskYN(q2app.ASK_COPY_CHILD_DATA % action["text"]) != 2
            ):
                continue
            self.copy_records[pos] = []
            for row_number in range(action["child_form_object"].model.row_count()):
                source_record = action["child_form_object"].model.get_record(row_number)
                self.copy_records[pos].append(source_record)

    def copy_children_data(self):
        for pos, action in enumerate(self.children_forms):
            if pos not in self.copy_records:
                continue
            for source_record in self.copy_records[pos]:
                action["child_form_object"].model.insert(source_record)

    def update_current_row(self, crud_data):
        rez = self.model.update(crud_data, self.current_row)
        self.set_grid_index(self.current_row)
        return rez

    def get_crud_form_data(self):
        # put data from form into self._model_record
        for x in self.crud_form.widgets:
            if x.startswith("/"):
                continue
            widget = self.crud_form.widgets[x]
            if widget.meta.get("control") in NO_DATA_WIDGETS:
                continue
            self._model_record[x] = self.s.__getattr__(x)

            # if widget.meta.get("check") and not widget.check.get_text():
            if widget.meta.get("check") and not widget.check.is_checked():
                if widget.meta.get("num"):
                    value = "0"
                else:
                    value = ""
                self._model_record[x] = value

        return self._model_record

    def show_crud_form(self, mode, modal="modal"):
        """mode - VIEW, NEW, COPY, EDIT"""
        self.crud_mode = mode
        self.add_crud_buttons(mode)
        self.crud_form = self._Q2FormWindow_class(self, f"{self.title}.[{mode}]")
        self.crud_form.is_crud = True
        self.crud_form.build_form()
        self.set_crud_form_data(mode)
        self.crud_form.show_form(modal=modal)

    def set_crud_form_data(self, mode=EDIT):
        """set current record's value in crud_form"""
        where_string = self.model.get_where()
        where_dict = {}
        if "=" in where_string:
            for part in self.model.get_where().split(" and "):
                eq = part.split("=")
                if len(eq) == 2:
                    if self.controls.get(eq[0].strip()):
                        where_dict[eq[0].strip()] = eq[1].strip()
                else:
                    continue
        else:
            where_dict = {}

        if self.current_row >= 0:
            self.model.refresh_record(self.current_row)
            self._model_record = dict(self.model.get_record(self.current_row))
            for x in self._model_record:
                if x not in self.crud_form.widgets:
                    if mode == NEW:
                        self._model_record[x] = ""
                    continue
                if mode in (NEW, COPY) and x == "seq":
                    self.crud_form.widgets[x].set_text(self.model.get_next_sequence(x, self._model_record[x]))
                if (
                    self.controls.c.__getattr__(x)["pk"]
                    and mode in (NEW, COPY)
                    and not self.controls.c.__getattr__(x)["ai"]
                ):
                    # for new record - get next primary key
                    self.crud_form.widgets[x].set_text(self.model.get_uniq_value(x, self._model_record[x]))

                if self.c.__getattr__(x) is None:
                    if mode == NEW:
                        self._model_record[x] = ""
                    continue
                if self.c.__getattr__(x)["check"]:
                    if self.c.__getattr__(x)["num"]:
                        value = num(self._model_record[x])
                    else:
                        value = self._model_record[x]
                    if value:
                        self.crud_form.widgets[x].check.set_checked(True)
                        # self.crud_form.widgets[x].check.set_text("*")
                if mode == NEW:
                    if x not in where_dict and x != "seq" and not self.controls.c.__getattr__(x)["pk"]:
                        self.crud_form.widgets[x].set_text("")
                        self._model_record[x] = ""
                else:
                    self.crud_form.widgets[x].set_text(self._model_record[x])
        # take care about PK and filters
        for x in self.controls.get_names():
            if x not in self.crud_form.widgets:
                continue
            if mode == EDIT and self.controls.get(x)["pk"] and x in self.crud_form.widgets:
                # Disable primary key when edit
                self.crud_form.widgets[x].set_disabled()
            elif mode == NEW and x in where_dict:
                # set where fields
                if where_dict[x][0] == where_dict[x][-1] and where_dict[x][0] in (
                    '"',
                    "'",
                ):
                    where_dict[x] = where_dict[x][1:-1]  # cut quotes
                self.crud_form.widgets[x].set_text(where_dict[x])
                self.crud_form.widgets[x].set_disabled()

    def _grid_index_changed(self, row, column):
        refresh_children_forms = row != self.current_row and row >= 0
        refresh_children_forms = True
        self.last_current_row = self.current_row
        self.last_current_column = self.current_column
        self.current_row = row
        self.current_column = column
        if refresh_children_forms:
            self.refresh_children()
            self.grid_index_changed()

    def grid_index_changed(self):
        pass

    def refresh_children(self):
        for x in self.actions + self.grid_navi_actions:
            if x.get("engineAction") and "_set_disabled" in x:
                x["_set_disabled"](True if x.get("eof_disabled") and self.model.row_count() <= 0 else False)

        for action in self.children_forms:
            filter = self.get_where_for_child(action)
            action["child_form_object"].model.set_where(filter)
            action["child_form_object"].model.refresh()
            action["child_form_object"].set_grid_index()
            action["child_form_object"].refresh_children()

    def show_child_form(self, action):
        child_form = action.get("child_form")()
        child_form.prev_form = self
        child_form.model.set_where(self.get_where_for_child(action))
        child_form.model.refresh()
        child_form.show_mdi_modal_grid()
        # self.refresh()

    def get_where_for_child(self, action):
        if self.current_row >= 0 and self.model.row_count() > 0:
            current_record = self.model.get_record(self.current_row)

            if action.get("child_form_object"):
                if action.get("child_form_object").grid_form:
                    action["child_form_object"].grid_form.set_enabled()
            return action["child_where"].format(**current_record)
        else:
            if action["child_form_object"].grid_form:
                action["child_form_object"].grid_form.set_disabled()
            return "1=2"

    def grid_header_clicked(self, column, direction=None):
        current_record = self.model.get_record(self.current_row)
        if self.model is not None:
            self._q2dialogs.q2working(lambda: self.model.set_order(column, direction), q2app.MESSAGE_SORTING)
            self.refresh()
            self.set_grid_index(self.model.seek_row(current_record))

    def grid_double_clicked(self):
        for tag in ("select", "view", "edit"):
            action = self.a.tag(tag)
            if action and action.get("worker"):
                action.get("worker")()
                break

    def set_grid_index(self, row=None, column=None):
        if row is None:
            row = self.current_row
        if column is None:
            column = self.current_column
        if self.grid_form:
            self.grid_form.set_grid_index(row, column)

    def move_grid_index(self, mode):
        self.grid_form.move_grid_index(mode)

    def get_controls(self):
        self.add_ok_cancel_buttons()
        self.before_form_build()
        return self.controls + self.system_controls

    def when(self):
        pass

    def valid(self):
        pass

    def before_grid_show(self):
        pass

    def after_grid_show(self):
        pass

    def before_form_show(self):
        pass

    def after_form_show(self):
        pass

    def after_form_closed(self):
        pass

    def before_crud_save(self):
        pass

    def after_crud_save(self):
        pass

    def add_control(
        self,
        column="",
        label="",
        gridlabel="",
        control="",
        pic="",
        data="",
        datatype="char",
        datalen=0,
        datadec=0,
        pk="",
        ai="",
        migrate="*",
        actions=[],
        alignment=-1,
        to_table="",
        to_column="",
        to_form=None,
        related="",
        db=None,
        mask="",
        opts="",
        when=None,
        show=None,
        valid=None,
        changed=None,
        dblclick=None,
        readonly=None,
        disabled=None,
        check=None,
        noform=None,
        nogrid=None,
        widget=None,
        margins=None,
        stretch=0,
        mess="",
        tag="",
        eat_enter=None,
        hotkey="",
        style="",
        **args,
    ):
        """Adds a new control(widget) into the form
        arguments:
        column: name of form variable, also migrates to DB as column name
        label: shows in the form as a label and in the grid as column label
        gridlabel: shows in the grid as column label when not empty
        control: control type - "line", "date", "combo", "list",
                                "radio", "check", "text", "code",
                                "button", "toolbutton"
        pic: some extra data, the meaning depends
            pic="F" if control="line" and datatype="num" - thouthands delimiters
            pic="*" if control="line" - password input
            pic="Item1;Item2;.." if control in ["radio", "list", "combo"] - controls items
        data: initial value for control
        datatype: defines default aligment and input mask
                  if migrate=True - defines sql datatype
        datalen=0: defines lenght of control and sql datatype
        datadec=0: defines mask and sql datatype
        pk: if migrate=True - this column is primary key
        ai: if migrate=True - this column is autoincrement
        migrate="*": if migrate=True - this column will be migrated to sql
        actions: actions (Q2Actions) for widget
        alignment: numbers [1-9] - see see keyboards numpad for meanings

        to_table: this column linked to table (Foreign key)
        to_column: this column linked to to_table.to_column (Foreign key)
        to_form: Q2Form object, that appears to search and select the value of to_column
        related: displayed value from table to_table (sql expression)

        db: explicit database(Q2Db)
        mask: -
        opts: -
        when: focus in callback
        show: -
        valid: focus out, data changed callback
        dblclick: grid double click callback
        readonly: .
        disabled: .
        check: has checkbox, contriol is enabled when it is checked
        noform: do not show this control in the form
        nogrid: do not show this control in the grid
        widget: external widget (QWidget, ....)
        margins: .
        stretch: .
        mess: tooltip message
        tag: extradata, sometimes used as name, sometimes as a color
        eat_enter: by default Enter key works like Tab
        hotkey: usually for control="button", for example "Ok" - "PgDown"
        """

        if isinstance(column, dict):
            self.controls.add_control(**column)
        else:
            d = locals().copy()
            del d["self"]
            self.controls.add_control(**d)
        return True  # Do not delete - it allows indentation in code

    def add_action(
        self,
        text,
        worker=None,
        icon="",
        mess="",
        hotkey="",
        tag="",
        eof_disabled="",
        child_form=None,
        child_where="",
        child_copy_mode=1,
        child_noshow=0,
    ):
        """
        child_form - form class or function(fabric) that returns form object
        """
        d = locals().copy()
        del d["self"]
        self.actions.add_action(**d)

    def validate_impexp_file_name(self, file, filetype):
        ft = re.split(r"[^\w]", filetype)[0].lower()
        filetype = f".{ft}"
        file += "" if file.lower().endswith(filetype) else filetype
        return file

    def hidden_row_hide(self):
        self.hidden_row_toggle("*")

    def hidden_row_show(self):
        self.hidden_row_toggle("")

    def hidden_row_toggle(self, status):
        selected_rows = self.get_grid_selected_rows()
        if selected_rows:
            pk = self.model.get_meta_primary_key()
            waitbar = None
            if len(selected_rows) > 10:
                waitbar = self.show_progressbar(q2app.MESSAGE_ROWS_HIDING, len(selected_rows))
            for row in selected_rows:
                if waitbar:
                    waitbar.step(1000)
                dic = {pk: self.model.get_record(row)[pk]}
                dic["q2_hidden"] = status
                self.model.update(dic, self.current_row, refresh=False)
            self.model.refresh()
            self.set_grid_index(self.current_row)
            if waitbar:
                waitbar.close()

    def hidden_row_show_not_hidden(self):
        self.model.set_hidden_row_status("show_not_hidden")
        self.refresh()

    def hidden_row_show_all(self):
        self.model.set_hidden_row_status("show_all")
        self.refresh()

    def hidden_row_show_hidden(self):
        self.model.set_hidden_row_status("show_hidden")
        self.refresh()

    def grid_data_export(self):
        file, filetype = q2app.q2_app.get_save_file_dialoq(
            q2app.MESSAGE_GRID_DATA_EXPORT_TITLE, filter="CSV (*.csv);;JSON(*.json)"
        )
        if not file:
            return
        file = self.validate_impexp_file_name(file, filetype)
        waitbar = self._q2dialogs.Q2WaitShow(
            q2app.MESSAGE_GRID_DATA_EXPORT_WAIT % file, self.model.row_count()
        )
        try:
            self.model.data_export(file, tick_callback=lambda: waitbar.step(1000))
        except Exception as e:
            self._q2dialogs.q2Mess(q2app.MESSAGE_GRID_DATA_EXPORT_ERROR % (file + ": " + str(e)))
            waitbar.close()
        else:
            _count, _time = waitbar.close()
            self._q2dialogs.q2Mess(q2app.MESSAGE_GRID_DATA_EXPORT_DONE % (_count, _time))
        waitbar.close()

    def grid_data(self, row, col, skip_format=False):
        return self.model.data(row, col, skip_format=skip_format)

    def grid_data_import(self):
        file, filetype = q2app.q2_app.get_open_file_dialoq(
            q2app.MESSAGE_GRID_DATA_IMPORT_TITLE, filter="CSV (*.csv);;JSON(*.json)"
        )
        if not file:
            return
        file = self.validate_impexp_file_name(file, filetype)
        waitbar = self._q2dialogs.Q2WaitShow(q2app.MESSAGE_GRID_DATA_IMPORT_WAIT % file)
        try:
            self.model.data_import(file, tick_callback=lambda: waitbar.step(1000))
        except Exception as e:
            self._q2dialogs.q2Mess(
                q2app.MESSAGE_GRID_DATA_IMPORT_ERROR % (self.db.last_sql_error + ": " + str(e))
            )
            waitbar.close()
        else:
            _count, _time = waitbar.close()
            self._q2dialogs.q2Mess(q2app.MESSAGE_GRID_DATA_IMPORT_DONE % (_count, _time))

    def set_grid_row_colors(self):
        selected_rows = self.get_grid_selected_rows()
        if selected_rows:
            _form: Q2Form = self.q2_app.Q2Form(q2app.ACTION_TOOLS_COLOR_TEXT)
            _form.add_control("/v")
            q2_bcolor = self.r.__getattr__("q2_bcolor")
            _bcolor = f"#{int_(q2_bcolor):06x}"
            q2_fcolor = self.r.__getattr__("q2_fcolor")
            _fcolor = f"#{int_(q2_fcolor):06x}"
            _form.add_control("fcolor", _("Font color"), control="color", data=_fcolor, datalen=20)
            _form.add_control("bcolor", _("Background color"), control="color", data=_bcolor, datalen=20)

            def reset_colors():
                _form.s.fcolor = "#000000"
                _form.s.bcolor = "#000000"

            _form.add_control(
                "reset_colors", _("Reset colors"), datalen=15, control="button", valid=reset_colors
            )
            _form.ok_button = True
            _form.cancel_button = True
            _form.init_size = [300, 300]

            def colors_valid():
                not_valid = False
                color = _form.s.fcolor
                _form.s.fcolor = "#000000"
                _form.s.fcolor = color
                if color != _form.s.fcolor:
                    self._q2dialogs.q2Mess(_("Foreground color is not valid! "))
                    not_valid = True

                color = _form.s.bcolor
                _form.s.bcolor = "#000000"
                _form.s.bcolor = color
                if color != _form.s.bcolor:
                    self._q2dialogs.q2Mess(_("Background color is not valid! "))
                    not_valid = True

                return not not_valid

            _form.valid = colors_valid
            _form.run()
            if _form.ok_pressed:
                pk = self.model.get_meta_primary_key()
                waitbar = None
                if len(selected_rows) > 10:
                    waitbar = self.show_progressbar(q2app.MESSAGE_ROWS_COLOR, len(selected_rows))
                for row in selected_rows:
                    if waitbar:
                        waitbar.step(1000)
                    dic = {pk: self.model.get_record(row)[pk]}
                    _form.s.fcolor = _form.s.fcolor if _form.s.fcolor else "0"
                    _form.s.bcolor = _form.s.bcolor if _form.s.bcolor else "0"

                    dic["q2_fcolor"] = int(_form.s.fcolor.lstrip("#"), 16)
                    dic["q2_bcolor"] = int(_form.s.bcolor.lstrip("#"), 16)
                    self.model.update(dic, self.current_row, refresh=False)
                self.model.refresh()
                self.set_grid_index(self.current_row)
                if waitbar:
                    waitbar.close()

    def grid_data_paste_clipboard(self):
        Q2PasteClipboard(self)

    def grid_data_bulk_update(self):
        Q2BulkUpdate(self)

    def grid_print(self):
        self._q2dialogs.q2mess("Must be implemented")

    def grid_data_info(self):
        columns = self.model.columns
        self._q2dialogs.q2Mess(
            f"{q2app.GRID_DATA_INFO_TABLE}: {self.model.get_table_name()}"
            f"<br>{q2app.GRID_DATA_INFO_ROWS}: {self.model.row_count()}"
            f"<br>{q2app.GRID_DATA_INFO_ORDER}: {self.model.get_order()}"
            f"<br>{q2app.GRID_DATA_INFO_FILTER}: {html.escape(self.model.get_where())}"
            f"<br>{q2app.GRID_DATA_INFO_COLUMNS}: {columns}"
        )

    def set_style_sheet(self, css: str):
        self.style_sheet = css
        for x in self.form_stack:
            x.set_style_sheet(self.style_sheet)

    def prepare_where(self, column=None, control1=None, control2=None):
        mem_widgets = self.widgets().keys()
        if control1 is None:
            if column in mem_widgets:
                control1 = column
            elif column + "____1" in mem_widgets:
                control1 = column + "____1"
        if control1 not in mem_widgets:
            return ""

        if not self.w.__getattr__(control1).is_checked():
            return ""

        # control_datatype = self.controls.c.__getattr__(control1)["datatype"]
        date_control = self.controls.c.__getattr__(control1)["datatype"] == "date"
        num_control = self.controls.c.__getattr__(control1).get("num")
        control1_value = self.s.__getattr__(control1)
        if control2 is None:
            if control1.endswith("____1"):
                control2 = control1[:-5] + "____2"
                control2_value = self.s.__getattr__(control2)
            else:
                control2_value = None
        if date_control:
            if control1_value == "0000-00-00":
                control1_value = ""
            if control2_value == "0000-00-00":
                control2_value = ""
        elif num_control:
            control1_value = num(control1_value)
            if control2_value:
                control2_value = num(control2_value)

        if (control2_value is None) or control1_value == control2_value:
            if date_control or num_control:
                return f"{column} = '{control1_value}'"
            else:
                return f"{column} like '%{control1_value}%'"
        elif (control1_value and not control2_value) or (control2_value and control1_value > control2_value):
            return f"{column} >= '{control1_value}'"
        elif not control1_value and control2_value:
            return f"{column} <= '{control2_value}'"
        elif control1_value and control2_value:
            return f"{column} >= '{control1_value}' and {column}<='{control2_value}'"
        return ""


class Q2FormWindow:
    def __init__(self, q2_form: Q2Form, title=""):
        super().__init__()
        self.title = title if title else q2_form.title
        self.shown = False
        self.q2_form = q2_form
        self.form_is_active = False
        # self.title = ""
        self.widgets = {}
        self.tab_widget_list = []
        self.tab_widget = None
        # Must be defined in any subclass
        self._widgets_package = None
        self.escape_enabled = True
        self.mode = "form"
        self.hotkey_widgets = {}
        self.grid_actions = q2app.Q2Actions()
        self._in_close_flag = None
        self.is_crud = None
        self.not_closed = True

    def on_activate(self):
        if self.mode == "grid":
            self.q2_form.q2_app.show_statusbar_mess(self.q2_form.model.row_count())

    def create_grid_navigation_actions(self):
        """returns standard actions for the grid"""
        actions = q2app.Q2Actions()
        actions.add_action(text="-")
        actions.add_action(
            text=q2app.ACTION_FIRST_ROW_TEXT,
            worker=lambda: self.move_grid_index(7),
            icon=q2app.ACTION_FIRST_ROW_ICON,
            hotkey=q2app.ACTION_FIRST_ROW_HOTKEY,
            eof_disabled=1,
        )
        actions.add_action(
            text=q2app.ACTION_PREVIOUS_ROW_TEXT,
            worker=lambda: self.move_grid_index(8),
            icon=q2app.ACTION_PREVIOUS_ROW_ICON,
            eof_disabled=1,
        )
        actions.add_action(
            text=q2app.ACTION_REFRESH_TEXT,
            worker=lambda: self.q2_form.refresh(),
            icon=q2app.ACTION_REFRESH_ICON,
            hotkey=q2app.ACTION_REFRESH_HOTKEY,
        )
        actions.add_action(
            text=q2app.ACTION_NEXT_ROW_TEXT,
            worker=lambda: self.move_grid_index(2),
            icon=q2app.ACTION_NEXT_ROW_ICON,
            eof_disabled=1,
        )
        actions.add_action(
            text=q2app.ACTION_LAST_ROW_TEXT,
            worker=lambda: self.move_grid_index(1),
            icon=q2app.ACTION_LAST_ROW_ICON,
            hotkey=q2app.ACTION_LAST_ROW_HOTKEY,
            eof_disabled=1,
        )
        # HIIDEN rows menu

        show_color_menu = (
            hasattr(self.q2_form.model, "check_db_column")
            and self.q2_form.model.check_db_column("q2_bcolor")
            and not self.q2_form.model.readonly
        )

        show_hide_menu = (
            hasattr(self.q2_form.model, "check_db_column")
            and self.q2_form.model.check_db_column("q2_hidden")
            and not self.q2_form.model.readonly
        )

        if show_color_menu or show_hide_menu:
            actions.add_action(text="-")
            actions.add_action(
                text=q2app.ACTION_HIDDEN_ROW_TEXT,
                icon=q2app.ACTION_HIDDEN_ROW_ICON,
            )
        if show_color_menu:
            actions.add_action(
                text=q2app.ACTION_HIDDEN_ROW_TEXT + "|" + q2app.ACTION_TOOLS_COLOR_TEXT,
                icon=q2app.ACTION_TOOLS_COLOR_ICON,
                worker=self.q2_form.set_grid_row_colors,
                eof_disabled=1,
            )
            actions.add_action(
                text=q2app.ACTION_HIDDEN_ROW_TEXT + "|-",
            )
        if show_hide_menu:
            actions.add_action(
                text=q2app.ACTION_HIDDEN_ROW_TEXT + "|" + q2app.ACTION_HIDE_ROW_TEXT,
                icon=q2app.ACTION_HIDE_ROW_ICON,
                worker=self.q2_form.hidden_row_hide,
                eof_disabled=1,
            )
            actions.add_action(
                text=q2app.ACTION_HIDDEN_ROW_TEXT + "|" + q2app.ACTION_SHOW_ROW_TEXT,
                icon=q2app.ACTION_SHOW_ROW_ICON,
                worker=self.q2_form.hidden_row_show,
                eof_disabled=1,
            )
            actions.add_action(
                text=q2app.ACTION_HIDDEN_ROW_TEXT + "|-",
            )
            actions.add_action(
                text=q2app.ACTION_HIDDEN_ROW_TEXT + "|" + q2app.ACTION_SHOW_NOTHIDDEN_TEXT,
                icon=q2app.ACTION_SHOW_NOTHIDDEN_ICON,
                worker=self.q2_form.hidden_row_show_not_hidden,
            )
            actions.add_action(
                text=q2app.ACTION_HIDDEN_ROW_TEXT + "|" + q2app.ACTION_SHOW_ALL_TEXT,
                icon=q2app.ACTION_SHOW_ALL_ICON,
                worker=self.q2_form.hidden_row_show_all,
            )
            actions.add_action(
                text=q2app.ACTION_HIDDEN_ROW_TEXT + "|" + q2app.ACTION_SHOW_HIDDEN_TEXT,
                icon=q2app.ACTION_SHOW_HIDDEN_ICON,
                worker=self.q2_form.hidden_row_show_hidden,
            )

        actions.add_action(text="-")
        actions.add_action(
            text=q2app.ACTION_TOOLS_TEXT,
            icon=q2app.ACTION_TOOLS_ICON,
        )
        actions.add_action(
            text=q2app.ACTION_TOOLS_TEXT + "|" + q2app.ACTION_TOOLS_EXPORT_TEXT,
            worker=self.q2_form.grid_data_export,
            icon=q2app.ACTION_TOOLS_EXPORT_ICON,
            eof_disabled=1,
        )

        if self.q2_form.is_grid_updateable():
            actions.add_action(
                text=q2app.ACTION_TOOLS_TEXT + "|" + q2app.ACTION_TOOLS_IMPORT_TEXT,
                worker=self.q2_form.grid_data_import,
                icon=q2app.ACTION_TOOLS_IMPORT_ICON,
            )
        actions.add_action(
            text=q2app.ACTION_TOOLS_TEXT + "|-",
        )

        actions.add_action(
            text=q2app.ACTION_TOOLS_TEXT + "|" + q2app.ACTION_TOOLS_IMPORT_CLIPBOARD_TEXT,
            worker=self.q2_form.grid_data_paste_clipboard,
            icon=q2app.ACTION_TOOLS_IMPORT_CLIPBOARD_ICON,
        )

        actions.add_action(
            text=q2app.ACTION_TOOLS_TEXT + "|" + q2app.ACTION_TOOLS_BULK_UPDATE_TEXT,
            worker=self.q2_form.grid_data_bulk_update,
            icon=q2app.ACTION_TOOLS_BULK_UPDATE_ICON,
            eof_disabled=1,
        )

        actions.add_action(
            text=q2app.ACTION_TOOLS_TEXT + "|-",
        )

        actions.add_action(
            text=q2app.ACTION_TOOLS_TEXT + "|" + "Print",
            worker=self.q2_form.grid_print,
            icon="print",
            eof_disabled=1,
        )

        actions.add_action(
            text=q2app.ACTION_TOOLS_TEXT + "|-",
        )

        actions.add_action(
            text=q2app.ACTION_TOOLS_TEXT + "|" + q2app.ACTION_TOOLS_INFO_TEXT,
            worker=self.q2_form.grid_data_info,
            icon=q2app.ACTION_TOOLS_INFO_ICON,
        )

        if not self.q2_form.i_am_child:
            actions.add_action(text="-")
            actions.add_action(
                text=q2app.ACTION_CLOSE_TEXT, worker=self.close, icon=q2app.ACTION_CLOSE_ICON, tag="orange"
            )
        self.q2_form.grid_navigation_actions_hook(actions)
        return actions

    def move_grid_index(self, direction=None):
        """Directions - look at numpad to get the idea"""
        if direction == 7:  # Top
            self.set_grid_index(0, self.get_grid_index()[1])
        elif direction == 8:  # Up
            self.set_grid_index(self.get_grid_index()[0] - 1, self.get_grid_index()[1])
        elif direction == 2:  # Down
            self.set_grid_index(self.get_grid_index()[0] + 1, self.get_grid_index()[1])
        elif direction == 1:  # Last
            self.set_grid_index(self.get_grid_row_count(), self.get_grid_index()[1])

    def set_grid_index(self, row=0, col=0):
        self.widgets["form__grid"].set_index(row, col)

    def get_grid_index(self):
        return self.widgets["form__grid"].current_index()

    def get_grid_selected_rows(self):
        return self.widgets["form__grid"].get_selected_rows()

    def set_grid_selected_rows(self, index_list=[]):
        self.widgets["form__grid"].set_selected_rows(index_list)

    def get_grid_row_count(self):
        return self.widgets["form__grid"].row_count()

    def build_grid(self):
        # populate model with columns metadata
        self.mode = "grid"
        tmp_grid_form = Q2Form()
        tmp_grid_form.add_control("/vs", tag="gridsplitter")
        self.q2_form.grid_navi_actions = self.create_grid_navigation_actions()

        tmp_grid_form.add_control(
            "form__grid",
            control="grid",
            actions=[self.q2_form.actions, self.q2_form.grid_navi_actions],
            # stretch=100,
        )
        # place child forms
        if self.q2_form.max_child_level:
            for action in self.q2_form.actions:
                if action.get("child_form") and not action.get("child_noshow"):
                    tmp_grid_form.add_control("/t", action.get("text", "="), stretch=1)
                    #  create child form!
                    action["child_form_object"] = action.get("child_form")()
                    action["child_form_object"].prev_form = self.q2_form
                    action["child_form_object"].title = self.q2_form.title + " / " + action["text"]
                    action["child_form_object"].i_am_child = True
                    action["child_form_object"].max_child_level = self.q2_form.max_child_level - 1
                    self.q2_form.children_forms.append(action)
                    tmp_grid_form.add_control(
                        f"child_grid__{action['text']}",
                        widget=action["child_form_object"],
                    )
        tmp_grid_form.add_control("/")

        if self.q2_form.show_app_modal_form is False:
            tmp_grid_form.controls[-1], tmp_grid_form.controls[-2] = (
                tmp_grid_form.controls[-2],
                tmp_grid_form.controls[-1],
            )
        self.build_form(tmp_grid_form.get_controls())
        self.q2_form.refresh_children()
        self.move_grid_index(1)

    def grid_navigation_actions_hook(self, actions):
        pass

    def build_form(self, controls=[]):
        frame_stack = [self]
        tmp_frame = None

        if controls == []:
            controls = self.q2_form.get_controls()
        # set deafault layout to Form if first line not a layout def
        if controls and not controls[0].get("column", "").startswith("/"):
            controls.insert(0, {"column": "/f"})
        # Create widgets
        for meta in controls:
            meta["form"] = self.q2_form
            meta["q2_app"] = q2app.q2_app
            meta["form_window"] = self
            if meta.get("noform", ""):
                continue
            meta = q2app.Q2Controls.validate(meta)
            current_frame = frame_stack[-1]
            # do not add widget if it is not first tabpage on the form
            if not (meta.get("column", "") == ("/t") and self.tab_widget is not None):
                # get widgets to add
                label2add, widget2add = self.widget(meta)

                if current_frame.frame_mode == "f":  # form layout
                    # if label2add is not None:
                    #     label2add.set_content_margins(10, int(q2app.q2_app.get_char_height() / 4), 2, 0)
                    if hasattr(widget2add, "frame_mode") and not meta.get("relation"):
                        # add any frame into form frame
                        if label2add is None:
                            label2add = self._get_widget("label")({"label": meta.get("label", "")})
                            widget2add.label = label2add
                        widget2add.hide_border()
                    current_frame.add_row(label2add, widget2add)
                else:  # v- h- box layout
                    if label2add is not None:
                        if (
                            current_frame != self
                            and current_frame.get_widget_count() == 0
                            and current_frame.label
                            and frame_stack[-2].frame_mode == "f"
                        ):
                            # when frame prev frame is FORM and it is first widget
                            # in the current frame - move widget label to frame label
                            # which is prev FORM frame )
                            current_frame.label.set_text(label2add.get_text())
                            if widget2add:
                                widget2add.label = current_frame.label
                        else:
                            current_frame.add_widget(label2add)
                    if widget2add is not None:
                        if meta.get("column", "") in ("/vr", "/hr"):  # scroller
                            scroller = self._get_widget("scroller")({"widget": widget2add})
                            current_frame.add_widget(scroller)
                        else:
                            current_frame.add_widget(widget2add)
                        if meta.get("control") == "toolbar":  # context menu for frame
                            widget2add.set_context_menu(current_frame)
            # Hotkeys
            if meta.get("hotkey") and meta.get("valid"):
                if meta.get("hotkey") not in self.hotkey_widgets:
                    self.hotkey_widgets[meta.get("hotkey")] = []
                self.hotkey_widgets[meta.get("hotkey")].append(widget2add)
            # Special cases
            if meta.get("column", "") == ("/t"):
                if self.tab_widget is None:
                    self.tab_widget = widget2add
                    frame_stack.append(widget2add)
                    self.tab_widget_list.append(widget2add)
                else:  # If second and more tabpage widget
                    if tmp_frame in frame_stack:
                        frame_stack = frame_stack[: frame_stack.index(tmp_frame)]
                tmp_frame = self.widget({"column": "/v"})[1]
                self.tab_widget.add_tab(tmp_frame, meta.get("label", ""))
                frame_stack.append(tmp_frame)
            elif meta.get("column", "") == ("/s"):
                continue  # do not touch - see elif +2
            elif meta.get("column", "") == "/":
                if len(frame_stack) > 1:
                    frame_stack.pop()
                    # Remove tab widget if it is at the end of stack
                    if "q2tab.q2tab" in f"{type(frame_stack[-1])}":
                        self.tab_widget = None
                        frame_stack.pop()
            elif meta.get("column", "").startswith("/"):
                frame_stack.append(widget2add)

        if len(self.tab_widget_list) > 1:
            for x in self.tab_widget_list:
                x.set_shortcuts_local()

        # Make it no more working
        self.build_grid = lambda: None
        self.build_form = lambda: None

    def widget(self, meta):
        """Widgets fabric"""
        if not meta.get("control") or meta.get("control") == "":
            if meta.get("widget"):
                control = "widget"
            else:
                control = "line" if meta.get("column") else "label"
        else:
            control = meta.get("control")

        if meta.get("to_table"):  # relation is here
            control = "relation"

        if control == "":
            control = "label"

        column = meta.get("column", "")
        label = meta.get("label", "")
        class_name = ""

        widget2add = None
        if label and control not in NO_LABEL_WIDGETS:
            label2add = self._get_widget("label")(meta)
        else:
            label2add = None

        # Form or widget
        if control == "widget":
            if isinstance(meta.get("widget"), Q2Form):
                if meta.get("widget").model is not None:
                    widget2add = meta.get("widget").get_grid_widget()
                else:
                    widget2add = meta.get("widget").get_form_widget()
                widget2add.meta = meta
                widget2add.form_is_active = True
            else:
                widget2add = meta.get("widget")
            if not hasattr(widget2add, "meta"):
                setattr(widget2add, "meta", meta)
        else:  # Special cases
            if column[:2] in ("/h", "/v", "/f"):  # frame
                control = "frame"
                class_name = "frame"
                label2add = None
            elif "/" == column:
                return None, None
            elif "/t" in column:  # Tabpage
                label2add = None
                control = "tab"
            elif control.startswith("code"):
                control = "code"
            elif "radio" in control:
                control = "radio"
            elif "toolbar" in control:
                control = "toolbar"
            elif column == "/s":
                control = "space"

            widget_class = self._get_widget(control, class_name)
            widget2add = widget_class(meta)

            if hasattr(widget2add, "label"):
                widget2add.label = label2add
        if meta.get("check"):  # has checkbox
            # label2add = self._get_widget("check", "check")({"label": meta["label"], "stretch": 0})
            label2add = self._get_widget("check", "check")(
                {"label": meta["label"] if meta["control"] != "check" else "Turn on", "stretch": 0}
            )

            label2add.add_managed_widget(widget2add)
            if not meta.get("data"):
                widget2add.set_disabled()
            else:
                label2add.set_checked()

        self.widgets[meta.get("tag", "") if meta.get("tag", "") else column] = widget2add

        action2add = None
        if meta.get("actions") and meta.get("control") != "toolbar":
            action2add = self._get_widget("toolbar", "toolbar")(
                {
                    "control": "toolbar",
                    "actions": meta["actions"],
                    "form": self.q2_form,
                    "stretch": 0,
                }
            )
            action2add.set_context_menu(widget2add)
            action2add.fix_default_height()
            # Actions!
            if widget2add and action2add:
                if control == "label" or (not action2add.show_main_button and not action2add.show_actions):
                    action_frame = self._get_widget("frame")({"column": "/v"})
                else:
                    #  Splitter!
                    action_frame = self._get_widget("frame")({"column": "/vs"})
                    self.widgets[meta.get("tag", "") if meta.get("tag", "") else column + "_splitter"] = (
                        action_frame
                    )
                action_frame.add_widget(action2add)
                action_frame.add_widget(widget2add)
                widget2add = action_frame

        return label2add, widget2add

    def _get_widget(self, module_name, class_name=""):
        """For given name returns class from current GUI engine module"""
        if class_name == "":
            class_name = module_name
        module_name = f"q2{module_name}"
        class_name = f"q2{class_name}"
        try:
            # print(self._widgets_package, module_name)
            return getattr(getattr(self._widgets_package, module_name), class_name)
        except Exception:
            # print(self._widgets_package, module_name, class_name)
            return getattr(getattr(self._widgets_package, "q2label"), "q2label")

    def show_form(self, modal="modal", no_build=False):
        if no_build is False:
            self.build_form()
        self.set_style_sheet(self.q2_form.style_sheet)

        self.q2_form.form_stack.append(self)

        # Restore grid columns sizes
        self.restore_splitters()
        self.restore_grid_columns()

        if self.mode == "grid":
            if self.q2_form.before_grid_show() is False:
                self.q2_form.form_stack.pop()
                return
        elif self.mode == "form":
            self.form_is_active = True
            if self.q2_form.before_form_show() is False:
                self.q2_form.form_stack.pop()
                return
        # search for the first enabled widget
        for x, widget in self.q2_form.widgets().items():
            if not x.startswith("/") and widget is not None:
                if hasattr(widget, "can_get_focus") and not widget.can_get_focus():
                    continue
                elif hasattr(widget, "is_enabled") and widget.is_enabled():
                    widget.set_focus()
                    break
                elif hasattr(widget, "get_check") and widget.get_check():
                    if widget.get_check().is_enabled():
                        widget.get_check().set_focus()
                    break
        self.q2_form.q2_app.show_form(self, modal)
        # print(">>", len(set(self.q2_form.q2_app.QApplication.allWidgets())))

    def get_controls_list(self, name: str):
        return [self.widgets[x] for x in self.widgets if type(self.widgets[x]).__name__ == name]

    def restore_splitters(self):
        # Restore splitters sizes
        for x in self.get_splitters():
            sizes = q2app.q2_app.settings.get(
                self.window_title,
                f"splitter-{x}",
                "",
            )
            self.widgets[x].splitter.set_sizes(sizes)

    def restore_grid_columns(self):
        # for grid in self.get_grid_list():
        for grid in self.get_controls_list("q2grid"):
            col_settings = {}
            for count, x in enumerate(self.q2_form.model.headers):
                data = q2app.q2_app.settings.get(self.window_title, f"grid_column__'{x}'")
                if data == "":
                    if (
                        self.q2_form.model.meta[count].get("relation")
                        or self.q2_form.model.meta[count].get("num") is None
                    ):
                        c_w = q2app.GRID_COLUMN_WIDTH
                    else:
                        c_w = int_(self.q2_form.model.meta[count].get("datalen"))
                    c_w = int(q2app.q2_app.get_char_width() * (min(c_w, q2app.GRID_COLUMN_WIDTH)))
                    data = f"{count}, {c_w}"
                if len(self.q2_form.model.headers) == 1:
                    data = "0, 3000"
                col_settings[x] = data
            grid.set_column_settings(col_settings)
        for x in self.get_controls_list("Q2FormWindow"):
            x.restore_grid_columns()
            x.restore_splitters()

    def save_grid_columns(self):
        for grid in self.get_controls_list("q2grid"):
            for x in grid.get_columns_settings():
                q2app.q2_app.settings.set(
                    self.window_title,
                    f"grid_column__'{x['name']}'",
                    x["data"],
                )
        for x in self.get_controls_list("Q2FormWindow"):
            x.close()

    def close(self):
        if self._in_close_flag:
            return
        self._in_close_flag = True
        if self in self.q2_form.form_stack[-1:]:
            self.q2_form.form_stack.pop()
        self.save_splitters()
        self.save_grid_columns()
        if hasattr(q2app.q2_app, "settings"):
            self.save_geometry(q2app.q2_app.settings)
        self.q2_form._close(self)
        if self.is_crud:
            self.q2_form.crud_form = None

    def save_splitters(self):
        if not hasattr(q2app.q2_app, "settings"):
            return
        for x in self.get_splitters():
            q2app.q2_app.settings.set(
                self.window_title,
                f"splitter-{x}",
                self.widgets[x].splitter.get_sizes(),
            )

    def get_splitters(self):
        return [
            x
            for x in self.widgets.keys()
            if hasattr(self.widgets[x], "splitter") and self.widgets[x].splitter is not None
        ]

    def set_style_sheet(self, css):
        pass


class Q2FormData:
    """Get and put data from/to form"""

    def __init__(self, q2_form: Q2Form):
        self.q2_form = q2_form

    def __setattr__(self, name, value):
        if name != "q2_form":
            if self.q2_form.crud_form:
                widget = self.q2_form.crud_form.widgets.get(name)
            elif self.q2_form.form_stack:
                widget = self.q2_form.form_stack[-1].widgets.get(name)
            else:
                widget = None
            if hasattr(widget, "set_text"):
                widget.set_text(value)
            else:  # no widget - put data to model's record
                self.q2_form._model_record[name] = value
        else:
            self.__dict__[name] = value

    def __getattr__(self, name):
        if self.q2_form.crud_form:
            widget = self.q2_form.crud_form.widgets.get(name)
        elif self.q2_form.form_stack == []:
            if self.q2_form.last_closed_form is None:
                return None
            else:
                # widget = self.q2_form.last_closed_form.widgets.get(name)
                # widget = self.q2_form.last_closed_form_widgets_text.get(name)
                return self.q2_form.last_closed_form_widgets_text.get(name, "")
        else:
            widget = self.q2_form.form_stack[-1].widgets.get(name)
        if widget is not None:
            if hasattr(widget, "get_text"):
                return widget.get_text()
            else:
                return ""
        else:  # no widget here? get data from model
            return self.q2_form._model_record.get(name, None)


class Q2FormWidget:
    """Get widget object from form"""

    def __init__(self, q2_form: Q2Form):
        self.q2_form = q2_form

    def __getattr__(self, attrname):
        widget = None
        if self.q2_form.crud_form:
            widgets = self.q2_form.crud_form.widgets
        elif self.q2_form.form_stack == []:
            if self.q2_form.last_closed_form is None:
                return None
            else:
                widgets = self.q2_form.last_closed_form.widgets
                widgets = self.last_closed_form_widgets
        else:
            widgets = self.q2_form.form_stack[-1].widgets
        if attrname.startswith("_") and attrname.endswith("_"):
            pos = int_(attrname.replace("_", ""))
            if pos < len(widgets):
                widget = widgets.get(list(widgets)[pos])
        else:
            widget = widgets.get(attrname)
        if widget is not None:
            return widget


class Q2FormAction:
    def __init__(self, q2_form):
        self.q2_form: Q2Form = q2_form

    def tag(self, tag=""):
        if tag:
            for act in self.q2_form.actions:
                if act.get("tag") == tag:
                    return act
        return {}

    def __getattr__(self, name):
        for act in self.q2_form.actions:
            if act.get("text") == name:
                return act
        return {}


class Q2ModelData:
    def __init__(self, q2_form: Q2Form):
        self.q2_form = q2_form

    def __getattr__(self, name):
        self.q2_form.model.refresh_record(self.q2_form.current_row)
        datadic = self.q2_form.model.get_record(self.q2_form.current_row)
        return datadic.get(name, "")


class Q2PasteClipboard:
    def __init__(self, q2_form: Q2Form):
        self.q2_form = q2_form
        self.cliptext = q2app.q2_app.get_clipboard_text()
        self.clipboard_headers = self.cliptext.split("\n")[0].split("\t")
        self.load_target()
        self.load_source()
        self.load_data()
        self.load_set()
        if self.show_main_form().ok_pressed:
            self.save_set()
            self.paste_to_form()

    def paste_to_form(self):
        source_map = {x["source_column"]: x["_target_column"] for x in self.target_data if x["source_column"]}
        if not self.main_form.s.first_row_is_header:
            self.data_data.insert(0, {f"{x}": x for x in self.clipboard_headers})

        waitbar = self.q2_form.show_progressbar(q2app.PASTE_CLIPBOARD_WAIT, len(self.data_data))

        self.q2_form.show_crud_form(NEW, modal="")

        for row in self.data_data:
            waitbar.step(1000)
            for col in row:
                if col in source_map:
                    col_def = self.q2_form.c.__getattr__(source_map[col])
                    if col_def.get("num") and int_(col_def.get("datadec")) > 0 and "," in row[col]:
                        row[col] = nums(row[col])
                    self.q2_form.s.__setattr__(source_map[col], row[col])
            self.q2_form.crud_save(close_form=False)
            self.q2_form.before_form_show()
        self.q2_form.close()
        waitbar.close()

    def save_set(self):
        q2app.q2_app.settings.set(
            self.q2_form.title,
            f"paste-{self.target_hash}-{self.source_hash}",
            json.dumps(self.target_data),
        )

    def show_main_form(self):
        self.main_form = self.q2_form.q2_app.Q2Form(q2app.PASTE_CLIPBOARD_TITLE)
        self.main_form.add_control("/v")
        self.main_form.add_control(
            "first_row_is_header", q2app.PASTE_CLIPBOARD_FIRST_ROW, control="check", data="*"
        )
        self.main_form.add_control("/vs", tag="vs")
        self.main_form.add_control("/hs", tag="hs")
        self.main_form.add_control("target_form", widget=self.target_form)

        # csv_form.add_control("/v")
        # csv_form.add_control("/s")
        # csv_form.add_control("to_target", "<>", datalen=4, control="button", valid=self.move_it)
        # csv_form.add_control("/")

        self.main_form.add_control("source_form", widget=self.source_form)
        self.main_form.add_control("/")
        self.main_form.add_control("", q2app.PASTE_CLIPBOARD_CLIPBOARD_DATA)
        self.main_form.add_control("data_form", widget=self.data_form)

        self.main_form.cancel_button = True
        self.main_form.ok_button = True
        self.main_form.add_ok_cancel_buttons()
        self.main_form.show_form()

        return self.main_form

    def move_it(self):
        target_row = self.target_form.current_row
        source_row = self.source_form.current_row
        target_row_data = self.target_form.get_current_record()
        source_row_data = self.source_form.get_current_record()
        if target_row_data["source_column"] == "" and source_row_data["column"]:
            # move left
            target_row_data["source_column"] = source_row_data["column"]
            source_row_data["column"] = ""
        else:
            # swap
            target_row_data["source_column"], source_row_data["column"] = (
                source_row_data["column"],
                target_row_data["source_column"],
            )

        self.target_form.model.update(target_row_data, target_row)
        self.source_form.model.update(source_row_data, source_row)

        if self.target_form.w.form__grid.has_focus():
            source_row += 1
        elif self.source_form.w.form__grid.has_focus():
            target_row += 1
        self.target_form.set_grid_index(target_row)
        self.source_form.set_grid_index(source_row)

    def load_set(self):
        last_set = q2app.q2_app.settings.get(
            self.q2_form.title,
            f"paste-{self.target_hash}-{self.source_hash}",
            None,
        )

        if last_set:
            self.target_data = json.loads(last_set)
            self.target_form.model.set_records(self.target_data)
            for x in self.target_data:
                col_name = x["source_column"]
                for row, dic in enumerate(self.source_data):
                    if dic["column"] == col_name:
                        self.source_data[row]["column"] = ""
                        break

    def myhash(self, mystr):
        rez = 1
        for x in range(len(mystr)):
            rez += rez * x * ord(mystr[x])
        return rez & 0xFFFFFFFF

    def load_target(self):
        self.target_form = self.q2_form.q2_app.Q2Form(q2app.PASTE_CLIPBOARD_TARGET)
        self.target_data = []
        target_hash_string = ""
        for x in self.q2_form.controls:
            if x["migrate"]:
                target_hash_string += x.get("column")
                self.target_data.append(
                    {
                        "target_column": f'{x.get("label") if x.get("label") else x.get("gridlabel")} '
                        + f'({self.q2_form.model.get_table_name()}.{x.get("column")})',
                        "_target_column": x.get("column"),
                        "source_column": "",
                    },
                )
        self.target_hash = self.myhash(target_hash_string)

        self.target_form.set_model(Q2Model())
        self.target_form.model.set_records(self.target_data)
        self.target_form.add_control(
            "target_column", q2app.PASTE_CLIPBOARD_TARGET_COLUMNS, control="line", datalen=100
        )
        self.target_form.add_control(
            "source_column", q2app.PASTE_CLIPBOARD_SOURCE_COLUMNS, control="line", datalen=100
        )
        self.target_form.grid_double_clicked = self.move_it
        self.target_form.i_am_child = 1

    def load_source(self):
        self.source_data = [{"column": x} for x in self.clipboard_headers]
        self.source_hash = self.myhash(",".join(self.clipboard_headers))
        self.source_form = self.q2_form.q2_app.Q2Form(q2app.PASTE_CLIPBOARD_SOURCE)

        self.source_form.set_model(Q2Model())
        self.source_form.model.set_records(self.source_data)
        self.source_form.add_control(
            "column", q2app.PASTE_CLIPBOARD_SOURCE_COLUMNS, control="line", datalen=100
        )
        self.source_form.grid_double_clicked = self.move_it
        self.source_form.i_am_child = 1

    def load_data(self):
        self.data_data = []
        for cliptext_row in self.cliptext.split("\n")[1:]:
            row_dic = {}
            for ncol, cliptext_column in enumerate(cliptext_row.split("\t")):
                row_dic[self.clipboard_headers[ncol]] = cliptext_column
            if len(self.clipboard_headers) != len(row_dic):
                continue
            self.data_data.append(row_dic)

        self.data_form = self.q2_form.q2_app.Q2Form(q2app.PASTE_CLIPBOARD_CLIPBOARD_DATA)
        for col in self.clipboard_headers:
            self.data_form.add_control(col, col)

        self.data_form.set_model(Q2Model())
        self.data_form.model.set_records(self.data_data)
        self.data_form.i_am_child = 1


class Q2BulkUpdate:
    def __init__(self, q2_form: Q2Form):
        self.q2_form = q2_form

        self.load_target()
        if self.show_main_form().ok_pressed:
            self.bulk_data_enter()

    def bulk_data_enter(self):
        bulk_data_form = self.q2_form.q2_app.Q2Form(q2app.BULK_DATA_ENTRY_TITLE)
        bulk_data_form.model = self.q2_form.model
        bulk_columns = []
        current_record = self.q2_form.get_current_record()
        for x in self.target_data:
            if x["_selected"]:
                control = dict(x)
                control["data"] = current_record.get(control["column"], "")
                bulk_data_form.add_control(**control)
                bulk_columns.append(control["column"])
        if len(bulk_data_form.controls) == 0:
            return

        bulk_data_form.ok_button = True
        bulk_data_form.cancel_button = True
        bulk_data_form.show_form()
        if bulk_data_form.ok_pressed:
            self.bulk_update(bulk_data_form, bulk_columns)

    def bulk_update(self, bulk_data_form, bulk_columns):
        record_list = []
        for x in self.q2_form.get_grid_selected_rows():
            record_list.append(self.q2_form.model.get_record(x))
        waitbar = self.q2_form.show_progressbar(q2app.BULK_DATA_WAIT, len(record_list))
        for x in record_list:
            waitbar.step(1000)
            self.q2_form.set_grid_index(self.q2_form.model.seek_row(x))
            self.q2_form.show_crud_form(EDIT, modal="")
            for bulk_column in bulk_columns:
                self.q2_form.w.__getattr__(bulk_column).when()
                self.q2_form.s.__setattr__(bulk_column, bulk_data_form.s.__getattr__(bulk_column))
                self.q2_form.w.__getattr__(bulk_column).valid()
            self.q2_form.crud_save()
        waitbar.close()

    def show_main_form(self):
        self.main_form = self.q2_form.q2_app.Q2Form(q2app.BULK_DATA_MAIN_TITLE)
        self.main_form.add_control("/v")
        self.main_form.add_control("target_form", widget=self.target_form)
        self.main_form.cancel_button = True
        self.main_form.ok_button = True
        self.main_form.add_ok_cancel_buttons()
        self.main_form.show_form()
        return self.main_form

    def select(self):
        target_row = self.target_form.current_row
        target_row_data = self.target_form.get_current_record()
        target_row_data["_selected"] = "" if target_row_data["_selected"] else "*"
        self.target_form.model.update(target_row_data, target_row)
        self.target_form.set_grid_index(target_row)

    def load_target(self):
        self.target_form = self.q2_form.q2_app.Q2Form(q2app.BULK_TARGET_TITLE)
        self.target_data = []
        for x in self.q2_form.controls:
            if not x["pk"] and not x["noform"] and not x["column"].startswith("/"):
                x["target_column"] = (
                    f'{x.get("label") if x.get("label") else x.get("gridlabel")} '
                    + f'({self.q2_form.model.get_table_name()}.{x.get("column")})'
                )
                x["_target_column"] = x.get("column")
                x["_selected"] = ""
                self.target_data.append(dict(x))
        self.target_form.set_model(Q2Model())
        self.target_form.model.set_records(self.target_data)
        self.target_form.add_control("target_column", q2app.BULK_TARGET_COLUMNS, control="line", datalen=100)
        self.target_form.add_control("_selected", q2app.BULK_TARGET_SELECTED, control="check", datalen=5)
        self.target_form.grid_double_clicked = self.select
        self.target_form.i_am_child = 1
