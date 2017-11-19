import asyncio
import datetime

from bot import bot
from db import get_domains_expire_in, get_subscribed_users


NOTIFICATION_INTERVAL = int(datetime.timedelta(days=14).total_seconds())
DOMAIN_EXPIRATION_DAYS = 30


async def notify_about_expired_domains():
    while True:
        expiring_domains = get_domains_expire_in(DOMAIN_EXPIRATION_DAYS)
        users_to_notify = get_subscribed_users()
        expiring_domains_msg = "\n".join(
            [f"{domain['domain']} истекает {domain['expiration_date']}"
             for domain in expiring_domains]
        )
        usr_msg = f"Следующие домены истекают в течение {DOMAIN_EXPIRATION_DAYS} дней:\n" + expiring_domains_msg
        for user in users_to_notify:
            bot.send_message(user['chat_id'], usr_msg)

        await asyncio.sleep(NOTIFICATION_INTERVAL)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(notify_about_expired_domains(), loop=loop)
    loop.create_task(bot.loop())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
