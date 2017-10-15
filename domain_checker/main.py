import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup

from responses import responses as bulk_responses


async def bulk_resp(key):
    return bulk_responses[key]


async def fetch(url: str, session: ClientSession) -> str:
    return await bulk_resp(url.split('whois/')[-1])
    # async with session.get(url) as response:
    #     return await response.text()


def extract_domain_info(response):
    soup = BeautifulSoup(response, 'html.parser')
    domain_data = soup.find('div', {'class': 'df-block-raw'})
    assert domain_data, "No domain data :(C"
    print(domain_data.text)


async def run(domains: list):
    url = "https://www.whois.com/whois/{}"
    tasks = []

    # Fetch all responses within one Client session,
    # keep connection alive for all requests.
    async with ClientSession() as session:
        for domain in domains:
            task = asyncio.ensure_future(fetch(url.format(domain), session))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        # you now have all response bodies in this variable
        for response in responses:
            extract_domain_info(response)


def print_responses(result):
    print(result)


loop = asyncio.get_event_loop()
future = asyncio.ensure_future(run(['skavo.ru', 'terminal-firm.ru']))
loop.run_until_complete(future)
