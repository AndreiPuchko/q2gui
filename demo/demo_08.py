if __name__ == "__main__":
    import sys

    sys.path.insert(0, ".")


from q2gui.q2dialogs import q2Mess

from q2gui.q2model import Q2CursorModel

from q2db.schema import Q2DbSchema
from q2db.db import Q2Db
from q2db.cursor import Q2Cursor
from random import randint

from q2gui.q2app import Q2App
from q2gui.q2form import Q2Form
from q2gui.q2app import load_q2engine

load_q2engine(globals(), "PyQt6")


def mock_data_load(db: Q2Db):
    customer_qt = 100
    for x in range(1, customer_qt):
        db.insert(
            "customers",
            {
                "customer_id": x,
                "name": f"Customer {x}{str(randint(0,600)*6)}",
                "vip": {0: "", 1: "*"}[x % 2],
                "combo_status": x % 3 + 1,
                "list_status": x % 3 + 1,
                "radio_status": x % 3 + 1,
            },
        )


class DemoApp(Q2App):
    def on_start(self):
        mock_data_load(self.db)
        self.set_color_mode("dark")
        self.customers()

    def create_database(self):
        self.db = Q2Db("sqlite3", database_name=":memory:")

    def on_init(self):
        self.create_database()
        self.q2style.font_size = 10
        self.add_menu("File|About", lambda: q2Mess("First application!"))
        self.add_menu("File|-", None)
        self.add_menu("File|Dark Mode", lambda: self.set_color_mode("dark"), icon="▓", toolbar=1)
        self.add_menu("File|Light Mode", lambda: self.set_color_mode("light"), icon="▒", toolbar=1)
        self.add_menu("File|Clean Mode", lambda: self.set_color_mode("clean"), icon="|", toolbar=1)
        self.add_menu("File|-")
        self.add_menu("File|Exit", self.close, toolbar=1, icon="exit.png")
        self.add_menu("Catalogs|Customers", self.customers, toolbar=1, icon="$")

        data_schema = Q2DbSchema()

        for x in self.form_customers().get_table_schema():
            data_schema.add(**x)

        self.db.set_schema(data_schema)
        # print(self.db.migrate_error_list)
        mock_data_load(self.db)
        # self.customers()

    def form_customers(self):
        form = Q2Form("Customers")

        form.add_control(column="customer_id", label="Customer Id", datatype="int", pk="*", ai="*")
        form.add_control("name", "Name", datatype="char", datalen=100)
        form.add_control("/h", "3333")
        form.add_control("ddd1", "T1", datatype="char", datalen=5)
        form.add_control("ddd2", "T2", datatype="char", datalen=5)
        form.add_control("summa", "Summa", datatype="num", datalen=15, datadec=2, pic="F")
        form.add_control("/s")
        form.add_control("/")
        form.add_control("vip", "VIP", datatype="char", datalen=1, control="check", pic="VIP client")

        status_control_num = {"datatype": "int", "datalen": 1, "pic": "active;frozen;blocked"}
        status_control_char = {"datatype": "char", "datalen": 15, "pic": "active;frozen;blocked"}

        form.add_control("radio_status", "Num Radio Status", control="radio", **status_control_num)
        form.add_control("radio_status_char", "Char Radio Status", control="radio", **status_control_char)

        form.add_control("combo_status", "Num Combo Status", control="combo", **status_control_num)
        form.add_control("combo_status", "Char Combo Status", control="combo", **status_control_char)

        form.add_control("/")
        form.add_control("/h", "Group box title")
        form.add_control("list_status", "Num List Status", control="list", **status_control_num)
        form.add_control("list_status_char", "Char List Status", control="list", **status_control_char)

        cursor: Q2Cursor = self.db.table(table_name="customers")
        model = Q2CursorModel(cursor)
        form.set_model(model)
        form.actions.add_action("/crud")
        form.actions.add_action("Print", lambda: q2Mess("Test"), icon="⎙", tag="cyan")
        form.actions.add_action("Test", lambda: q2Mess("Test"), tag="HotPink")
        return form

    def customers(self):
        self.form_customers().show_mdi_modal_grid()


def demo():
    app = DemoApp("q2gui - the database app")
    app.run()


if __name__ == "__main__":
    demo()
