import asyncio
from aiotg import Bot, Chat
from domain_info_collector import fetch_domains_info
from db import db, get_domain, get_domains_expire_in, delete_by_domain_name

with open('token.secret', 'r') as f:
    token = f.read()

bot = Bot(token)


@bot.command(r"/check +")
async def check(chat: Chat, match):
    domain_name = chat.message['text'].split("check ")[-1]
    domain = get_domain(domain_name)
    if domain:
        return await chat.send_text(f"{domain['domain']} истечёт {domain['paid-till']}.")
    else:
        return await chat.send_text(f"Домен {domain_name} не найден.")


@bot.command(r"/add +")
async def add_domain(chat: Chat, match):
    domain_name = chat.message['text'].split("add ")[-1]
    if get_domain(domain_name):
        return await chat.send_text("Домен уже добавлен.")
    fetched_domains = await fetch_domains_info([domain_name])
    if fetched_domains:
        fetched_domain = fetched_domains[-1]
        db.insert(fetched_domain)
        return await chat.send_text(f"Домен {fetched_domain['domain']} успешно добавлен.")
    else:
        return await chat.send_text(f"Не удалось собрать информацию о {domain_name}.")


@bot.command(r"/add_domains +")
async def add_domain(chat: Chat, match):
    domain_names = set(chat.message['text'].split("/add_domains ")[-1].strip().
                       replace('\n', '').split(','))
    for domain_name in domain_names.copy():
        if get_domain(domain_name):
            await chat.send_text(f"Домен {domain_name} уже добавлен и будет пропущен.")
            domain_names.remove(domain_name)

    fetched_domains = await fetch_domains_info(domain_names)
    if fetched_domains:
        for fetched_domain in fetched_domains:
            if fetched_domain is not None:
                db.insert(fetched_domain)
            fetched_names = "\n".join((d['domain'] for d in fetched_domains if d is not None))
        return await chat.send_text(f"Успешно добавлены: \n{fetched_names}")
    else:
        return await chat.send_text(f"Не удалось собрать информацию о доменах.")


@bot.command(r"/delete +")
async def delete_domain(chat: Chat, match):
    domain_name = chat.message['text'].split("delete ")[-1]
    delete_by_domain_name(domain_name)
    return await chat.send_text(f"Домен {domain_name} удалён.")


@bot.command(r"/check [0-9]+")
async def check_domains(chat: Chat, match):
    days = int(chat.message['text'].split('check_domains ')[-1])
    domains = get_domains_expire_in(days)
    domains_names = "\n".join([f"{domain['domain']} истекает {domain['paid-till']}" for domain in domains])
    return await chat.send_text(domains_names)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.loop())
