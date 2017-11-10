import datetime
from tinydb import TinyDB, Query

db = TinyDB('db.json')
Domain = Query()


def get_domain(domain_name: str) -> dict:
    return db.get(Domain.domain == domain_name)


def get_domains_expire_in(days):

    def date_comparator(val: str, dayz: int) -> bool:
        expiration_date = datetime.datetime.strptime(val, "%Y-%M-%d")
        diff = datetime.datetime.today() - expiration_date
        return diff.days > dayz

    return db.search(Domain['paid-till'].test(date_comparator, days))


def delete_by_domain_name(domain_name: str) -> None:
    db.remove(Domain.domain == domain_name)
