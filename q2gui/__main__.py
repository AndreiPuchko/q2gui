print("""from q2gui.pyqt6.q2app import Q2App
from q2gui.pyqt6.q2form import Q2Form as Q2Form
from q2gui.q2dialogs import q2Mess


class firstApp(Q2App):
    def on_init(self):
        self.add_menu(
            "File|About", lambda: q2Mess("First application!"), toolbar=1
        )
        self.add_menu("File|First Form", self.first_form, toolbar=1)
        self.add_menu("File|-")
        self.add_menu("File|Exit", self.close, toolbar=1)
        return super().on_init()

    def first_form(self):
        form = Q2Form("FirstForm")
        form.add_control("", "First Label")
        form.add_control("field", "First Field")
        form.add_control("", "Close Form", control="button", valid=form.close)
        form.show_mdi_modal_form()


if __name__ == "__main__":
    firstApp("q2gui - the first app").run()

""")
