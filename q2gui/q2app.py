import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()


import q2gui.q2app as q2app
from configparser import ConfigParser

# from q2gui.q2window import Q2Window
from q2gui.q2utils import num

import re
import io
import time


q2_app = None

ASK_REMOVE_RECORD_TEXT = "You are about to remove current record! Are You Sure?"
ASK_REMOVE_RECORDS_TEXT = "You are about to remove records<b>(%s)</b>! Are You Sure?"
REMOVE_RECORD_ERROR_TEXT = "Remove record error"

DATA_FORMAT_STRING = "%d.%m.%Y"

ACTION_VIEW_TEXT = "View"
ACTION_VIEW_ICON = "View"
ACTION_VIEW_HOTKEY = "F12"

ACTION_NEW_TEXT = "New"
ACTION_NEW_ICON = "New"
ACTION_NEW_HOTKEY = "Ins"

ACTION_COPY_TEXT = "Copy"
ACTION_COPY_ICON = "Copy"
ACTION_COPY_HOTKEY = "Ctrl+Ins"

ACTION_EDIT_TEXT = "Edit"
ACTION_EDIT_ICON = "Edit"
ACTION_EDIT_HOTKEY = "Spacebar"

ACTION_REMOVE_TEXT = "Remove"
ACTION_REMOVE_ICON = "Remove"
ACTION_REMOVE_HOTKEY = "Delete"


ACTION_FIRST_ROW_TEXT = "<<"
ACTION_FIRST_ROW_ICON = "First"
ACTION_FIRST_ROW_HOTKEY = "Ctrl+Up"

ACTION_PREVIOUS_ROW_TEXT = "🡸"
ACTION_PREVIOUS_ROW_ICON = "Previous"

ACTION_REFRESH_TEXT = "↺"
ACTION_REFRESH_ICON = "REFRESH"
ACTION_REFRESH_HOTKEY = "F5"

ACTION_NEXT_ROW_TEXT = "🡺"
ACTION_NEXT_ROW_ICON = "Next"

ACTION_LAST_ROW_TEXT = ">>"
ACTION_LAST_ROW_ICON = "Last"
ACTION_LAST_ROW_HOTKEY = "Ctrl+Down"

ACTION_CLOSE_TEXT = "Close"
ACTION_CLOSE_ICON = "Close"

CRUD_BUTTON_EDIT_TEXT = "Edit"
CRUD_BUTTON_EDIT_MESSAGE = "enable editing"

CRUD_BUTTON_OK_TEXT = "OK"
CRUD_BUTTON_OK_MESSAGE = "save data"

CRUD_BUTTON_CANCEL_TEXT = "Cancel"
CRUD_BUTTON_CANCEL_MESSAGE = "Do not save data"

GRID_ACTION_TEXT = "☰"

FINANCIAL_FORMAT = r"{:,.%sf}"
GRID_COLUMN_WIDTH = 18


def load_q2engine(glo, engine="PyQt6"):
    from q2gui.pyqt6.q2app import Q2App as Q2App
    from q2gui.pyqt6.q2form import Q2Form as Q2Form

    glo["Q2App"] = Q2App
    glo["Q2Form"] = Q2Form


class Q2Heap:
    pass


class Q2Actions(list):
    def __init__(self, action=None):
        self.show_main_button = True
        self.show_actions = True
        self.main_button_text = "☰"
        if isinstance(action, list):
            # self.action_list = action[:]
            self.extend(action[:])
        # else:
        #     self.action_list = []

    def run(self, text):
        for action in self:
            if text == action["text"]:
                action["_worker"]()

    def set_visible(self, text, mode=True):
        for action in self:
            if text == action["text"]:
                action["_set_visible"](mode)
            # elif text == action.get("parent_action_text"):
            #     action["_set_visible_parent_action"](mode)

    def set_disabled(self, text="", mode=True):
        for action in self:
            if text == action["text"]:
                action["_set_disabled"](mode)

    def set_enabled(self, text="", mode=True):
        for action in self:
            if text == action["text"]:
                action["_set_enabled"](mode)

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
    ):
        """ "/view", "/crud" """
        for x in range(len(self)):
            # if text in self[x]["text"] and text.strip()[-1] != "-":
            if text == self[x]["text"] and text.strip()[-1] != "-":
                self[x]["worker"] = worker
                self[x]["hotkey"] = hotkey
                return True
        action = {}
        action["text"] = text
        action["worker"] = worker
        action["icon"] = icon
        action["mess"] = mess
        action["hotkey"] = hotkey
        action["tag"] = tag
        action["eof_disabled"] = eof_disabled
        action["child_form"] = child_form
        action["child_where"] = child_where
        self.append(action)
        return True

    # def insertAction(
    #     self, before, text, worker=None, icon="", mess="", key="", **kvargs
    # ):
    #     for x in self.addAction.__code__.co_varnames:
    #         if x not in ["kvargs", "self"]:
    #             kvargs[x] = locals()[x]
    #     self.action_list.insert(before, kvargs)

    # def removeAction(self, text):
    #     actionIndex = safe_index([x["text"] for x in self.action_list], text)
    #     if actionIndex is not None:
    #         self.action_list.pop(actionIndex)
    pass


class Q2Controls(list):
    class _C:
        def __init__(self, controls):
            self.controls = controls

        def __getattr__(self, name):
            for line in self.controls:
                if line.get("column") == name or line.get("tag") == name:
                    return line
            return [line["column"] for line in self.controls]

    def __init__(self):
        self.c = self._C(self)

    # def __getitem__(self, list_index):
    #     if isinstance(list_index, str):  # not index but name - return index for name
    #         for x in range(len(self)):
    #             if list_index == self[x].get("column"):
    #                 return x
    #         return None
    #     else:
    #         return super().__getitem__(list_index)

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
        valid=None,
        dblclick=None,
        readonly=None,
        disabled=None,
        check=None,
        noform=None,
        nogrid=None,
        widget=None,
        stretch=0,
        mess="",
        tag="",
        eat_enter=None,
        hotkey="",
    ):
        meta = locals().copy()
        del meta["self"]
        meta["_control"] = None
        # meta = self.validate(meta)
        self.append(meta)
        return True

    @staticmethod
    def validate(meta):
        if meta.get("datatype", "").lower() == "date":
            meta["control"] = "date"
            meta["datalen"] = 16

        if meta.get("column").startswith("/"):
            meta["control"] = ""
        elif not meta.get("control") and not meta.get("widget") and meta.get("column"):
            meta["control"] = "line"
            # meta["control"] = ""

        if num(meta.get("datalen", 0)) == 0 and meta.get("control", "") in ("line", "radio"):
            if meta.get("datatype", "").lower() == "int":
                meta["datalen"] = 9
            elif meta.get("datatype", "").lower() == "bigint":
                meta["datalen"] = 17
            else:
                meta["datalen"] = 100

        # if re.match(".*int.*|.*dec.*|.*num.*", meta.get("datatype", ""), re.RegexFlag.IGNORECASE):
        #     meta["num"] = True
        #     if meta.get("pic", "") == "":
        #         meta["pic"] = "9" * int(num(meta["datalen"]) - num(meta["datadec"])) + (
        #             "" if num(meta["datadec"]) == 0 else "." + "9" * int(num(meta["datadec"]))
        #         )
        #     if num(meta.get("alignment", 0)) == 0:
        #         meta["alignment"] = 9

        if (
            re.match(".*text.*", meta.get("datatype", ""), re.RegexFlag.IGNORECASE)
            and "code" not in meta["control"]
        ):
            meta["datalen"] = 0
            meta["control"] = "text"

        if "***" == "".join(["*" if meta.get(x) else "" for x in ("to_table", "to_column", "related")]):
            meta["relation"] = True

        if re.match(".*int.*|.*dec.*|.*num.*", meta.get("datatype", ""), re.RegexFlag.IGNORECASE):
            meta["num"] = True
            if meta.get("pic", "") == "":
                meta["pic"] = "9" * int(num(meta["datalen"]) - num(meta["datadec"])) + (
                    "" if num(meta["datadec"]) == 0 else "." + "9" * int(num(meta["datadec"]))
                )
            if meta.get("alignment", -1) == -1:
                meta["alignment"] = 9

        if not meta["column"].startswith("/"):
            if "char" in meta.get("datatype", "") and num(meta.get("datalen")) == 0:
                if meta.get("control") in ("check"):
                    meta["datalen"] = 1
                elif meta.get("control") in ("line"):
                    meta["datalen"] = 100
        return meta


class Q2Settings:
    def __init__(self, filename=""):
        self.filename = filename if filename else "q2gui.ini"
        self.config = ConfigParser()
        self.read()

    def read(self):
        if self.filename in ("none", "memory"):
            self.filename = io.StringIO("")
        if isinstance(self.filename, io.StringIO):
            self.config.read_file(self.filename)
        else:
            self.config.read(self.filename)

    def write(self):
        if self.filename == "none":
            return
        if isinstance(self.filename, io.StringIO):
            self.config.write(self.filename)
        else:
            with open(self.filename, "w") as configfile:
                self.config.write(configfile)

    def prepSection(self, section):
        return re.sub(r"\[.*\]", "", section).strip().split("\n")[0].replace("\n", "").strip()

    def get(self, section="", key="", defaultValue=""):
        section = self.prepSection(section)
        try:
            return self.config.get(section, key)
        except Exception:
            return defaultValue

    def set(self, section="", key="", value=""):
        if section == "":
            return
        section = self.prepSection(section)
        value = "%(value)s" % locals()
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)


class Q2App:
    def __init__(self, title=""):
        q2app.q2_app = self
        self.window_title = title
        self.heap = Q2Heap()
        self.db = None
        self.style_file = ""
        self.settings_file = ""
        self.settings_file = self.get_argv("ini")
        self.icon = None

        self.menu_list = []
        self._main_menu = {}

        self.settings = Q2Settings(self.settings_file)
        self.style_file = self.get_argv("style")
        if self.style_file == "":
            self.style_file = "q2gui.qss"
        self.set_style_sheet()
        self.menu_list = []
        self.set_icon("assets/q2gui.ico")
        self.on_init()

    def set_style_sheet(self):
        pass

    def get_argv(self, argtext: str):
        for x in sys.argv:
            if x.startswith(f"/{argtext}:") or x.startswith(f"-{argtext}:"):
                file_name = x[(len(argtext) + 2) :]  # noqa: E203
                return file_name
        return ""

    def add_menu(self, text="", worker=None, before=None, toolbar=None):
        if text.endswith("|"):
            text = text[:-1]
        if text.startswith("|"):
            text = text[1:]
        self.menu_list.append({"TEXT": text, "WORKER": worker, "BEFORE": before, "TOOLBAR": toolbar})

    def clear_menu(self):
        self.menu_list = []

    def build_menu(self):
        self.menu_list = self.reorder_menu(self.menu_list)

    def reorder_menu(self, menu):
        tmp_list = [x["TEXT"] for x in menu]
        tmp_dict = {x["TEXT"]: x for x in menu}
        re_ordered_list = []
        for x in tmp_list:
            # add node element for menu
            menu_node = "|".join(x.split("|")[:-1])
            if menu_node not in re_ordered_list:
                re_ordered_list.append(menu_node)
                tmp_dict[menu_node] = {
                    "TEXT": menu_node,
                    "WORKER": None,
                    "BEFORE": None,
                    "TOOLBAR": None,
                }
            if tmp_dict[x].get("BEFORE") in re_ordered_list:
                re_ordered_list.insert(re_ordered_list.index(tmp_dict[x].get("BEFORE")), x)
            else:
                re_ordered_list.append(x)
        return [tmp_dict[x] for x in re_ordered_list]

    def close(self):
        self.save_geometry(self.settings)

    def save_geometry(self, settings):
        pass

    def restore_geometry(self, settings):
        pass

    def show_statusbar_mess(self, text=""):
        pass

    def show_form(self, form=None, modal="modal"):
        pass

    def focus_changed(self, from_widget, to_widget):
        if from_widget.__class__.__name__ in (
            "q2line",
            "q2relation",
            "q2ScriptEdit",
            "q2ScriptSqlEdit",
        ):
            if from_widget.valid() is False:
                from_widget.set_focus()

        if to_widget.__class__.__name__ in (
            "q2line",
            "q2relation",
            "q2ScriptEdit",
            "q2ScriptSqlEdit",
        ):
            if to_widget:
                to_widget.when()

    def lock(self):
        pass

    def unlock(self):
        pass

    def set_icon(self):
        pass

    def process_events(self):
        pass

    def on_init(self):
        pass

    def on_start(self):
        pass

    def on_new_tab(self):
        pass

    def show_menubar(self, mode=True):
        pass

    def hide_menubar(self, mode=True):
        if mode:
            self.show_menubar(False)
        else:
            self.show_menubar(True)

    def is_menubar_visible(self):
        pass

    def show_toolbar(self, mode=True):
        pass

    def hide_toolbar(self, mode=True):
        if mode:
            self.show_toolbar(False)
        else:
            self.show_toolbar(True)

    def is_toolbar_visible(self):
        pass

    def disable_toolbar(self, mode=True):
        pass

    def disable_menubar(self, mode=True):
        pass

    def disable_tabbar(self, mode=True):
        pass

    def show_tabbar(self, mode=True):
        pass

    def get_tabbar_text(self):
        pass

    def set_tabbar_text(self, text=""):
        pass

    def hide_tabbar(self, mode=True):
        if mode:
            self.show_tabbar(False)
        else:
            self.show_tabbar(True)

    def is_tabbar_visible(self):
        pass

    def show_statusbar(self, mode=True):
        pass

    def keyboard_modifiers(self):
        pass

    def hide_statusbar(self, mode=True):
        if mode:
            self.show_statusbar(False)
        else:
            self.show_statusbar(True)

    def is_statusbar_visible(self):
        pass

    def get_char_width(self, char="W"):
        return 9

    def get_char_height(self):
        return 9

    def sleep(self, seconds=0):
        time.sleep(seconds)

    @staticmethod
    def get_open_file_dialoq(header="Open file", path="", filter=""):
        pass

    @staticmethod
    def get_save_file_dialoq(header="Save file", path="", filter=""):
        pass

    def add_new_tab(self):
        pass

    def run(self):
        self.build_menu()
