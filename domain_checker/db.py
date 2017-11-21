from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import JSON
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func as sql_func

engine = create_engine('postgresql+psycopg2://postgres:123456@172.17.0.2/domain_checker')
Session = sessionmaker(bind=engine)
Base = declarative_base()

session = Session()


class Domain(Base):
    __tablename__ = 'domains'

    id = Column(Integer, primary_key=True)
    domain_name = Column(String)
    registration_date = Column(Date)
    expiration_date = Column(Date)
    status = Column(String)
    last_update = Column(Date, default=sql_func.now())
    extra_info = Column(JSON)


class Subscriber(Base):
    __tablename__ = 'subscribers'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    chat_id = Column(Integer)
    subscribed = Column(Boolean)









#
# domains_db = TinyDB(str(DATABASE_FILE), default_table='domains')
# users_db = TinyDB(str(DATABASE_FILE), default_table='users')
#
# Domain = Query()
# User = Query()
#
#
# def get_domain(domain_name: str) -> dict:
#     return domains_db.get(Domain.domain == domain_name)
#
#
# def get_domains_expire_in(days):
#
#     def date_comparator(val: str, dayz: int) -> bool:
#         expiration_date = datetime.datetime.strptime(val, "%Y-%M-%d")
#         diff = datetime.datetime.today() - expiration_date
#         return diff.days > dayz
#
#     return domains_db.search(Domain['expiration_date'].test(date_comparator, days))
#
#
# def delete_by_domain_name(domain_name: str) -> None:
#     domains_db.remove(Domain.domain == domain_name)
#
#
# def add_domain(domain_data: dict):
#     return domains_db.insert(domain_data)
#
#
# def update_domain(domain_data: dict):
#     return domains_db.update(domain_data, Domain.domain == domain_data['domain'])
#
#
# def get_all_users():
#     return users_db.all()
#
#
# def add_user(user_data: dict):
#     user_data['subscribed'] = True
#     return users_db.upsert(user_data, User.chat_id == user_data['chat_id'])
#
#
# def unsubscribe_user(chat_id: str):
#     user = users_db.get(User.chat_id == chat_id)
#     user['subscribed'] = False
#     return users_db.update(user, doc_ids=[user.doc_id])
#
#
# def get_subscribed_users():
#     return users_db.search(User.subscribed == True)
