if __name__ == "__main__":
    import sys

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()

import csv
import datetime
import re

import q2gui.q2app as q2app
from q2gui.q2utils import num

try:
    from q2db.cursor import Q2Cursor
    from q2db.db import Q2Db
except Exception:
    pass


class Q2Model:
    def __init__(self):
        self.q2_form = None
        self.columns = []
        self.headers = []
        self.alignments = []

        self.records = []
        self.proxy_records = []
        self.use_proxy = False
        self.relation_cache = {}
        self.lastdata_error_text = ""

        self.meta = []

        # CRUD flags
        self.readonly = True
        self.delete_enabled = False
        self.insert_enabled = False
        self.update_enabled = False

        self.filterable = False

        self.data_changed = False

        self.order_text = ""
        self.where_text = ""

    def get_row(self, row_number):
        if row_number < len(self.records):
            return self.records[row_number]
        else:
            return None

    def get_table_name(self):
        return ""

    def get_data_error(self):
        return self.lastdata_error_text

    def set_data_error(self, text=""):
        self.lastdata_error_text = text

    def update(self, record: dict, current_row, refresh=True):
        if self.proxy_records:
            current_row = self.proxy_records[current_row]
        if self.records:
            self.records[current_row].update(record)
        self.data_changed = True
        if refresh:
            self.refresh()
        return True

    def insert(self, record: dict, current_row=0, refresh=True):
        self.records.append(record)
        self.data_changed = True
        if refresh:
            self.refresh()
        return True

    def delete(self, row_number, refresh=True):
        if self.proxy_records:
            row_number = self.proxy_records[row_number]
        self.records.pop(row_number)
        self.data_changed = True
        if refresh:
            self.refresh()
        return True

    def set_where(self, where_text=""):
        self.where_text = where_text
        if self.where_text:
            self.use_proxy = True
            self.proxy_records = []
            for row, rec in enumerate(self.records):
                rc = dict(rec)
                if eval(self.where_text, rc):
                    self.proxy_records.append(row)
        else:
            self.use_proxy = False
        self.refresh()
        return self

    def get_where(self):
        return self.where_text

    def set_order(self, order_data=""):
        if isinstance(order_data, int):
            self.order_text = self.columns[order_data]
        elif isinstance(order_data, list):
            self.order_text = ",".join(order_data)
        else:
            self.order_text = order_data
        if self.records:
            colname = self.order_text

            if self.proxy_records:
                sort_records = {}
                for x in range(len(self.proxy_records)):
                    value = self.records[self.proxy_records[x]][colname]
                    if value not in sort_records:
                        sort_records[value] = [self.proxy_records[x]]
                    else:
                        sort_records[value].append(self.proxy_records[x])
            else:
                sort_records = {}
                for x in range(len(self.records)):
                    if self.records[x][colname] not in sort_records:
                        sort_records[self.records[x][colname]] = [x]
                    else:
                        sort_records[self.records[x][colname]].append(x)

            sorted_keys = sorted([x for x in sort_records.keys()])
            # sorted_keys.sort()
            tmp_proxy_records = []
            for x in sorted_keys:
                for y in sort_records[x]:
                    tmp_proxy_records.append(y)

            self.proxy_records = tmp_proxy_records
            self.use_proxy = True

    def refresh(self):
        self.relation_cache = {}

    # def refresh(self):
    #     self.set_where(self.where_text)
    #     self.set_order(self.order_text)

    def reset(self):
        self.records = []
        self.proxy_records = []
        self.use_proxy = False
        self.relation_cache = {}
        self.lastdata_error_text = ""

    def set_records(self, records):
        self.records = records

    def build(self):
        self.columns = []
        self.headers = []
        self.alignments = []
        self.meta = []
        for meta in self.q2_form.controls:
            if meta.get("column", "").startswith("/") or meta.get("nogrid"):
                continue
            if meta.get("control", "") in ["button", "widget", "form"]:
                continue
            self.q2_form.model.add_column(meta)

    def add_column(self, meta):
        if not meta.get("control"):
            meta["control"] = "line"

        meta = q2app.Q2Controls.validate(meta)
        self.columns.append(meta["column"])
        self.headers.append(meta["gridlabel" if meta.get("gridlabel") else "label"])
        self.alignments.append(meta.get("alignment", "7"))
        self.meta.append(meta)

    def get_record(self, row):
        if row < 0 or row > len(self.records) - 1:
            return {}
        if self.use_proxy:
            return self.records[self.proxy_records[row]]
        else:
            return self.records[row]

    def _get_related(self, value, meta, do_not_show_value=False, reset_cache=False):
        if meta.get("num") and num(value) == 0:
            return ""
        elif value == "":
            return ""
        key = (meta["to_table"], f"{meta['to_column']}='{value}'", meta["related"])
        if not reset_cache and key in self.relation_cache:
            related = self.relation_cache[key]
        else:
            related = self.get_related(meta["to_table"], f"{meta['to_column']}='{value}'", meta["related"])
            self.relation_cache[key] = related
        if related is None:
            related = ""
        if do_not_show_value:
            return f"{related}"
        else:
            return f"{value},{related}"

    def get_related(self, to_table, filter, related):
        return "get_related"

    def data(self, row, col, role="display"):
        if role == "display":
            colName = self.columns[col]
            value = self.get_record(row).get(colName, "")
            meta = self.meta[col]
            if meta.get("relation"):
                value = self._get_related(value, meta)
            elif self.is_strign_for_num(meta):
                value = meta.get("pic").split(";")[int(num(value)) - 1]
            elif meta.get("num"):  # Numeric value
                if num(value) == 0:  # do not show zero
                    value = ""
                elif meta.get("pic") == "F":  # financial format
                    format_string = q2app.FINANCIAL_FORMAT % meta.get("datadec", 0)
                    value = format_string.format(num(value))
            elif meta["datatype"] == "date":
                try:
                    value = datetime.datetime.strptime(value, "%Y-%m-%d").strftime(q2app.DATA_FORMAT_STRING)
                except Exception:
                    value = ""
            return value

    def is_strign_for_num(self, meta):
        """return str data from numeric controls - radio, list, combo"""
        return meta.get("num") and ("radio" in meta["control"] or meta["control"] in ("list", "combo"))

    def alignment(self, col):
        if self.meta[col].get("relation"):
            return 7
        elif self.is_strign_for_num(self.meta[col]):
            return 7
        return self.alignments[col]

    def column_header_data(self, col):
        return self.headers[col]

    def row_header_data(self, row):
        return f"{row}"

    def row_count(self):
        if self.use_proxy:
            return len(self.proxy_records)
        else:
            return len(self.records)

    def column_count(self):
        return len(self.columns)

    def parse_lookup_text(self, text):
        text = text.upper()
        raw_cond_list = ["+"] + re.split("([+-])", text)
        cond_list = []
        for cond in range(int(len(raw_cond_list) / 2)):
            operator = raw_cond_list[cond * 2]
            value = raw_cond_list[cond * 2 + 1]
            if operator and value:
                cond_list.append([operator, value])
        return cond_list

    def lookup(self, column, text):
        """search for text in column, return list of [row, value]"""
        cond_list = self.parse_lookup_text(text)
        rez = []
        for x in range(self.row_count()):
            cond_result = True
            for cond in cond_list:
                operator = cond[0]
                value = cond[1]
                model_value = self.get_record(x)[self.columns[column]]
                if self.meta[column].get("relation"):
                    model_value = self._get_related(model_value, self.meta[column])

                if operator == "+" and value not in model_value.upper():
                    cond_result = False
                elif operator == "-" and value in model_value.upper():
                    cond_result = False
            if cond_result:
                rez.append([x, model_value])
        return rez

    def data_export(self, file):
        pass

    def data_import(self, file):
        pass


class Q2CsvModel(Q2Model):
    def __init__(self, csv_file_object=None):
        super().__init__()
        csv_dict = csv.DictReader(csv_file_object)
        # If there are names with space -  replace spaces in columns names
        if [filename for filename in csv_dict.fieldnames if " " in filename]:
            fieldnames = [x.replace(" ", "_") for x in csv_dict.fieldnames]
            csv_dict = csv.DictReader(csv_file_object, fieldnames)
        self.set_records([x for x in csv_dict])
        self.filterable = True

    # def update(self, record: dict, current_row):
    #     self.records[current_row] = record
    #     self.data_changed = True
    #     self.refresh()
    #     return True

    # def insert(self, record: dict, current_row):
    #     self.records.append(record)
    #     self.data_changed = True
    #     self.refresh()
    #     return True

    # def delete(self, row_number):
    #     self.records.pop(row_number)
    #     self.data_changed = True
    #     self.refresh()
    #     return True

    # def set_where(self, where_text=""):
    #     self.where_text = where_text
    #     if self.where_text:
    #         self.use_proxy = True
    #         self.proxy_records = []
    #         for row, rec in enumerate(self.records):
    #             if eval(self.where_text, rec):
    #                 self.proxy_records.append(row)
    #     else:
    #         self.use_proxy = False
    #     self.refresh()

    # def set_order(self, order_data=""):
    #     super().set_order(order_data=order_data)

    #     colname = self.order_text

    #     if self.proxy_records:
    #         sort_records = {}
    #         for x in range(len(self.proxy_records)):
    #             value = self.records[self.proxy_records[x]][colname]
    #             if value not in sort_records:
    #                 sort_records[value] = [self.proxy_records[x]]
    #             else:
    #                 sort_records[value].append(self.proxy_records[x])
    #     else:
    #         sort_records = {}
    #         for x in range(len(self.records)):
    #             if self.records[x][colname] not in sort_records:
    #                 sort_records[self.records[x][colname]] = [x]
    #             else:
    #                 sort_records[self.records[x][colname]].append(x)

    #     sorted_keys = sorted([x for x in sort_records.keys()])
    #     # sorted_keys.sort()
    #     tmp_proxy_records = []
    #     for x in sorted_keys:
    #         for y in sort_records[x]:
    #             tmp_proxy_records.append(y)

    #     self.proxy_records = tmp_proxy_records
    #     self.use_proxy = True


class Q2CursorModel(Q2Model):
    def __init__(self, cursor: Q2Cursor = None):
        super().__init__()
        self.cursor = cursor

        self.readonly = False
        self.delete_enabled = False
        self.insert_enabled = False
        self.update_enabled = False

    def get_table_name(self):
        return self.cursor.table_name

    def row_count(self):
        return self.cursor.row_count()

    def get_record(self, row):
        return self.cursor.record(row)

    def refresh(self):
        super().refresh()
        self.cursor.refresh()

    def delete(self, current_row=0, refresh=True):
        self.set_data_error()
        record = self.get_record(current_row)
        if self.cursor.delete(record, refresh=False):
            if refresh:
                self.refresh()
            return True
        else:
            self.set_data_error(self.cursor.last_sql_error())
            return False

    def update(self, record: dict, current_row=0, refresh=True):
        self.set_data_error()
        if self.cursor.update(record):
            if refresh:
                self.refresh()
            return True
        else:
            self.set_data_error(f"{self.cursor.last_sql_error()}<br>{self.cursor.last_sql()}")
            return False

    def insert(self, record: dict, current_row=0, refresh=True):
        self.set_data_error()
        if self.cursor.insert(record):
            if refresh:
                self.refresh()
            return True
        else:
            self.set_data_error(self.cursor.last_sql_error())
            return False

    def get_related(self, to_table, filter, related):
        db: Q2Db = self.cursor.q2_db
        return db.get(to_table, filter, related)

    def set_order(self, order_data):
        if self.cursor.table_name:
            super().set_order(order_data=order_data)
            self.cursor.set_order(self.order_text)
        return self

    def set_where(self, where_text=""):
        self.cursor.set_where(where_text)
        self.refresh()
        return super().set_where(where_text)

    def add_column(self, meta):
        """update metadata from db"""
        db: Q2Db = self.cursor.q2_db
        db_meta = db.db_schema.get_schema_table_attr(self.cursor.table_name, meta["column"])
        meta["pk"] = db_meta.get("pk", "")
        meta["datatype"] = db_meta.get("datatype", meta["datatype"])
        if num(meta["datalen"]) < num(db_meta.get("datalen", 10)):
            meta["datalen"] = int(num(db_meta.get("datalen", 10)))
        if "datadec" not in meta:
            meta["datadec"] = int(num(db_meta.get("datadec", 2)))
        return super().add_column(meta)

    def data_export(self, file: str, tick_callback=None):
        if file.lower().endswith(".csv"):
            self.cursor.export_csv(file, tick_callback=tick_callback)
        else:
            self.cursor.export_json(file, tick_callback=tick_callback)

    def data_import(self, file: str, tick_callback=None):
        if file.lower().endswith(".csv"):
            rez = self.cursor.import_csv(file, tick_callback=tick_callback)
        else:
            rez = self.cursor.import_json(file, tick_callback=tick_callback)
        self.refresh()
        return rez
