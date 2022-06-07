if __name__ == "__main__":
    import sys

    sys.path.insert(0, ".")

from urllib import request
from io import BytesIO, TextIOWrapper
from zipfile import ZipFile

from q2gui.pyqt6.q2app import Q2App as Q2App
from q2gui.pyqt6.q2form import Q2Form as Q2Form
from q2gui.q2model import Q2CsvModel, Q2Model
from q2gui.pyqt6.q2form import q2Mess, q2Wait

about = """Parses webpage and shows list of downloadable files (ZIP with CSV inside)
Uses build_grid_view_auto_form method to create UI
Then downloads selected file and shows it in the grid (sortable and filterable)
"""


class DemoApp(Q2App):
    def on_start(self):
        self.file_select_form()

    def on_init(self):
        self.add_menu("File|Links", self.file_select_form, toolbar="*")
        self.add_menu("File|-")
        self.add_menu("Help|About", lambda: q2Mess(about), toolbar="*")
        self.add_menu("File|Quit", self.close, toolbar=1)

    def file_select_form(self):
        url = (
            "https://eforexcel.com/wp/"
            "downloads-18-sample-csv-files-data-sets-for-testing-sales/"
        )
        req = request.Request(url, headers={"User-Agent": "Safari"})

        data: str = q2Wait(
            lambda: str(request.urlopen(req).read()), "Loading webpage..."
        )

        links = []
        for x in data.split('<a href="'):
            link = x.split('">')[0]
            if ".zip" in link:
                links.append({"link": link})

        form = Q2Form("Grid form")
        form.set_model(Q2Model())
        form.model.set_records(links)
        form.build_grid_view_auto_form()
        form.actions.add_action(
            text="Download", worker=lambda: self.load_and_show_file(form), hotkey="F3"
        )
        form.show_mdi_modal_grid()

    def load_and_show_file(self, form: Q2App):
        url = form.r.link  # get current row column data
        req = request.Request(url, headers={"User-Agent": "Safari"})

        data = q2Wait(lambda: request.urlopen(req).read(), "Loading file from web...")

        mem_zip_file_data = BytesIO()
        mem_zip_file_data.write(data)
        zip_file: ZipFile = ZipFile(mem_zip_file_data)
        csv_file_object = TextIOWrapper(zip_file.open(zip_file.namelist()[0]))

        form = Q2Form("CSV")
        model = q2Wait(
            lambda: q2CsvModel(csv_file_object=csv_file_object), "Loading CSV data"
        )
        form.set_model(model)
        form.build_grid_view_auto_form()
        form.show_mdi_modal_grid()


def demo():
    app = DemoApp("q2gui Demo application")
    app.run()


if __name__ == "__main__":
    demo()
