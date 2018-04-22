import datetime
from itertools import filterfalse, tee


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
