if __name__ == "__main__":
    import sys

    sys.path.insert(0, ".")


from random import randint
from q2gui.q2dialogs import q2Mess

from q2gui.q2model import Q2CursorModel

from q2db.schema import Q2DbSchema
from q2db.db import Q2Db
from q2db.cursor import Q2Cursor

from q2gui.q2app import Q2App
from q2gui.q2form import Q2Form
from q2gui.q2app import load_q2engine

load_q2engine(globals(), "PyQt6")


class dataSchema(Q2DbSchema):
    def __init__(self):
        super().__init__()
        self.add_customers()
        self.add_products()
        self.add_orders()
        self.add_order_lines()

    def add_order_lines(self):
        self.add(table="order_lines", column="id", datatype="int", datalen=9, pk=True)
        self.add(
            table="order_lines",
            column="product_id",
            to_table="products",
            to_column="product_id",
            related="name",
        )
        self.add(
            table="order_lines",
            column="order_id",
            to_table="orders",
            to_column="order_id",
            related="date",
        )
        self.add(
            table="order_lines",
            column="quantity",
            datatype="num",
            datalen=10,
            datadec=4,
        )
        self.add(
            table="order_lines",
            column="price",
            datatype="num",
            datalen=10,
            datadec=2,
        )

    def add_orders(self):
        self.add(table="orders", column="order_id", datatype="int", datalen=9, pk=True)
        self.add(table="orders", column="date", datatype="date")
        self.add(
            table="orders",
            column="customer_id",
            to_table="customers",
            to_column="customer_id",
            related="name",
        )

    def add_products(self):
        self.add(table="products", column="product_id", datatype="int", datalen=9, pk=True)
        self.add(table="products", column="name", datatype="varchar", datalen=100)

    def add_customers(self):
        self.add(
            table="customers",
            column="customer_id",
            datatype="int",
            datalen=9,
            pk=True,
        )
        self.add(table="customers", column="name", datatype="varchar", datalen=100)
        self.add(table="customers", column="address", datatype="varchar", datalen=100)
        self.add(table="customers", column="comment", datatype="text")


def load_mock_data(db: Q2Db):
    customer_qt = 10
    product_qt = 10
    order_qt = 100
    order_lines_qt = 6
    for x in range(1, customer_qt):
        db.insert(
            "customers",
            {
                "customer_id": x,
                "name": f"Customer {x}{str(randint(0,600)*6)}",
                "address": f"Address {x}{str(randint(0,600)*6)}",
                "comment": f"Comment {x}{str(randint(0,600)*6)}",
            },
        )
    for x in range(1, product_qt):
        db.insert("products", {"product_id": x, "name": f"Product {x}"})
    for x in range(1, order_qt):
        db.insert(
            "orders",
            {
                "order_id": x,
                "customer_id": randint(1, customer_qt - 1),
                "date": f"2022-01-{randint(1,31):02}",
            },
        )
        for y in range(1, randint(2, order_lines_qt)):
            rez = db.insert(
                "order_lines",
                {
                    "order_id": x,
                    "product_id": randint(1, product_qt - 1),
                    "quantity": randint(1, 100),
                    "price": randint(1, y),
                },
            )
            if rez is not True:
                print(db.last_sql_error)
    assert len(db.get_tables()) == 8
    assert db.cursor(table_name="customers").row_count() == customer_qt - 1
    assert db.cursor(table_name="products").row_count() == product_qt - 1
    assert db.cursor(table_name="orders").row_count() == order_qt - 1


class DemoApp(Q2App):
    def on_init(self):
        # super().on_init()
        self.set_color_mode("light")
        self.create_database()

        self.add_menu("File|About", lambda: q2Mess("First application!"))
        self.add_menu("File|-", None)
        self.add_menu("File|Dark Mode", lambda: self.set_color_mode("dark"))
        self.add_menu("File|Light Mode", lambda: self.set_color_mode("light"))
        self.add_menu("File|-")
        self.add_menu("File|Exit", self.close, toolbar=1, icon="exit.png")
        self.add_menu("Catalogs|Customers", self.customers, toolbar=1)
        self.add_menu("Catalogs|Products", self.products, toolbar=1)
        self.add_menu("Documents|Orders", self.filter_orders, toolbar=1)
        self.add_menu("Reports|Sales", self.show_sales, toolbar=1)

    def on_new_tab(self):
        # def on_start(self):
        # self.form_order_lines().run()
        # self.orders()
        self.customers()
        # self.filter_orders()
        # self.products()
        # self.show_sales()
        pass

    def create_database(self):
        self.db = Q2Db("sqlite3", database_name=":memory:")
        self.db.set_schema(dataSchema())
        load_mock_data(self.db)

    def form_customers(self):
        form = Q2Form("Customers")
        form.no_view_action = 1
        form.add_control(column="customer_id", label="Customer Id", datatype="int", pk="*")
        form.add_control("name", "Name", datatype="char", datalen=100)
        form.add_control("address", "Address", datatype="char", datalen=100)
        # form.add_control("/")
        # form.add_control("/v", "333")
        form.add_control("comment", "Comment", datatype="text")

        cursor: Q2Cursor = self.db.table(table_name="customers")
        model = Q2CursorModel(cursor)
        form.set_model(model)
        form.actions.add_action("/crud")
        form.add_action(
            "Orders", child_form=self.form_orders, child_where="customer_id={customer_id}", hotkey="F2"
        )
        form.max_child_level = 2
        return form

    def customers(self):
        customers = self.form_customers()
        customers.run()

    def form_products(self):
        form = Q2Form("Products")
        form.add_control("product_id", "Product Id", datatype="int", pk="*")
        form.add_control("name", "Name", datalen=100, datatype="char")
        form.set_model(Q2CursorModel(self.db.table(table_name="products")))
        form.actions.add_action("/crud")
        form.add_action(
            text="Orders",
            worker=None,
            child_form=self.form_orders,
            child_where="""order_id in (select order_id from order_lines  where product_id={product_id})""",
            hotkey="F2",
        )
        return form

    def products(self):
        self.form_products().run()

    def form_orders(self):
        form = Q2Form("Orders")
        form.add_control("order_id", "Order Id", datatype="int", pk="*", noform=1)
        form.add_control(
            column="customer_id",
            label="Customer",
            datatype="int",
            control="line",
            to_table="customers",
            to_column="customer_id",
            to_form=self.form_customers,
            related="name",
        )
        form.add_control("date", "Date", datatype="date")
        form.add_action("/crud")
        form.add_action("-")
        form.add_action(
            "Lines", child_form=self.form_order_lines, child_where="order_id={order_id}", hotkey="F2"
        )
        form.set_model(Q2CursorModel(self.db.table("orders")))
        return form

    def orders(self):
        self.form_orders().run()

    def form_order_lines(self):
        form = Q2Form("Order lines")
        form.add_control("id", "line id", datatype="int", pk="*", noform=1, nogrid=1)
        form.add_control(
            column="order_id",
            label="Order Id",
            datatype="int",
            to_table="orders",
            to_column="order_id",
            related="date",
            noform=0,
            nogrid=0,
        )
        form.add_control(
            column="product_id",
            label="Product",
            control="line",
            to_table="products",
            to_column="product_id",
            to_form=self.form_products,
            related="name",
        )
        form.add_control("quantity", "Quantity", datatype="num", datalen=10, datadec=4)
        form.add_control("price", "Price", datatype="num", datalen=15, datadec=2)

        form.add_action("/crud")
        form.set_model(Q2CursorModel(self.db.table("order_lines")))
        return form

    def form_filter_orders(self):
        form = Q2Form("Filter orders")
        form.add_control("/")
        form.add_control("/h")
        form.add_control("date1", "From date", datatype="date", data="2022-01-01")
        form.add_control("date2", "To date", datatype="date", data="2022-01-31")
        form.add_control("/")
        form.add_control("/f")
        form.add_control(
            "customer_id",
            "Customer",
            datatype="int",
            control="line",
            to_table="customers",
            to_column="customer_id",
            to_form=self.form_customers,
            related="name",
            data=3,
            check="*",
        )

        form.add_control(
            "product_id",
            "Product",
            datatype="int",
            control="line",
            to_table="products",
            to_column="product_id",
            to_form=self.form_products,
            related="name",
            check="*",
        )

        def show_filtered_orders():
            filter_list = []
            filter_list.append(f"date>='{form.s.date1}' and date<='{form.s.date2}'")
            for x in [form.w.customer_id]:
                if x.check.is_checked():
                    filter_list.append(f'{x.meta.get("column")} = {x.get_text()}')
            if form.w.product_id.check.is_checked():
                filter_list.append(
                    f"order_id in (select order_id from order_lines where product_id = {form.s.product_id}) "
                )

            form_orders = self.form_orders()
            form_orders.model.set_where(" and ".join(filter_list))
            form_orders.run()
            return False

        form.ok_button = 1
        form.cancel_button = 1
        form.valid = show_filtered_orders

        # def after_form_show():
        #     form.s.date1 = '2023-05-05'
        #     print(form.s.date1)
        # form.after_form_show = after_form_show
        return form

    def filter_orders(self):
        self.form_filter_orders().run()

    def show_sales(self):
        cursor = self.db.cursor(
            """
                                select
                                    product_id,
                                    customer_id,
                                    sum(quantity) as quantity,
                                    sum(quantity*price) as totalsum,
                                    sum(quantity*price) / sum(quantity*0.1) as av_price
                                from orders, order_lines
                                where orders.order_id = order_lines.order_id
                                group by customer_id, product_id
                                """
        )
        form = Q2Form("Total sales!")
        form.add_control(
            column="product_id",
            label="Product",
            control="line",
            to_table="products",
            to_column="product_id",
            to_form=self.form_products,
            related="name",
        )
        form.add_control(
            column="customer_id",
            label="Customer",
            datatype="int",
            control="line",
            to_table="customers",
            to_column="customer_id",
            to_form=self.form_customers,
            related="name",
        )
        form.add_control("quantity", "Quantity")
        form.add_control("totalsum", "Totalsum")
        form.set_model(Q2CursorModel(cursor))
        form.run()


def demo():
    app = DemoApp("q2gui - the database (q2db) app")
    app.run()


if __name__ == "__main__":
    demo()
