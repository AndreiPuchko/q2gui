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

if __name__ == "__main__":
    import sys

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()

from q2gui.q2utils import num


class Q2Frame:
    def __init__(self, mode="v"):
        super().__init__()
        self.frame_mode = mode
        self.set_mode(self.frame_mode)
        self._widgets_list = []

    def set_mode(self, mode="v"):
        self.frame_mode = mode

    def set_title(self, title):
        pass

    def hide_border(self):
        self.set_title("")

    def add_widget(self, widget=None, label=None):
        if widget is None:
            return
        if self.frame_mode in ["v", "h"]:
            self.insert_widget(len(self._widgets_list), widget)

    def insert_widget(self, pos=None, widget=None):
        pass

    def add_row(self, label=None, widget=None):
        pass

    def swap_widgets(self, widget1, widget2):
        pass

    def move_widget(self, widget, direction="up"):
        pass


class Q2Window(Q2Frame):
    def __init__(self, title=""):
        super().__init__()
        self.window_title = ""
        self.settings_title = ""
        # print("init", self)
        self.set_title(title)

    def set_title(self, title):
        self.window_title = title

    def set_settings_title(self, title):
        self.settings_title = title

    def set_position(self, left, top):
        pass

    def set_size(self, width, height):
        pass

    def get_position(self):
        pass

    def get_size(self):
        pass

    def move_window(self, right=0, down=0):
        pos = self.get_position()
        right += pos[0]
        down += pos[1]
        self.set_position(right, down)

    def is_maximized(self):
        pass

    def show_maximized(self):
        return 0

    def set_enabled(self, mode):
        pass

    def set_disabled(self, mode):
        pass

    def restore_geometry(self, settings):
        title = self.settings_title if self.settings_title else self.window_title
        width = num(settings.get(title, "width", "1000"))
        height = num(settings.get(title, "height", "800"))
        self.set_size(width, height)

        left = num(settings.get(title, "left", "-9999"))
        top = num(settings.get(title, "top", "-9999"))
        self.set_position(left, top)

        if num(settings.get(title, "is_max", "0")):
            self.show_maximized()

    def save_geometry(self, settings):
        if hasattr(self, "q2_form)") and self.q2_form.do_not_save_geometry:
            return
        title = self.settings_title if self.settings_title else self.window_title
        settings.set(title, "is_max", f"{self.is_maximized()}")
        if not self.is_maximized():
            pos = self.get_position()
            if pos is not None:
                settings.set(title, "left", pos[0])
                settings.set(title, "top", pos[1])
            size = self.get_size()
            settings.set(title, "width", size[0])
            settings.set(title, "height", size[1])
        else:
            settings.set(title, "is_max", 1)
        settings.write()
