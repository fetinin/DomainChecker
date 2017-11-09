from tinydb import TinyDB, Query

db = TinyDB('db.json')
Domain = Query()


def get_domain(domain_name: str) -> dict:
    return db.get(Domain.domain == domain_name)
