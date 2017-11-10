import asyncio
from aiotg import Bot, Chat
from main import fetch_domains_info
from db import db, get_domain, get_domains_expire_in, delete_by_domain_name

with open('token.secret', 'r') as f:
    token = f.read()

bot = Bot(token)


@bot.command(r"check +")
async def check(chat: Chat, match):
    domain_name = chat.message['text'].split("check ")[-1]
    domain = get_domain(domain_name)
    if domain:
        return await chat.send_text(f"{domain['domain']} will expire {domain['paid-till']}.")
    else:
        return await chat.send_text(f"No such domain found.")


@bot.command(r"add +")
async def add_domain(chat: Chat, match):
    domain_name = chat.message['text'].split("add ")[-1]
    if get_domain(domain_name):
        return await chat.send_text("Domain already registered")
    fetched_domains = await fetch_domains_info([domain_name])
    if fetched_domains:
        fetched_domain = fetched_domains[-1]
        db.insert(fetched_domain)
        return await chat.send_text(f"Successfully added {fetched_domain['domain']}")
    else:
        return await chat.send_text(f"Failed to fetch {domain_name}.")


@bot.command(r"delete +")
async def delete_domain(chat: Chat, match):
    domain_name = chat.message['text'].split("delete ")[-1]
    delete_by_domain_name(domain_name)
    return await chat.send_text(f"Removed {domain_name}")


@bot.command(r"check_domains [0-9]+")
async def check_domains(chat: Chat, match):
    days = int(chat.message['text'].split('check_domains ')[-1])
    domains = get_domains_expire_in(days)
    domains_names = "\n".join([f"{domain['domain']} истекает {domain['paid-till']}" for domain in domains])
    return await chat.send_text(domains_names)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.loop())
