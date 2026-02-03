#    Copyright © 2021 Andrei Puchko
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


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
        self.hidden_rows = []
        self.filtered_columns = []
        self.columns_filter_values = {}
        self.use_proxy = False
        self.relation_cache = {}
        self.lastdata_error_text = ""
        self.refreshed = False

        self.meta = []
        self.cursor = None

        # CRUD flags
        self.readonly = True
        self.delete_enabled = False
        self.insert_enabled = False
        self.update_enabled = False

        self.filterable = False

        self.data_changed = False
        self.q2_bcolor = False
        self.q2_fcolor = False
        self.q2_bcolors = {}
        self.q2_fcolors = {}

        self.order_text = ""
        self.where_text = ""

    def is_hidden(self, row):
        return row in self.hidden_rows

    def get_records(self):
        for x in range(self.row_count()):
            yield self.records[x]

    def get_row(self, row_number):
        return self.get_record(row_number)

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
        self.filtered_columns = []
        self.columns_filter_values = {}
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

    def set_order(self, order_data="", direction=None):
        if isinstance(order_data, int):
            self.order_text = self.columns[order_data]
        elif isinstance(order_data, list):
            self.order_text = ",".join(order_data)
        else:
            self.order_text = order_data.strip()
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

    def get_order(self):
        return self.order_text

    def refresh(self):
        self.hidden_rows = []
        self.relation_cache = {}
        self.refreshed = True

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
            elif meta.get("control", "") in ["button", "widget"]:
                continue
            elif meta.get("control", "") == "form":
                for meta2 in meta.get("widget", "").controls:
                    if meta2.get("column", "").startswith("/") or meta2.get("nogrid"):
                        continue
                    self.add_column(meta2)
                continue
            self.add_column(meta)

    def add_column(self, meta):
        if not meta.get("control"):
            meta["control"] = "line"

        meta = q2app.Q2Controls.validate(meta)
        self.columns.append(meta["column"])
        self.headers.append(meta["gridlabel" if meta.get("gridlabel") else "label"])
        if meta.get("relation"):
            self.alignments.append("7")
        else:
            self.alignments.append(meta.get("alignment", "7"))
        self.meta.append(meta)

    def get_record(self, row):
        if row < 0 or row > len(self.records) - 1:
            return {}
        if self.use_proxy:
            return self.records[self.proxy_records[row]]
        else:
            return self.records[row]

    def refresh_record(self, row):
        pass

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
        if related is None or related == {}:
            related = ""
        if do_not_show_value:
            return f"{related}"
        else:
            return f"{value},{related}"

    def get_related(self, to_table, filter, related):
        return "get_related"

    def data(self, row, col, role="display", skip_format=False):
        if role == "display":
            col_name = self.columns[col]
            value = self.get_record(row).get(col_name, "")
            meta = self.meta[col]
            strign_for_num = False
            if meta.get("relation"):
                value = self._get_related(value, meta)
                skip_format = True
            elif meta.get("show"):
                value = meta.get("show")(mode="grid", row=row)
            elif strign_for_num := self.is_strign_for_num(meta):
                if num(value) == 0:
                    value = 1
                tmp_list = meta.get("pic").split(";")
                value = tmp_list[int(num(value)) - 1] if int(num(value)) - 1 < len(tmp_list) else "****"
            elif meta["datatype"] == "date":
                try:
                    value = datetime.datetime.strptime(value, "%Y-%m-%d").strftime(q2app.DATE_FORMAT_STRING)
                except Exception:
                    value = ""

            if not strign_for_num and meta.get("num") and skip_format is False:  # Numeric value
                if num(value) == 0:  # do not show zero
                    value = ""
                elif meta.get("pic") == "F":  # financial format
                    format_string = q2app.FINANCIAL_FORMAT % meta.get("datadec", 0)
                    value = format_string.format(num(value)).replace(",", " ")

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
        model_value = None
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
            if cond_result and model_value:
                rez.append([x, model_value])
        return rez

    def unique_column_values(self, column):
        uniq_values = set()
        for row in range(self.row_count()):
            if self.is_hidden(row) and column not in self.columns_filter_values:
                continue
            uniq_values.add(self.data(row, column))
        uniq_values = {
            index: {"v": value, "c": True} for index, value in enumerate(sorted(list(uniq_values)))
        }
        return uniq_values

    def data_export(self, file):
        pass

    def data_import(self, file):
        pass

    def seek_row(self, row_dict):
        if self.row_count() > 10000:
            return 0
        pk = self.get_meta_primary_key()
        if pk and pk in row_dict:
            for row_number in range(self.row_count()):
                rec_dic = self.get_record(row_number)
                if str(row_dict[pk]) == rec_dic[pk]:
                    return row_number
        else:
            for row_number in range(self.row_count()):
                rec_dic = self.get_record(row_number)
                found = 1
                for colname in row_dict:
                    if row_dict[colname] != rec_dic[colname]:
                        found = 0
                        break
                if found:
                    return row_number
        return 0

    def get_meta_primary_key(self):
        for x in self.q2_form.controls:
            if x["pk"]:
                return x["column"]

    def get_uniq_value(self, column, value):
        pass

    def get_next_sequence(self, column, start_value=0):
        pass

    def info(self):
        info = {}
        info["table"] = self.get_table_name()
        info["row_count"] = self.row_count()
        info["order"] = self.get_order()
        info["where"] = self.get_where()
        info["columns"] = self.columns
        return info


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


class Q2CursorModel(Q2Model):
    def __init__(self, cursor: Q2Cursor = None):
        super().__init__()
        self.last_order_text = ""

        self.readonly = False
        self.delete_enabled = False
        self.insert_enabled = False
        self.update_enabled = False
        self.set_cursor(cursor)
        self.where_text = self.cursor.where
        self.order_text = self.cursor.order
        self.check_q2_colors()

    def set_cursor(self, cursor):
        self.cursor: Q2Cursor = cursor
        self.original_sql = self.cursor.sql
        last_order_text, last_order_text = self.last_order_text, ""
        if self.last_order_text:
            self.set_order(last_order_text)
        self.readonly = False if self.cursor.table_name else True
        # print(self.cursor.table_name, "--", self.cursor.sql, self.readonly)

    def get_table_name(self):
        if self.cursor.table_name:
            return self.cursor.table_name
        else:
            return self.cursor.sql

    def row_count(self):
        return self.cursor.row_count()

    def get_record(self, row):
        return self.cursor.record(row)

    def refresh_record(self, row):
        self.cursor.refresh_record(row)

    def seek_row(self, row_dict):
        if self.row_count() > 10000:
            return 0
        if self.cursor.table_name:
            return self.cursor.seek_primary_key_row(row_dict)
        else:
            return super().seek_row(row_dict)

    def refresh(self):
        super().refresh()
        self.cursor.refresh()
        self.check_q2_colors()

    def check_q2_colors(self):
        self.q2_bcolors = {}
        self.q2_fcolors = {}
        if self.row_count():
            self.q2_bcolor = "q2_bcolor" in (rec := self.get_record(0))
            self.q2_fcolor = "q2_fcolor" in rec

    def get_uniq_value(self, column, value):
        return self.cursor.get_uniq_value(column, value)

    def get_next_sequence(self, column, start_value=0):
        return self.cursor.get_next_sequence(column, start_value)

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
        if self.cursor.update(record, refresh=False):
            if refresh:
                self.refresh()
            return True
        else:
            self.set_data_error(f"{self.cursor.last_sql_error()}<br>{self.cursor.last_sql()}")
            return False

    def insert(self, record: dict, current_row=0, refresh=True):
        self.set_data_error()
        if self.cursor.insert(record, refresh=False):
            if refresh:
                self.refresh()
            return True
        else:
            self.set_data_error(self.cursor.last_sql_error())
            return False

    def get_related(self, to_table, filter, related):
        db: Q2Db = self.cursor.q2_db
        return db.get(to_table, filter, related)

    def set_order(self, order_data, direction=None):
        super().set_order(order_data=order_data)
        if self.order_text == "":
            return self
        if direction == "AZ":
            pass
        elif direction == "ZA":
            self.order_text += " desc"
        elif self.order_text in self.last_order_text and "desc" not in self.last_order_text:
            self.order_text += " desc"

        if self.cursor.table_name:
            self.cursor.set_order(self.order_text)
        else:
            self.cursor.sql = f"select * from ({self.original_sql}) qq order by {self.order_text}"
            self.last_order_text = order_data
        self.last_order_text = self.order_text
        return self

    def set_where(self, where_text=""):
        self.cursor.set_where(where_text)
        self.refresh()
        return super().set_where(where_text)

    def add_column(self, meta):
        """update metadata from db"""
        db: Q2Db = self.cursor.q2_db
        db_meta = db.db_schema.get_schema_table_attr(self.cursor.table_name, meta["column"])
        # meta["pk"] = db_meta.get("pk", "")
        meta["datatype"] = db_meta.get("datatype", meta["datatype"])
        if num(meta["datalen"]) < num(db_meta.get("datalen", 10)):
            meta["datalen"] = int(num(db_meta.get("datalen", 10)))
        if "datadec" not in meta:
            meta["datadec"] = int(num(db_meta.get("datadec", 2)))
        return super().add_column(meta)

    def before_export(self, write_to, records):
        if self.hidden_rows:
            new_records = []
            for row in range(len(records)):
                if not self.is_hidden(row):
                    new_records.append(records[row])
            records = new_records
        return write_to, records

    def data_export(self, file: str, tick_callback=None):
        if self.cursor.before_export != self.before_export:
            self.cursor.before_export = self.before_export
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

    def get_records(self):
        return self.cursor.records()

    def check_db_column(self, column):
        db: Q2Db = self.cursor.q2_db
        return db.db_schema.get_schema_table_attr(self.cursor.table_name, column)

    def set_hidden_row_status(self, status=""):
        self.cursor.set_hidden_row_status(status)
