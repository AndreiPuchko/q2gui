"""Downloads CSV file (from local folder or from web)
Uses build_grid_view_auto_form to create UI
Shows it's content in the editable grid
Functionality "save data to disk" not implemented.
"""
if __name__ == "__main__":
    import sys

    sys.path.insert(0, ".")

from urllib import request
from io import BytesIO, TextIOWrapper
from zipfile import ZipFile
import os

from q2gui.q2app import load_q2engine
from q2gui.q2app import Q2App
from q2gui.q2form import Q2Form

load_q2engine(globals(), "PyQt6")

from q2gui.q2dialogs import q2Mess
from q2gui.q2model import Q2CsvModel


class DemoApp(Q2App):
    def on_start(self):
        self.show_grid_form()

    def on_init(self):
        self.add_menu("File|Grid", self.show_grid_form, toolbar="*")
        self.add_menu("File|-")
        self.add_menu("Help|About", lambda: q2Mess("About q2gui"), toolbar="*")
        self.add_menu("File|Quit", self.close, toolbar=True)

    def show_grid_form(self):
        # load some CSV data from ...
        file_name = "temp/electronic-card-transactions-october-2021-csv-tables.csv"
        if not os.path.isfile(file_name):
            url = (
                "https://www.stats.govt.nz/assets/Uploads/"
                "Electronic-card-transactions/"
                "Electronic-card-transactions-October-2021/"
                "Download-data/electronic-card-transactions-october-2021-csv.zip"
            )
            data = request.urlopen(url).read()
            mem_zip_file_data = BytesIO()
            mem_zip_file_data.write(data)
            zip_file: ZipFile = ZipFile(mem_zip_file_data)
            csv_file_object = TextIOWrapper(zip_file.open(zip_file.namelist()[0]))
        else:
            csv_file_object = open(file_name)
        # Define form
        # self.process_events()
        form = Q2Form("Grid form")
        form.set_model(Q2CsvModel(csv_file_object=csv_file_object))
        form.actions.add_action("/crud")
        form.build_grid_view_auto_form()

        form.actions.add_action(
            "Show Period value", worker=lambda: q2Mess(f"{form.r.Period}"), hotkey="F4"
        )
        form.show_mdi_modal_grid()


def demo():
    app = DemoApp("q2gui Demo application")
    app.run()


if __name__ == "__main__":
    demo()
