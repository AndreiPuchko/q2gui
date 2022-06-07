#    Copyright (C) 2021 Andrei Puchko
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

from decimal import Decimal
import datetime


def is_sub_list(sublst, lst):
    return len([x for x in sublst if x in lst]) == len(sublst)


def int_(toInt):
    try:
        return int(f"{toInt}")
    except Exception:
        return int(num(toInt))

def float_(toFloat):
    try:
        return float(f"{toFloat}")
    except Exception:
        return float(num(toFloat))


def num(tonum):
    try:
        return Decimal(f"{tonum}")
    except Exception:
        return 0


def today():
    return datetime.date.today()


class dotdict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def set_dict_default(_dict, _key, _value):
    """set only key does not exist"""
    
    if not _dict.get(_key):
        _dict[_key] = _value
