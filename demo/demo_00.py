if __name__ == "__main__":
    import sys

    sys.path.insert(0, ".")

import importlib
from q2gui.q2app import Q2App
from q2gui.q2form import Q2Form
from q2gui.q2app import load_q2engine

load_q2engine(globals(), "PyQt6")


class DemoApp(Q2App):
    def on_init(self):
        self.hide_tabbar()
        self.hide_statusbar()
        self.hide_menubar()
        self.define_launch_data()

    def on_new_tab(self):
        self.center_position()
        self.first_form()
        self.close()

    def first_form(self):
        self.form = Q2Form("Launch demo")
        self.form.maximized = True
        self.form.hide_title = True
        self.form.set_style_sheet(
            """QWidget{font:25px;}
                q2button {font:30px; padding: 10 200px}
                q2list::item {margin: 10px;}
            """
        )
        self.form.add_control("/")
        if self.form.add_control("/v"):
            if self.form.add_control("/hs"):
                self.form.add_control(
                    "app_list",
                    "",
                    control="list",
                    pic=";".join(self.launch_data.keys()),
                    valid=self.set_description,
                    dblclick=self.launcher,
                    stretch=1,
                )
                self.form.add_control(
                    "source",
                    "",
                    control="code",
                    readonly=1,
                    stretch=2,
                )
                self.form.add_control("/")
        self.form.add_control("/h")
        self.form.add_control("/s")
        self.form.add_control("run", "Run", control="button", valid=self.launcher)
        self.form.add_control("/s")
        self.form.add_control("quit", "Quit", control="button", valid=self.form.close)
        self.form.add_control("/s")
        self.form.after_form_show = self.after_form_show
        self.form.run()
        self.close()

    def launcher(self):
        py = self.launch_data[self.form.s.app_list]
        mo = importlib.import_module(f"demo.{py}")
        mo.demo()

    def after_form_show(self):
        self.form.w.run.set_style_sheet("{background-color:lightblue}")
        self.form.w.quit.set_style_sheet("{background-color:pink}")
        self.form.w.app_list.set_text(list(self.launch_data.keys())[0])
        self.form.w.app_list.itemDoubleClicked.connect(self.launcher)
        self.set_description()

    def define_launch_data(self):
        self.launch_data = {
            "Widgets": "demo_01",
            "Main window management": "demo_02",
            "Grid (CSV)": "demo_03",
            "Progressbar and Grid": "demo_04",
            "Nonmodal form": "demo_05",
            "Code editor": "demo_06",
            "Database App 1": "demo_07",
            "Database App 2": "demo_08",
            "This launcher": "demo_00",
        }

    def set_description(self):
        if self.form.s.app_list is None:
            return
        # self.form.s.description = self.launch_data[self.form.s.app_list]["text"]
        py = self.launch_data[self.form.s.app_list]
        self.form.s.source = open(f"demo/{py}.py").read()


def demo():
    app = DemoApp("q2gui Demo Launcher")
    app.run()


if __name__ == "__main__":
    demo()
