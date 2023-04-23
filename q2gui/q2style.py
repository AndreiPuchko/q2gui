import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()


import darkdetect


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
            "color_disabled": "#777",
            "background_disabled": "#444",
            # selected text
            "color_selection": "#222",
            "background_selection": "yellow",
            # selected item
            "color_selected_item": "#111",
            "background_selected_item": "#A1A1F6",
            # selected menu item
            "background_menu_selection": "#B0E2FF",
            # for focusable controls
            # "background_control": "rgb(48, 69, 92)",
            "background_control": "#43455C",
            # for contol with focus
            "background_focus": "#0077BB",
            "border_focus": "1px solid yellow",
            # general border
            "border": "1px solid #fff",
            # actice window border
            "border_window": "0px solid #1E90FF",
            "padding": "1px",
            "margin": "1px",
            "border_raduis": "border-radius: 0.3em;",
        }

        self.styles["dark"] = dict(self.default_style)
        self.styles["light"] = dict(self.default_style)

        self.styles["light"].update(
            {
                # base colors
                "color": "#000",
                "background": "palette(base)",
                # disabled color, background doesnt change
                "color_disabled": "#DDD",
                "background_disabled": "#AAA",
                # selected text
                "color_selection": "#222",
                "background_selection": "#B0E2FF",
                # selected item
                "color_selected_item": "#111",
                "background_selected_item": "#A1A1F6",
                # selected menu item
                "background_menu_selection": "#B0E2FF",
                # for focusable controls
                "background_control": "rgb(160, 188, 217)",
                # for contol with focus
                "background_focus": "yellow",
                "border_focus": "2px solid #005599",
                # general border
                "border": "2px solid #666",
            }
        )
        if q2widget:
            self.set_style_sheet(q2widget, self.color_mode)

    def set_color_mode(self, q2widget=None, color_mode=None):
        if q2widget is None:
            return
        if color_mode:
            self.color_mode = color_mode
            self.set_style_sheet(q2widget, self.color_mode)

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
        return darkdetect.theme().lower()

    def get_stylesheet(self, color_mode=None):
        color_mode = self.get_color_mode(color_mode)
        return self._style().format(**self.get_styles(color_mode))

    def get_color_mode(self, color_mode):
        if color_mode is None:
            color_mode = self.color_mode
        return color_mode

    def get_style(self, name, color_mode=None):
        return self.styles.get(self.get_color_mode(color_mode),{}).get(name, "")

    def get_styles(self, mode="dark"):
        return self.styles.get(mode, self.styles["dark"])

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
        self.color_mode = color_mode
        if hasattr(q2widget, "set_style_sheet"):
            q2widget.set_style_sheet(self.get_stylesheet(color_mode))
            q2widget.set_font(self._font_name, self._font_size)
