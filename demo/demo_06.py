if __name__ == "__main__":
    import sys

    sys.path.insert(0, ".")

from q2gui.pyqt6.q2app import Q2App
from q2gui.pyqt6.q2form import Q2Form as Q2Form
from q2gui.pyqt6.q2form import q2Mess


class DemoApp(Q2App):
    def on_start(self):
        self.first_form()

    def on_init(self):
        self.add_menu("File|About", lambda: q2Mess("First application!"), toolbar=1)
        self.add_menu("File|First Form", self.first_form, toolbar=1)
        self.add_menu("File|-")
        self.add_menu("File|Exit", self.close, toolbar=1)
        return super().on_init()

    def first_form(self):
        form = Q2Form("FirstForm")
        form.init_size = [95, 95]
        form.add_control("", "First Label")
        form.add_control("field", "First Field")
        form.add_control("/")
        form.add_control("code", "Text Field", control="codepython")
        form.add_control("/h")

        def open_file():
            file_name = Q2App.get_open_file_dialoq(filter="Python file(*.py);; Toml file(*.toml *.ini)")[0]
            if file_name:
                form.s.code = open(file_name).read()

        form.add_control("open", "Open file", control="button", valid=open_file)

        form.add_control("/s")
        form.add_control("", "Close Form", control="button", valid=form.close)

        def after_form_show():
            form.s.code = open("q2gui/q2app.py").read()

        form.after_form_show = after_form_show
        form.run()


def demo():
    app = DemoApp("q2gui - the first app")
    app.run()


if __name__ == "__main__":
    demo()
