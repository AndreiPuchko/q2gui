"""
shows a form with vertical and horizontal splitters
"""


from q2gui.q2app import Q2App
from q2gui.q2app import load_q2engine
from q2gui.q2form import Q2Form
from q2gui.q2utils import today

load_q2engine(globals(), "PyQt6")


class DemoApp(Q2App):
    def on_new_tab(self):
        form = Q2Form("Layouts with splitters")
        form.add_control("/")  # close default form layout
        if form.add_control("/hs"):
            if form.add_control("/vs"):
                form.add_control("", "Label")
                form.add_control("var1", "Line input", control="line", data="One line data")
                if form.add_control("/h"):
                    form.add_control("text1", "Text input1", control="text", stretch=1)
                    form.add_control("text2", "Text input2", control="text", stretch=2)
                    form.add_control("/")
                form.add_control("var2", "Date input", control="date", data=f"{today()}")
                form.add_control("/")
            if form.add_control("/v"):
                form.add_control("text3", "Text input3", control="text", stretch=1)
                form.add_control("text4", "Text input4", control="text", stretch=2)
                form.add_control("/")
        form.run()


def demo():
    app = DemoApp(f"q2gui Sample applcation - {__file__}")
    app.run()


if __name__ == "__main__":
    demo()
