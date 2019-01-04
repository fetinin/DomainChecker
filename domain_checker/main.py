import asyncio
import datetime
import logging

from domain_checker.bot import bot
from domain_checker.db import (
    get_domains_expire_in,
    get_subscribed_users,
    list_domains,
    update_domain,
    update_user_notification_time,
)
from domain_checker.domain_info_collector import fetch_domains_info
from domain_checker.settings import DOMAIN_EXPIRATION_DAYS, NOTIFICATIONS_INTERVAL

SECONDS_IN_ONE_DAY = 86400

logger = logging.getLogger(__name__)


async def notify_about_expired_domains():
    while True:
        logger.info("Checking if there is anyone to notify about expired domains.")

        expiring_domains = get_domains_expire_in(DOMAIN_EXPIRATION_DAYS)
        users_to_notify = get_subscribed_users()
        expiring_domains_msg = "\n".join(
            [
                f"{domain['domain']} истекает {domain['expiration_date']}"
                for domain in expiring_domains
            ]
        )
        usr_msg = (
            f"Следующие домены истекают в течение {DOMAIN_EXPIRATION_DAYS} дней:\n "
            f"{expiring_domains_msg}."
        )
        logger.info(f"Found {len(users_to_notify)} users to notify.")
        for user in users_to_notify:
            since_last_update = datetime.datetime.now() - user["last_informed"]
            logger.info(
                f"{user['name']} was last notified {since_last_update.days} days ago."
            )
            if since_last_update.days > NOTIFICATIONS_INTERVAL:
                logger.info(f"Notifying {user['name']}.")
                bot.send_message(user["chat_id"], usr_msg)
                update_user_notification_time(user["chat_id"])
        await asyncio.sleep(SECONDS_IN_ONE_DAY)


async def actualize_domains():
    def seconds_till(date: datetime.datetime) -> float:
        return (date - datetime.datetime.now()).total_seconds()

    while True:
        with open("./actualizer_time.tmp", "a+") as fh:
            fh.seek(0)
            next_check_time = fh.readline()

        if next_check_time:
            next_check = datetime.datetime.fromordinal(int(next_check_time))
            sec_till_next_month = seconds_till(next_check)
            if sec_till_next_month > 0:
                logger.info(f"Next info actualize will be {next_check}.")
                await asyncio.sleep(sec_till_next_month)
                continue

        domains_names = [d["domain"] for d in list_domains()]
        domains_info = await fetch_domains_info(domains_names)
        for domain in domains_info:
            logger.info(f"Updating {domain['domain']} info.")
            update_domain(domain)

        next_month = datetime.datetime.now() + datetime.timedelta(days=30)

        with open("./actualizer_time.tmp", "w") as fh:
            fh.write(str(next_month.toordinal()))

        logger.info(f"Next info actualize will be {next_month}.")
        await asyncio.sleep(seconds_till(next_month))


async def main():
    tasks = [bot.loop(), notify_about_expired_domains()]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        logger.info("Bot started...")
        asyncio.run(main(), debug=True)
    except KeyboardInterrupt:
        pass
