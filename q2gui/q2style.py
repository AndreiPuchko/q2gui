import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()


import darkdetect


class Q2Style:
    def __init__(self):
        self.styles = {}
        self.font_size = 12
        self.font_name = "Arial"

        self.styles["dark"] = {
            # base colors
            "color": "#fff",
            "background": "#282828",
            # disabled color, background doesnt change
            "color_disabled": "#777",
            # selected text
            "color_selection": "#000",
            "background_selection": "#fff",
            # selected item
            "color_selected_item": "#111",
            "background_selected_item": "#A1A1F6",
            # selected menu item
            "background_menu_selection": "#B0E2FF",
            # for focusable controls
            "background_control": "#555",
            # for contol with focus
            "background_focus": "#005599",
            "border_focus": "2px solid yellow",
            # general border
            "border": "1px solid #fff",
            # actice window border
            "border_window": "1px solid #1E90FF",
            "padding": "0.2em",
            "margin": "0.2em",
        }

        self.styles["dark1"] = {
            # base colors
            "color": "#000",
            "background": "palette(base)",
            # disabled color, background doesnt change
            "color_disabled": "#DDD",
            # selected text
            "color_selection": "#FFF",
            "background_selection": "#B0E2FF",
            # selected item
            "color_selected_item": "#111",
            "background_selected_item": "#A1A1F6",
            # selected menu item
            "background_menu_selection": "#B0E2FF",
            # for focusable controls
            "background_control": "rgb(173, 227, 245)",
            # for contol with focus
            "background_focus": "yellow",
            "border_focus": "2px solid #005599",
            # general border
            "border": "2px solid #666",
            # actice window border
            "border_window": "1px solid #1E90FF",
            "padding": "0.1em",
            "margin": "0.1em",
        }

    def get_system_mode(self):
        return darkdetect.theme().lower()

    def get_stylesheet(self, mode=None):
        if mode is None:
            mode = self.get_system_mode()
        return self._style().format(**self.get_style(mode))

    def get_style(self, mode="dark"):
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
