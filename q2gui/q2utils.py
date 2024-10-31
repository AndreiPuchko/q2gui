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
import hashlib
import secrets
import binascii
import re


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


def nums(number_str):
    number_str = f"{number_str}"
    decimal_sep_pos = max(number_str.rfind(","), number_str.rfind("."))

    if decimal_sep_pos == -1:
        return number_str

    integer_part = number_str[:decimal_sep_pos]
    decimal_part = number_str[decimal_sep_pos + 1:]

    integer_part = re.sub(r"[^0-9-]", "", integer_part)
    integer_part = re.sub(r"(?<!^)-", "", integer_part)

    formatted_number = f"{integer_part}.{decimal_part}"
    return formatted_number


def today():
    return f"{datetime.date.today()}"


class dotdict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def set_dict_default(_dict, _key, _value):
    """set only key does not exist"""

    if not _dict.get(_key):
        _dict[_key] = _value


class Q2Crypto:
    def __init__(self, pin, lenght=256):
        self._pin = pin
        self.pin = [x for x in hashlib.shake_256(self._pin.encode()).hexdigest(lenght // 2)]

    def encrypt(self, text):
        if not isinstance(text, str):
            return None
        text = binascii.hexlify((text + chr(1) + self._pin).encode())
        step = max(len(self.pin) // max(len(text), 1), 1)
        crypted = self.pin[:]
        r = 0
        for x in range(len(text)):
            r += secrets.randbelow(step) + 1
            if r >= len(crypted):
                raise BaseException("Cryptgraphy Error - given text to long")
            while True:
                if chr(text[x]) != crypted[r]:
                    break
                else:
                    r += 1
            crypted[r] = chr(text[x])
        return "".join(crypted)

    def _decrypt(self, crypted):
        if len(crypted) != len(self.pin):
            return None
        rez = []
        for x in range(len(self.pin)):
            if self.pin[x] != crypted[x]:
                rez.append(crypted[x])
        rez = ("".join(rez)).encode()
        try:
            return binascii.unhexlify(rez).decode()
        except Exception as errow:
            return None

    def decrypt(self, crypted):
        if not isinstance(crypted, str):
            return None
        rez = self._decrypt(crypted)
        if rez is not None:
            if rez.endswith(chr(1) + self._pin):
                rez = rez[: -(len(self._pin) + 1)]
            else:
                return None
        return rez

    def check_pin(self, crypted):
        if not isinstance(crypted, str):
            return None
        rez = self._decrypt(crypted)
        if rez is not None:
            if rez.endswith(chr(1) + self._pin):
                return True
            else:
                return None
        return rez
