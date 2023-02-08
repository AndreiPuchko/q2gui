"""Shows the possibilities of combining several forms into one
"""
if __name__ == "__main__":
    import sys

    sys.path.insert(0, ".")


from q2gui.q2model import Q2Model
from q2gui.q2dialogs import q2Mess
from q2gui.q2utils import num

from q2gui.q2app import load_q2engine
from q2gui.q2app import Q2App
from q2gui.q2form import Q2Form

load_q2engine(globals(), "PyQt6")


class DemoApp(Q2App):
    def on_start(self):
        # self.show_complex_form()
        self.show_form1()
        # self.show_grid_form()

    def on_init(self):
        self.add_menu("File|First", self.show_form1, toolbar="*")
        self.add_menu("File|Second", self.show_form2, toolbar="*")
        self.add_menu("File|Grid", self.show_grid_form, toolbar="*")
        self.add_menu("File|Complex", self.show_complex_form, toolbar="*")
        self.add_menu("File|-")
        self.add_menu("File|Options|Toogle toolbar", self.show_hide_toolbar)
        self.add_menu("File|Options|Toogle menubar", self.show_hide_menubar)
        self.add_menu("File|Options|Toogle tabbar", self.show_hide_tabbar)
        self.add_menu("File|Options|Toogle statusbar", self.show_hide_statusbar)
        self.add_menu("File|-")
        self.add_menu("Documents|Personal")
        self.add_menu("Documents|Business")
        self.add_menu("Help|About", lambda: q2Mess("About q2gui"), toolbar="*")
        self.add_menu("File|Quit", self.close, toolbar="*")

    def describe_form1(self):
        form = Q2Form("First form")
        # form.add_control("/")
        form.add_control(
            "some_image",
            "Image",
            control="image",
            data="""89504E470D0A1A0A0000000D4948445200000018000000180806000000E
                    0773DF80000000467414D410000B18F0BFC6105000000206348524D0000
                    7A26000080840000FA00000080E8000075300000EA6000003A980000177
                    09CBA513C00000006624B4744000000000000F943BB7F00000009704859
                    73000000600000006000F06B42CF000000784944415448C763601805040
                    023116AFE53620613AD7DC042816F09F98C3E3E18B560705950CE004919
                    E89810C0A6A71E97625C96FC27D260BC8663B3A483081F34906238A9969
                    06538B196506438214BA8623836C31AB0F0A902B0A52E8A5D8ECF12A20D
                    6726C182A30C9022FB2003034323B55D3F82010046E641BF6CBB302E000
                    0002574455874646174653A63726561746500323032322D30372D313754
                    30383A34313A30382B30303A3030245A92B900000025744558746461746
                    53A6D6F6469667900323032322D30372D31375430383A34313A30382B30
                    303A303055072A050000000049454E44AE426082""",
        )
        form.add_control("/f")
        form.add_control("uid", "Uid", control="line", data=2, datatype="num", datalen=15, datadec=2, pic="F")
        if form.add_control("/h", "Title"):

            def add_id():
                form.s.uid = num(form.s.uid) + 1

            def sub_id():
                form.s.uid = num(form.s.uid) - 1

            form.add_control("", "+", control="toolbutton", valid=add_id)
            form.add_control("", "-", control="toolbutton", valid=sub_id)
            form.add_control("/")
        form.add_control("/")

        if form.add_control("/h"):
            form.add_control("name", "Name", control="line", data="First Name", datalen=100)
            form.add_control("birthdate", "Date of birth", control="date", data="2006-05-01")
            form.add_control("/")

        form.add_control("/t", "tab 1", alignment=7)

        form.add_control("", "label 1")
        form.add_control("", "label 2")
        form.add_control("", "label 2")

        form.add_control("/t", "tab 2")
        form.add_control("", "label 3")
        # form.add_control("prim", "Text", control="text")
        form.add_control("/")

        form.add_control("prim", "Text", control="text")

        form.add_control("/h", "-")
        form.add_control("/s")

        form.add_control(
            "",
            "Greet me",
            control="button",
            valid=lambda: q2Mess(f"{form.s.name}: {form.s.birthdate}"),
        )
        form.add_control("", "Close", control="button", valid=lambda: form.close())
        form.add_control("/")
        return form

    def show_form1(self):
        form = self.describe_form1()
        form.show_mdi_modal_form()

    def describe_form2(self):
        form = Q2Form("Second form")
        form.add_control("radio", "Color", pic="Red;White;Black", control="radio", data="2")
        form.add_control("check", "Transparency", pic="Transparency", control="check", data="")
        form.add_control("combo", "Popup List", control="combo", pic="Oprion1;Option2")
        form.add_control("/")
        form.add_control("/h")
        form.add_control("/s")
        form.add_control(
            "",
            "Greet me",
            control="button",
            valid=lambda: q2Mess(f"{form.s.name}-{form.s.birthdate}"),
        )

        def close_form():
            form.close()

        form.add_control("", "Close", control="button", valid=close_form)
        form.add_control("/")
        return form

    def show_form2(self):
        self.describe_form2().show_mdi_modal_form()

    def describe_complex_form(self):
        form = Q2Form("Complex form")
        form.add_control("/")
        form.add_control("/h")
        form.add_control("", "1", widget=self.describe_form1())
        form.add_control("/v")
        f1 = self.describe_form2()
        f2 = self.describe_form2()
        form.add_control("", "2", widget=f1)
        form.add_control("", "3", widget=f2)
        form.add_control("/")
        form.add_control("/")
        form.add_control("", "4", widget=self.describe_grid_form().get_grid_widget())

        return form

    def show_complex_form(self):
        self.describe_complex_form().show_mdi_modal_form()

    def describe_form4(self):
        form = Q2Form("Grid form")
        form.actions.add_action("New", lambda: q2Mess("New"))
        form.actions.add_action("Edit|1", lambda: q2Mess("Edit"))
        form.actions.add_action("Edit|2", lambda: q2Mess("Edit"))
        form.actions.add_action("Nt", lambda: q2Mess("Nt"))
        form.actions.add_action("Edit|3", lambda: q2Mess("Edit"))
        form.add_control("uid", "Uid", control="line")
        form.add_control("name", "Name", control="line", data="First Name")
        form.add_control("date", "Date of bith", control="date", data="1990-05-01")
        return form

    def describe_grid_form(self):
        data = [
            {"uid": 1, "name": "Lorem Ipsum", "date": "2005-01-15"},
            {"uid": 2, "name": "Dolor Sit", "date": "2005-01-15"},
            {"uid": 3, "name": "Quis autem", "date": "2005-01-15"},
            {"uid": 4, "name": "Iron nagel", "date": "2005-01-15"},
        ]
        form = self.describe_form4()
        form.set_model(Q2Model())
        form.model.set_records(data)
        return form

    def show_grid_form(self):
        form = self.describe_grid_form()
        form.show_mdi_modal_grid()

    def show_hide_menubar(self):
        self.show_menubar(not self.is_menubar_visible())

    def show_hide_toolbar(self):
        self.show_toolbar(not self.is_toolbar_visible())

    def show_hide_tabbar(self):
        self.show_tabbar(not self.is_tabbar_visible())

    def show_hide_statusbar(self):
        self.show_statusbar(not self.is_statusbar_visible())


def demo():
    app = DemoApp("q2gui Demo application")
    app.run()


if __name__ == "__main__":
    demo()
