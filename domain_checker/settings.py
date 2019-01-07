from __future__ import annotations

import logging

from .helpers import SettingsMeta


class Settings(metaclass=SettingsMeta, app_name="DOMAIN_CHECKER"):
    API_KEY: str
    BOT_TOKEN: str
    DATABASE_URL: str = (
        "postgresql+psycopg2://postgres:O-nGNTY&235212asef@localhost/domain_checker"
    )
    NOTIFICATIONS_INTERVAL: int = 14
    DOMAIN_EXPIRATION_DAYS: int = 30


logging.basicConfig(
    format="%(asctime)s |%(levelname)s| %(message)s", level=logging.INFO
)
