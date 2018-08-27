import asyncio
import logging

import datetime

from bot import bot
from db import (
    get_domains_expire_in,
    get_subscribed_users,
    update_user_notification_time,
)
from settings import NOTIFICATIONS_INTERVAL, DOMAIN_EXPIRATION_DAYS

SECONDS_IN_ONE_DAY = 86400

logger = logging.getLogger(__name__)


async def notify_about_expired_domains():
    while True:
        expiring_domains = get_domains_expire_in(DOMAIN_EXPIRATION_DAYS)
        users_to_notify = get_subscribed_users()
        expiring_domains_msg = "\n".join(
            [
                f"{domain['domain']} истекает {domain['expiration_date']}"
                for domain in expiring_domains
            ]
        )
        usr_msg = f"Следующие домены истекают в течение {DOMAIN_EXPIRATION_DAYS} дней:\n {expiring_domains_msg}"
        for user in users_to_notify:
            days_since_last_update = (
                datetime.datetime.now() - user["last_informed"]
            ).days
            if days_since_last_update > NOTIFICATIONS_INTERVAL:
                logger.info(f"Notifying {user['name']}.")
                bot.send_message(user["chat_id"], usr_msg)
                update_user_notification_time(user["chat_id"])
        await asyncio.sleep(SECONDS_IN_ONE_DAY)


async def actualize_domains():
    pass


async def main():
    tasks = [bot.loop(), notify_about_expired_domains(), actualize_domains()]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        logger.info("Bot started...")
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
