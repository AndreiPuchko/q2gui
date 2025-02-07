"""
shows how to create the main menu bar
Note. The main menu is also accessible by left-clicking 
anywhere (except any form) in the application.
"""


from q2gui.q2app import Q2App
from q2gui.q2app import load_q2engine
from q2gui.q2form import Q2Form
from q2gui.q2dialogs import q2mess


load_q2engine(globals(), "PyQt6")


class DemoApp(Q2App):
    def on_init(self):
        self.add_menu("File|Form", worker=self.run_form, toolbar="*")
        self.add_menu("File|-", None)
        self.add_menu("File|Toogle toolbar", self.show_hide_toolbar, toolbar="*")
        self.add_menu("File|Toogle menubar", self.show_hide_menubar, toolbar="*")
        self.add_menu("File|Toogle tabbar", self.show_hide_tabbar, toolbar="*")
        self.add_menu("File|Toogle statusbar", self.show_hide_statusbar, toolbar="*")
        self.add_menu("File|-", None)
        self.add_menu("File|Dark Mode", lambda: self.set_color_mode("dark"), toolbar=1)
        self.add_menu("File|Light Mode", lambda: self.set_color_mode("light"), toolbar=1)
        self.add_menu("File|Clean Mode", lambda: self.set_color_mode("clean"), toolbar=1)
        self.add_menu("File|-", None)
        self.add_menu("Documents|Personal", lambda: q2mess("Personal"))
        self.add_menu("Documents|Business|Company 1", lambda: q2mess("B.|Company 1"))
        self.add_menu("Documents|Business|Company 2", lambda: q2mess("B.|Company 2"))
        self.add_menu("Help|About", lambda: q2mess("About q2gui"))
        self.add_menu("File|Quit", self.close, toolbar="*")

    def show_hide_menubar(self):
        self.show_menubar(not self.is_menubar_visible())

    def show_hide_toolbar(self):
        self.show_toolbar(not self.is_toolbar_visible())

    def show_hide_tabbar(self):
        self.show_tabbar(not self.is_tabbar_visible())

    def show_hide_statusbar(self):
        self.show_statusbar(not self.is_statusbar_visible())

    def run_form(self):
        form = Q2Form("First form")
        form.add_control(label="Just label")
        form.run()


def demo():
    app = DemoApp(f"q2gui Sample applcation - {__file__}")
    app.run()


if __name__ == "__main__":
    demo()
