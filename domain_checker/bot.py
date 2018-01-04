import asyncio

from aiotg import Bot, Chat

import db
from domain_info_collector import fetch_domains_info
from settings import BOT_TOKEN

bot = Bot(BOT_TOKEN)


def _extract_message(chat: Chat, command_name: str) -> str:
    """Get rid of command from chat message."""
    msg = chat.message['text'].split(command_name)[-1]
    return msg.strip(" ").strip("\n")


@bot.command(r"/check +")
async def check(chat: Chat, match):
    domain_name = _extract_message(chat, "/check ")
    domain = db.get_domain(domain_name)
    if domain:
        formatted_domain_info = "\n".join((f"{k}: {v}" for k, v in domain.items()))
        return await chat.send_text(formatted_domain_info)
    else:
        return await chat.send_text(f"Домен {domain_name} не найден.")


@bot.command(r"/add_domain +")
async def add_domain(chat: Chat, match):
    domain_name = _extract_message(chat, "/add_domain ")
    if db.get_domain(domain_name):
        return await chat.send_text("Домен уже добавлен.")
    fetched_domains = await fetch_domains_info([domain_name])
    if fetched_domains:
        fetched_domain = fetched_domains[-1]
        db.add_domain(fetched_domain)
        return await chat.send_text(f"Домен {fetched_domain['domain']} успешно добавлен.")
    else:
        return await chat.send_text(f"Не удалось собрать информацию о {domain_name}.")


@bot.command(r"/update_domain +")
async def update_domain(chat: Chat, match):
    domain_name = _extract_message(chat, "update_domain ")
    if not db.get_domain(domain_name):
        return await chat.send_text("Добавьте домен командой /add_domains.")
    fetched_domains = await fetch_domains_info([domain_name])
    if fetched_domains:
        fetched_domain = fetched_domains[-1]
        db.update_domain(fetched_domain)
        return await chat.send_text(f"Домен {fetched_domain['domain']} успешно обновлён.")
    else:
        return await chat.send_text(f"Не удалось собрать информацию о {domain_name}.")


@bot.command(r"/add_domains +")
async def add_domains(chat: Chat, match):
    domain_names = {
        domain.strip().replace('\n', '') for domain in
        _extract_message(chat, '/add_domains').split(',')
    }
    for domain_name in domain_names.copy():
        if db.get_domain(domain_name):
            await chat.send_text(f"Домен {domain_name} уже добавлен и будет пропущен.")
            domain_names.remove(domain_name)

    fetched_domains = await fetch_domains_info(domain_names)
    if fetched_domains:
        for fetched_domain in fetched_domains:
            db.add_domain(fetched_domain)
            fetched_names = "\n".join((d['domain'] for d in fetched_domains))
        return await chat.send_text(f"Успешно добавлены: \n{fetched_names}")
    else:
        return await chat.send_text(f"Не удалось собрать информацию о доменах.")


@bot.command(r"/delete_domain +")
async def delete_domain(chat: Chat, match):
    domain_name = _extract_message(chat, "/delete_domain ")
    db.delete_by_domain_name(domain_name)
    return await chat.send_text(f"Домен {domain_name} удалён.")


@bot.command(r"/check_domains [0-9]+")
async def check_domains(chat: Chat, match):
    days = int(_extract_message(chat, 'check_domains '))
    domains = db.get_domains_expire_in(days)
    msg = "\n".join([f"{domain['domain']} истекает {domain['expiration_date']}" for domain in domains])
    if not msg:
        msg = "Все домены в порядке."
    return await chat.send_text(msg)


@bot.command(r"/subscribe")
async def subscribe(chat: Chat, match):
    user = {'chat_id': chat.id, 'name': str(chat.sender)}
    db.subscribe_user(user)
    return await chat.send_text("Буду переодически оповещать вас об истекающих доменах.")


@bot.command(r"/unsubscribe")
async def unsubscribe(chat: Chat, match):
    db.unsubscribe_user(chat.id)
    return await chat.send_text("Отписали вас от рассылки.")


@bot.command(r'/ping')
async def pong(chat: Chat, match):
    chat.send_text('Pong 🏓')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.loop())
