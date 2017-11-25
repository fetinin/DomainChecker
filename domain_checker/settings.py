import os
import datetime
import pathlib


def _get_token():
    try:
        with BOT_TOKEN_FILE.open() as f:
            token = f.read()
    except FileNotFoundError:
        token = os.environ.get("BOT_TOKEN", "")
    return token


ROOT = pathlib.Path(__file__).parent

BOT_TOKEN_FILE = ROOT / 'token.secret'
BOT_TOKEN = _get_token()

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql+psycopg2://postgres:123456@172.17.0.2/domain_checker')

_notification_days = os.environ.get('NOTIFICATIONS_INTERVAL', 14)
NOTIFICATIONS_INTERVAL = int(datetime.timedelta(days=_notification_days).total_seconds())
DOMAIN_EXPIRATION_DAYS = os.environ.get('DOMAIN_EXPIRATION_DAYS', 30)
