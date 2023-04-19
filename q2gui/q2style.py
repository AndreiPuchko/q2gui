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
            "color": "#fff",
            "background": "#282828",
            "color_disabled": "#777",
            "color_selection": "#000",
            "background_selection": "#fff",
            "color_selected_item": "#111",

            "background_selected_item": "#CCC",
            "background_menu_selection": "#B0E2FF",
            "background_control": "#555",
            "background_focus": "#005599",
            "border": "1px solid #666",
            "border_focus": "2px solid yellow",
            "border_window": "1px solid #1E90FF",
            "padding": "0.2em",
        }

    def get_system_mode(self):
        return darkdetect.theme().lower()

    def get_stylesheet(self, mode=None):
        if mode is None:
            mode = self.get_system_mode()
        return self._style(mode).format(**self.get_style(mode))

    def get_style(self, mode="dark"):
        return self.styles.get(mode, self.styles["dark"])

    def _style(self, mode=None):
        if mode == "dark":
            return self._dark_style()
        else:
            return self._light_style()

    def _dark_style(self):
        return ""

    def _light_style(self):
        return ""
