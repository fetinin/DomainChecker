import datetime
import os
from itertools import filterfalse, tee
from typing import get_type_hints


def partition(pred, iterable):
    """
    Use a predicate to partition entries into false entries and true entries
    :example:
      partition(is_odd, range(10)) --> 0 2 4 6 8   and  1 3 5 7 9
    """
    t1, t2 = tee(iterable)
    return filter(pred, t1), filterfalse(pred, t2)


def format_date(date: datetime.date, fmt: str):
    if not date:
        return ""

    return date.strftime(fmt)


class SettingsParamMissing(Exception):
    pass


class SettingsMeta(type):
    def __new__(mcs, name, bases, namespace, app_name="", reader=os.environ):
        cls = super().__new__(mcs, name, bases, namespace)

        for var_name, type_cls in get_type_hints(cls).items():
            key_name = f"{app_name}_{var_name}" if app_name else var_name
            try:
                value = type_cls(reader[key_name])
            # todo: handle conversion error
            except KeyError:
                if var_name not in namespace:
                    raise SettingsParamMissing(
                        f"{key_name} is required but not found in {reader}."
                    ) from None
            else:
                setattr(cls, var_name, value)

        return cls
