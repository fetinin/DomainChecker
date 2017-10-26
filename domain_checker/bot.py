from aiotg import Bot, Chat, asyncio

with open('token.secret', 'r') as f:
    token = f.read()

bot = Bot(token)


@bot.command(r"check")
async def check(chat: Chat, match):
    url = "http://google.com"
    async with bot.session.get(url) as s:
        info = await s.text()
        await chat.send_text(info[:15])


@bot.command(r"check")
async def add_domain(chat: Chat, match):
    pass


@bot.command(r"check")
async def delete_domain(chat: Chat, match):
    pass


@bot.command(r"check")
async def check(chat: Chat, match):
    pass

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.loop())
