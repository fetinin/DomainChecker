import asyncio
from aiotg import Bot, Chat
from main import fetch_domains_info
from db import db, get_domain

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
    # chat.send_text(domain_name)
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
    pass


@bot.command(r"update +")
async def check(chat: Chat, match):
    pass

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.loop())
