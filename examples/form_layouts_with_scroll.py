"""
shows a form with scrollable layouts
"""


from q2gui.q2app import Q2App
from q2gui.q2app import load_q2engine
from q2gui.q2form import Q2Form
from q2gui.q2utils import today

load_q2engine(globals(), "PyQt6")


class DemoApp(Q2App):
    def on_new_tab(self):
        form = Q2Form("Layouts with scroll")
        form.add_control("/")  # close default form layout
        if form.add_control("/vr", "Vertical scroll"):
            for x in range(100):
                form.add_control(label=f"Label {x:02}")
            form.add_control("/")
        if form.add_control("/hr", "Horizontal scroll"):
            for x in range(100):
                form.add_control(label=f"Label {x:02}")
            form.add_control("/")
        form.run()


def demo():
    app = DemoApp(f"q2gui Sample applcation - {__file__}")
    app.run()


if __name__ == "__main__":
    demo()
