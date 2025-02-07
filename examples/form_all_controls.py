"""
shows all the basic input controls(widgets)
"""


from q2gui.q2app import Q2App
from q2gui.q2app import load_q2engine
from q2gui.q2form import Q2Form
from q2gui.q2utils import today

load_q2engine(globals(), "PyQt6")


class DemoApp(Q2App):
    def on_new_tab(self):
        form = Q2Form("All controls")
        form.add_control("/")  # close default form layout
        if form.add_control("/h", "-"):
            if form.add_control("/f", "-"):
                form.add_control("", "Label")
                form.add_control(
                    "var1", "String input", control="line", data="One line data"
                )
                form.add_control(
                    "var2",
                    "Password input",
                    control="line",
                    data="One line data",
                    pic="*",
                )
                form.add_control(
                    "var3",
                    "Money input",
                    datatype="dec",
                    datalen=15,
                    datadec=2,
                    control="line",
                    data="123456.45",
                    pic="F",
                )
                form.add_control("var2", "Date input", control="date", data=today())
                form.add_control("var21", "Time input", datatype="time", control="time", data="15:45:00")
                form.add_control(
                    "var4",
                    "Radio button",
                    pic="Red;White",
                    control="radio",
                    data="White",
                )
                form.add_control("var5", "Checkbox", control="check", data=True)
                form.add_control("", "Pushbutton", control="button", mess="Tooltip")
                form.add_control("", "Toolbutton", control="toolbutton")
                form.add_control(
                    "var7", "Combo", pic="Red;White", control="combo", data="White"
                )
                form.add_control("/")
            if form.add_control("/v", "-"):
                form.add_control(
                    "var5", "My text", control="text", data="Line 1<br>Line 2"
                )
                form.add_control(
                    "var6", "My code", control="code", data="def f(): pass"
                )
                form.add_control("/")
            if form.add_control("/v", "-"):
                form.add_control(
                    "var8", "List", pic="Red;White", control="list", data="White"
                )
                form.add_control("/")
        form.run()


def demo():
    app = DemoApp(f"q2gui Sample applcation - {__file__}")
    app.run()


if __name__ == "__main__":
    demo()
