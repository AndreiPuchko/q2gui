"""
shows a simple form
"""

from q2gui.q2app import Q2App
from q2gui.q2form import Q2Form

from q2gui.q2app import load_q2engine
from q2gui.q2dialogs import q2mess

load_q2engine(globals(), "PyQt6")


class DemoApp(Q2App):
    def on_new_tab(self):
        self.hide_tabbar()  # avoid adding a new tab
        form = Q2Form("Hello world")
        form.add_control("", "Hello World!")
        # adding a control named var into form
        form.add_control("var", " Enter some data", data="Hello World")

        form.ok_button = True  # show OK button
        form.cancel_button = True  # show Cancel button
        form.run()
        if form.ok_pressed:  # when OK button pressed (shortcut - PgDown)
            # the form.s.var notation provides access to the contents of a control named var
            q2mess(
                f"""Ok pressed!<br>
                   Entered data:<br> <font color=darkgreen size=+3><b>{form.s.var}</b>!"""
            )
        self.close()  # close the app


def demo():
    app = DemoApp(f"q2gui Sample applcation")
    app.run()


if __name__ == "__main__":
    demo()
