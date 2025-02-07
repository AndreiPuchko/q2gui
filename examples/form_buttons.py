"""
shows a form with buttons when new tab is added
validating click with valid
"""


from q2gui.q2app import Q2App
from q2gui.q2app import load_q2engine
from q2gui.q2dialogs import q2mess
from q2gui.q2form import Q2Form

load_q2engine(globals(), "PyQt6")


class DemoApp(Q2App):
    def on_new_tab(self):
        form = Q2Form("Hello world")
        form.add_control(
            "",
            "Push me",
            control="button",
            valid=lambda: q2mess(
                f"Button pressed!"
                f"<br><br>Radio-{form.s.radio}"
                f"<br><br>My text: <b>{'disabled' if form.s.check else 'enabled'}</b>"
            ),
        )

        def radio_valid():
            form.s.mytext = f"{form.s.radio}"

        form.add_control(
            "radio",
            "Radio button",
            pic="Option 1;Option 2;Option 3",
            control="radio",
            valid=radio_valid,
        )
        form.add_control(
            "check",
            "Disable My text",
            control="check",
            valid=lambda: form.w.mytext.set_disabled(form.s.check),
            data=1,
        )
        form.add_control(
            "mytext", "My text", control="text", disabled=1, data="initial text"
        )
        form.cancel_button = True
        form.run()
        if form.ok_pressed:
            q2mess(
                f"""Ok pressed!<br>
                   Entered data: <font color=red size=+3><b>{form.s.var}</b>!"""
            )


def demo():
    app = DemoApp(f"q2gui Sample applcation - {__file__}")
    app.run()


if __name__ == "__main__":
    demo()
