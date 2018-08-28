import datetime
import logging
import os
import pathlib


def _get_token():
    try:
        with BOT_TOKEN_FILE.open() as f:
            token = f.read()
    except FileNotFoundError:
        token = os.environ.get("BOT_TOKEN", "")
    return token


ROOT = pathlib.Path(__file__).parent

BOT_TOKEN_FILE = ROOT / "token.secret"
BOT_TOKEN = _get_token()

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:O-nGNTY&235212asef@localhost/domain_checker",
)

_notification_days = os.environ.get("NOTIFICATIONS_INTERVAL", 14)
NOTIFICATIONS_INTERVAL = datetime.timedelta(days=_notification_days).days
DOMAIN_EXPIRATION_DAYS = os.environ.get("DOMAIN_EXPIRATION_DAYS", 30)
API_KEY = os.environ.get("API_KEY", "")

logging.basicConfig(
    format="%(asctime)s |%(levelname)s| %(message)s", level=logging.INFO
)
