"""
shows a form with tabbed layouts
Ctrl+PgDown/PgUp for switch tabs
"""


from q2gui.q2app import Q2App
from q2gui.q2app import load_q2engine
from q2gui.q2form import Q2Form


load_q2engine(globals(), "PyQt6")


class DemoApp(Q2App):
    def on_new_tab(self):
        form = Q2Form("Tabs")
        form.add_control("/")  # close default form layout
        form.add_control("var", "Line input")
        if form.add_control("/t", "Tab1 - form layout"):
            if form.add_control("/f", "-"):
                form.add_control("var", "Line input")
                form.add_control("var", "Line input")
        if form.add_control("/t", "Tab2 - horizontal layout"):
            if form.add_control("/h", "-"):  # no label - no borders
                form.add_control("var", "Line input")
                form.add_control("var", "Line input")
        if form.add_control("/t", "Tab3 - vertical layout(by default)"):
            form.add_control("var", "Line input")
            form.add_control("var", "Line input")

        form.cancel_button = True
        form.run()


def demo():
    app = DemoApp(f"q2gui Sample applcation - {__file__}")
    app.run()


if __name__ == "__main__":
    demo()
