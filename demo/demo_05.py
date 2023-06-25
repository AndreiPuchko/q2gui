if __name__ == "__main__":
    import sys

    sys.path.insert(0, ".")


from urllib import request
from io import BytesIO, TextIOWrapper
from zipfile import ZipFile
import time
import csv
import os


from q2gui.q2model import Q2Model
from q2gui.q2dialogs import q2Mess, q2Wait, q2WaitMax, q2WaitStep, Q2WaitShow, q2working

from q2gui.q2app import Q2App
from q2gui.q2form import Q2Form
from q2gui.q2app import load_q2engine

load_q2engine(globals(), "PyQt6")


class DemoApp(Q2App):

    def on_start(self):
        self.run_simple_wait_bar()

    def run_simple_wait_bar(self):
        steps = 500
        w = Q2WaitShow("Update:", steps)
        for x in range(steps):
            if w.step(f"Step {x}"):
                break
            time.sleep(0.01)
        w.close()

    def run_thread_wait_bar(self):
        def worker():
            def real_worker():
                steps = 500
                q2WaitMax(steps)
                for x in range(steps):
                    q2WaitStep()
                    time.sleep(0.01)

            return real_worker

        q2working(worker(), "W o r k i n g")

    def on_init(self):
        self.add_menu("File|Grid", self.show_grid_form, toolbar="*")
        self.add_menu("File|MdiNonModal", self.mdi_non_modal, toolbar="*")
        self.add_menu("Waitbars|Simple", self.run_simple_wait_bar)
        self.add_menu("Waitbars|Smart", self.run_thread_wait_bar)

        self.add_menu("Help|About", lambda: q2Mess("About q2gui"), toolbar="*")

        self.add_menu("File|-")
        self.add_menu("File|Quit", self.close, toolbar="*")

    def describe_grid_form(self):
        file_name = "temp/electronic-card-transactions-october-2021-csv-tables.csv"
        if not os.path.isfile(file_name):
            url = (
                "https://www.stats.govt.nz/assets/"
                "Uploads/Electronic-card-transactions/"
                "Electronic-card-transactions-October-2021/"
                "Download-data/"
                "electronic-card-transactions-october-2021-csv.zip"
            )
            data = request.urlopen(url).read()
            mem_zip_file_data = BytesIO()
            mem_zip_file_data.write(data)
            zip_file: ZipFile = ZipFile(mem_zip_file_data)

            csv_file_object = TextIOWrapper(zip_file.open(zip_file.namelist()[0]))
            csv_file_object2 = TextIOWrapper(zip_file.open(zip_file.namelist()[0]))

        else:
            csv_file_object = open(file_name)
            csv_file_object2 = open(file_name)

        csv_dict = csv.DictReader(csv_file_object)
        csv_dict2 = csv.DictReader(csv_file_object2)

        form = Q2Form("Grid form")
        form.set_model(Q2Model())

        def w1(form: Q2App = form, csv_dict2=csv_dict2):
            def real_do():
                for x in [x for x in csv_dict2]:
                    form.model.records.append(x)

            return real_do

        q2working(w1(), "Loading")

        form.add_control("/f")
        for x in csv_dict.fieldnames:
            form.add_control(x, x, control="line")

        form.actions.add_action("/view")
        return form

    def show_grid_form(self):
        form = self.describe_grid_form()
        form.show_mdi_modal_grid()

    def mdi_non_modal(self):
        wait_window = Q2Form("wai")
        wait_window.add_control(label="333333333333")
        wait_window.show_mdi_form()


def demo():
    app = DemoApp("q2gui Demo application")
    app.run()


if __name__ == "__main__":
    demo()
