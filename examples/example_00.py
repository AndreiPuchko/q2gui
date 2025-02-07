import os
import types
from q2gui.q2app import Q2App
from q2gui.q2form import Q2Form
from q2gui.q2app import load_q2engine

load_q2engine(globals(), "PyQt6")

files = {
    "form_hello_world.py": "Hello World ",
    "form_buttons.py": "Buttons example",
    "form_layouts.py": "Layouts example",
    "form_layouts_with_splitter.py": "Splitters Layouts example",
    "form_layouts_with_scroll.py": "Scroll Layouts example",
    "form_tabs.py": "Tabs example",
    "form_all_controls.py": "All controls example",
    "mainwindow_menu.py": "Mainwindow+Mainmenu example",
}


class DemoApp(Q2App):
    def __init__(self, title=""):
        super().__init__(title)
        self.hide_tabbar()
        self.hide_toolbar()
        self.hide_statusbar()
        self.hide_menubar()
        self.define_launcher_data()
        self.folder = os.path.dirname(__file__)

    def on_new_tab(self):
        self.center_position()
        self.laucher_form()
        self.close()

    def laucher_form(self):
        self.form = Q2Form("Launch demo")
        self.form.maximized = True
        self.form.hide_title = True
        self.form.style_sheet
        self.form.set_style_sheet(
            """
                q2button {font:30px; padding: 10 100px} 
                q2button:hover {background-color:darksalmon}
            """
        )
        self.form.add_control("/")
        if self.form.add_control("/v"):
            if self.form.add_control("/h"):
                self.form.add_control(
                    "app_list",
                    control="list",
                    pic=";".join(self.launcher_data.keys()),
                    valid=self.set_content,
                    dblclick=self.launch,
                    stretch=1,
                )
                if self.form.add_control("/v"):
                    self.form.add_control(
                        "filename",
                        control="line",
                        readonly=1,
                    )
                    self.form.add_control(
                        "source",
                        control="code",
                    )
                    self.form.add_control("/")
                self.form.add_control("/")
        self.form.add_control("/h")
        self.form.add_control("/s")
        self.form.add_control("run", "Run", control="button", valid=self.launch)
        self.form.add_control("/s")
        self.form.add_control("quit", "Quit", control="button", valid=self.close)
        self.form.add_control("/s")
        self.form.after_form_show = self.after_form_show
        self.form.after_form_closed = self.close
        self.form.run()

    def launch(self):
        code = self.form.s.source.encode("UTF-8")
        dynamic_module = types.ModuleType("dynamic_module")
        dynamic_module.__dict__["__file__"] = os.path.abspath(self.launcher_data[self.form.s.app_list])
        exec(code, dynamic_module.__dict__)
        dynamic_module.demo()

    def after_form_show(self):
        # self.form.w.app_list.set_minimum_width(10)
        self.set_content()

    def define_launcher_data(self):
        self.launcher_data = {text: file for file, text in files.items()}

    def set_content(self):
        if self.form.s.app_list is None:
            return
        py = self.launcher_data[self.form.s.app_list]
        self.form.s.source = open(f"{self.folder}/{py}").read()
        self.form.s.filename = f"{self.folder}/{py}"


def demo():
    app = DemoApp("q2gui Demo Launcher")
    app.run()


if __name__ == "__main__":
    demo()
