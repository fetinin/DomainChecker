import asyncio
from aiohttp import ClientSession
from fnmatch import fnmatch
from bs4 import BeautifulSoup
import maya

from responses import responses as bulk_responses


def bulk_resp(key):
    return bulk_responses[key]

i = 0

async def fetch(url: str, session: ClientSession) -> str:
    global i
    if i == 0:
        i += 1
        raise AssertionError
    return bulk_resp(url.split('whois/')[-1])
    # async with session.get(url) as response:
    #     return await response.text()


def extract_domain_info(response):
    soup = BeautifulSoup(response, 'html.parser')
    parsed_text = soup.find('div', {'class': 'df-block-raw'}).get_text()
    assert parsed_text, "No domain data :`("

    info_lines = (
        line.strip() for line in parsed_text.splitlines()
        if fnmatch(line, '*: *')
    )
    domain_info = {
        k: v.strip() for k, v in (line.split(':', 1) for line in info_lines)
    }

    maya_date = maya.parse(domain_info['paid-till'])

    domain_info['slang_exp_date'] = (f"{maya_date.slang_time()}, "
                                     f"{maya_date.slang_date()}")
    domain_info['paid-till'] = maya_date.datetime(
        to_timezone='Europe/Moscow',
        naive=True
    )

    print(f"{domain_info['domain']} paid till "
          f"{domain_info['paid-till'].strftime('%d-%m-%Y')}.")
    print(f"{domain_info['domain']} will expire in "
          f"{domain_info['slang_exp_date']}.")


async def run(domains: list):
    url = "https://www.whois.com/whois/{}"
    tasks = []

    # Fetch all responses within one Client session,
    # keep connection alive for all requests.
    async with ClientSession() as session:
        for domain in domains:
            task = asyncio.ensure_future(fetch(url.format(domain), session))
            tasks.append(task)

        responses = await asyncio.gather(*tasks, return_exceptions=True)
        # you now have all response bodies in this variable
        responses = filter(lambda x: not isinstance(x, Exception), responses)
        for response in responses:
            domain_info = extract_domain_info(response)


def print_responses(result):
    print(result)


loop = asyncio.get_event_loop()
future = asyncio.ensure_future(run(['skavo.ru', 'terminal-firm.ru']))
loop.run_until_complete(future)
