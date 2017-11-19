import datetime
import pathlib


ROOT = pathlib.Path(__file__).parent
BOT_TOKEN_FILE = ROOT / 'token.secret'
DATABASE_FILE = ROOT / 'db.json'

NOTIFICATIONS_INTERVAL = int(datetime.timedelta(days=14).total_seconds())
DOMAIN_EXPIRATION_DAYS = 30
