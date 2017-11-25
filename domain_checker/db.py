import datetime
from operator import setitem

from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func as sql_func
from sqlalchemy.types import JSON

from settings import DATABASE_URL

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

session = Session()


class Domain(Base):
    __tablename__ = 'domains'

    id = Column(Integer, primary_key=True)
    domain = Column(String, unique=True)
    name_servers = Column(String)
    registration_date = Column(Date)
    expiration_date = Column(Date)
    status = Column(String)
    last_update = Column(DateTime, default=sql_func.now(), onupdate=sql_func.now())
    extra_info = Column(JSON)

    @classmethod
    def get_by_name(cls, domain_name: str):
        return session.query(cls).filter(cls.domain == domain_name).one_or_none()

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "name_servers": self.name_servers,
            "registration_date": self.registration_date.strftime("%d-%m-%Y"),
            "expiration_date": self.expiration_date.strftime("%d-%m-%Y"),
            "status": self.status,
            "last_update": self.last_update,
            "extra_info": self.extra_info,
        }


class Subscriber(Base):
    __tablename__ = 'subscribers'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    chat_id = Column(Integer)
    subscribed = Column(Boolean, default=True)

    @classmethod
    def get_by_chat_id(cls, chat_id: str):
        return session.query(cls).filter(cls.chat_id == chat_id).one_or_none()

    def to_dict(self):
        return {
            'name': self.name,
            'chat_id': self.chat_id,
            'subscribed': self.subscribed,
        }


def _normalize_domain_data(new_attrs: dict) -> dict:
    allowed_keys = {'domain', 'registration_date',
                    'expiration_date', 'status', 'name_servers'}
    kwargs = {'extra_info': {}}
    for k, v in new_attrs.items():
        setitem(kwargs, k, v) if k in allowed_keys else setitem(kwargs['extra_info'], k, v)
    return kwargs


def _normalize_user_data(new_attrs: dict) -> dict:
    allowed_keys = {'name', 'chat_id', 'subscribed'}
    return {k: v for k, v in new_attrs.items() if k in allowed_keys}


def get_domain(domain_name: str) -> dict or None:
    domain = Domain.get_by_name(domain_name)
    if domain:
        return domain.to_dict()


def get_domains_expire_in(days: int):
    exp = (datetime.datetime.today() + datetime.timedelta(days=days)).date()
    domains = session.query(Domain).filter(Domain.expiration_date <= exp).all()
    return [domain.to_dict() for domain in domains]


def delete_by_domain_name(domain_name: str) -> None:
    domain = Domain.get_by_name(domain_name)
    if domain:
        session.delete(domain)
        session.commit()


def add_domain(domain_data: dict) -> None:
    session.add(Domain(**_normalize_domain_data(domain_data)))
    session.commit()


def update_domain(domain_data: dict):
    domain_name = domain_data['domain']
    domain = Domain.get_by_name(domain_name)
    if domain:
        for k, v in _normalize_domain_data(domain_data).items():
            setattr(domain, k, v)
        session.add(domain)
        session.commit()
        return True
    return False


def add_user(user_data: dict):
    session.add(Subscriber(**_normalize_user_data(user_data)))
    session.commit()


def subscribe_user(user_data: dict):
    user_data = _normalize_user_data(user_data)
    user = Subscriber.get_by_chat_id(user_data['chat_id'])
    if user and not user.subscribed:
        user.subscribed = True
        session.add(user)
        session.commit()
    else:
        add_user(user_data)


def unsubscribe_user(chat_id: str):
    user = Subscriber.get_by_chat_id(chat_id)
    if user:
        user.subscribed = False
        session.add(user)
        session.commit()
        return True
    return False


def get_subscribed_users() -> [dict]:
    subs = session.query(Subscriber).filter(Subscriber.subscribed == True).all()
    return [sub.to_dict() for sub in subs]
