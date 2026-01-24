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


import re
from q2gui.q2utils import num


RE_QSS_CM = re.compile(r"\d*\.+\d*\.*cm")


def re_qss_cm_replace(mo):
    return str(int(mo.group(0).replace("cm", "").replace(".", "")) / 2)


class Q2Widget:
    def __init__(self, meta={}):
        self.meta = meta
        self.form = None
        self.label = None
        self.check = None
        self.frame = None
        self.style_sheet = ""
        if self.meta.get("readonly"):
            self.set_readonly(True)
        if self.meta.get("disabled"):
            self.set_disabled(True)
        if self.meta.get("mess"):
            self.set_tooltip(self.meta.get("mess"))
        if hasattr(self, "set_text") and self.meta.get("data"):
            self.set_text(self.meta.get("data"))

        max_width = max(num(self.meta.get("datalen", 0)), len(self.meta.get("pic", "")))
        if max_width:
            self.set_maximum_width(max_width)
        if max_width:
            self.set_maximum_len(max_width)
        if self.meta.get("style"):
            self.set_style_sheet(self.meta["style"])

        self.set_alignment(self.meta.get("alignment", 7))

    def set_readonly(self, arg):
        pass

    def set_disabled(self, arg=True):
        self.set_enabled(not arg)

    def set_enabled(self, arg=True):
        pass

    def set_visible(self, arg=True):
        pass

    def is_visible(self):
        pass

    def is_checked(self):
        if self.check:
            return self.check.is_checked()
        elif self.frame:
            return self.frame.is_checked()
        else:
            return True

    def can_get_focus(self):
        return True

    def get_check(self):
        if self.check:
            return self.check
        elif self.frame:
            return self.frame.get_check()
        else:
            return None

    def set_checked(self, mode=True):
        if self.check:
            return self.check.set_checked(mode)
        elif self.frame:
            return self.frame.set_checked(mode)
        else:
            return True

    def set_tooltip(self, mess):
        pass

    def set_focus(self):
        pass

    def set_font(self, font_name, font_size):
        pass

    def has_focus(self):
        pass

    def is_enabled(self):
        pass

    def set_text(self, text):
        pass

    def get_text(self):
        pass

    def valid(self):
        if not self.meta.get("form"):
            return
        # if not self.meta.get("form").form_is_active is True:
        #     return
        if self.meta.get("form_window") and not self.meta.get("form_window").form_is_active is True:
            return
        valid = self.meta.get("valid")
        if valid is not None:
            return valid()
        else:
            return True

    def when(self):
        when = self.meta.get("when", lambda: True)
        if when:
            return self.meta.get("when", lambda: True)()
        else:
            return True

    def show_(self):
        if self.meta.get("show"):
            self.set_text(self.meta["show"](mode="form"))

    def set_maximum_len(self, length):
        pass

    def set_maximum_width(self, width, char="O"):
        pass

    def set_minimum_width(self, width, char="O"):
        pass

    def set_fixed_width(self, width, char="O"):
        pass

    def set_fixed_height(self, width, char="O"):
        pass

    def set_alignment(self, alignment):
        pass

    def set_style_sheet(self, css):
        if isinstance(css, dict):
            css = ";".join(([f"{y}:{css[y]}" for y in css]))
        if css.strip().startswith("{"):
            css = type(self).__name__ + css
        css = RE_QSS_CM.sub(re_qss_cm_replace, css)
        self.style_sheet = css

    def add_style_sheet(self, css: str):
        pass

    def get_style_sheet(self):
        pass

    def fix_default_height(self):
        self.set_maximum_height(self.get_default_height())

    def get_default_height(self):
        pass

    def set_maximum_height(self, height, char="O"):
        pass

    def fix_default_width(self):
        self.set_maximum_width(self.get_default_width(), "")

    def get_default_width(self):
        pass

    def set_size_policy(self, horizontal, vertical):
        pass

    def set_content_margins(self, top=0, right=None, bottom=None, left=None):
        pass

    def get_next_focus_widget(self, pos=1):
        pass

    def get_next_widget(self, pos=1):
        pass

    def add_widget_above(self, widget, pos=0):
        pass

    def add_widget_below(self, widget, pos=0):
        pass

    def remove(self):
        pass

    def get_layout_position(self):
        pass

    def get_layout_count(self):
        pass

    def get_layout_widget(self):
        pass

    def get_layout_widgets(self):
        pass

    def move_up(self):
        pass

    def move_down(self):
        pass

    def action_set_visible(self, text, mode):
        pass

    def action_set_enabled(self, text, mode):
        pass

    @staticmethod
    def make_meta(
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
        index=None,
        hotkey="",
        style="",
    ):
        meta = locals().copy()
        return meta
