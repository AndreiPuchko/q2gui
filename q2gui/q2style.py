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


import darkdetect
import logging
from q2gui.q2app import q2app

_logger = logging.getLogger(__name__)


class Q2Style:
    def __init__(self, q2widget=None, color_mode=None):
        self.styles = {}
        self._font_size = 12
        self._font_name = "Arial"
        self.color_mode = color_mode
        if color_mode is None:
            self.color_mode = self.get_system_color_mode()

        self.default_style = {
            "font_size": f"{self._font_size}",
            "font_name": f"{self._font_name}",
            # base colors
            "color": "#fff",
            "background": "#282828",
            # disabled color
            "color_disabled": "#CCC",
            "background_disabled": "#444",
            # selected text
            "color_selection": "#222",
            "background_selection": "#B0E2FF",
            # selected item
            "color_selected_item": "#111",
            "background_selected_item": "#6b6bcf",
            # selected menu item
            "background_menu_selection": "#B0E2FF",
            # for focusable controls
            "background_control": "#53556C",
            # for contol with focus
            "background_focus": "#215370",
            "color_focus": "#FFF",
            "border_focus": "1px solid yellow",
            # general border
            "border": "1px solid palette(Mid)",
            # actice window border
            "border_radius": "border-radius: 0.25ex;",
            "padding": "0px",
            "toolbutton_background": "palette(Mid)",
            "margin": "0px",
        }

        self.styles["dark"] = dict(self.default_style)
        self.styles["light"] = dict(self.default_style)

        self.styles["light"].update(
            {
                # base colors
                "color": "#000",
                "background": "#EEE",
                # disabled color, background doesnt change
                "color_disabled": "#333",
                "background_disabled": "#cccccc",
                # selected text
                "color_selection": "#222",
                "background_selection": "#f3f5a4",
                # selected item
                "color_selected_item": "#111",
                "background_selected_item": "#cdcdf7",
                # selected menu item
                "background_menu_selection": "#B0E2FF",
                # for focusable controls
                "background_control": "#dae7f0",
                # for contol with focus
                "background_focus": "#b1d6f0",
                "color_focus": "#000",
                "border_focus": "1px solid blue",
                # general border
                "border": "1px solid palette(Mid)",
                "toolbutton_background": "palette(Button)",
            }
        )
        if q2widget:
            self.set_style_sheet(q2widget, self.color_mode)

    def set_color_mode(self, q2widget=None, color_mode=None):
        if q2widget is None:
            return
        if color_mode is [None, "", "None", ""]:
            color_mode = self.get_system_color_mode()
        self.color_mode = color_mode
        self.set_style_sheet(q2widget, color_mode)

    @property
    def font_size(self):
        return self._font_size

    @font_size.setter
    def font_size(self, size):
        self._font_size = size
        for style in self.styles:
            self.styles[style]["font_size"] = size

    @property
    def font_name(self):
        return self._font_name

    @font_name.setter
    def font_name(self, name):
        self._font_name = name
        for style in self.styles:
            self.styles[style]["font_name"] = name

    def get_system_color_mode(self):
        mode = darkdetect.theme()
        mode = mode.lower() if mode else "light"
        return mode

    def get_stylesheet(self, color_mode=None):
        if color_mode == "clean":
            return ""
        else:
            color_mode = self.get_color_mode(color_mode)
            return self._style().format(**self.get_styles(color_mode))

    def get_color_mode(self, color_mode=None):
        if color_mode in [None, "", "None"]:
            color_mode = self.color_mode
        if color_mode in [None, "", "None"]:
            color_mode = self.get_system_color_mode()
        return color_mode

    def get_style(self, name, color_mode=None):
        # if color_mode in [None, "", "None"]:
        #     color_mode = self.color_mode
        # if color_mode in [None, "", "None"]:
        #     color_mode = self.get_system_color_mode()
        color_mode = self.get_color_mode()
        return self.styles.get(color_mode, {}).get(name, "")

    def get_styles(self, color_mode=None):
        # if color_mode in [None, "", "None"]:
        #     color_mode = self.color_mode
        # if color_mode in [None, "", "None"]:
        #     color_mode = self.get_system_color_mode()
        color_mode = self.get_color_mode()
        return self.styles.get(color_mode, self.styles["dark"])

    def _style(self):
        if sys.platform == "darwin":
            return self._mac_style()
        elif sys.platform == "win32":
            return self._windows_style()
        elif sys.platform == "linux":
            return self._linux_style()

    def _windows_style(self):
        return ""

    def _mac_style(self):
        return ""

    def _linux_style(self):
        pass

    def set_style_sheet(self, q2widget=None, color_mode=None):
        if hasattr(q2widget, "set_style_sheet"):
            q2widget.set_style_sheet(
                "* {font-family:'%s';font-size: %spx;}" % (self._font_name, self._font_size)
                + self.get_stylesheet(color_mode)
            )
