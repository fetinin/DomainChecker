import asyncio
import logging
from fnmatch import fnmatch
from typing import List, Tuple

import maya
from aiohttp import ClientSession
from bs4 import BeautifulSoup

from cache import memoize
from responses import responses as bulk_responses
from helpers import partition

# todo: add invalidation time
@memoize(ignore_values={'session'})
async def _fetch(url: str, session: ClientSession) -> str:
    print(f"fetcing {url}")
    # return bulk_responses[url.split('whois/')[-1]]
    async with session.get(url) as response:
        return await response.text()


def _add_pretty_date(domain_info):
    maya_date = maya.parse(domain_info['paid-till'])
    domain_info['slang_exp_date'] = f"{maya_date.slang_time()}, " \
                                    f"{maya_date.slang_date()}"
    domain_info['paid-till'] = maya_date.datetime(to_timezone='Europe/Moscow',
                                                  naive=True)


def _extract_info_from_request(response: str) -> dict:
    soup = BeautifulSoup(response, 'html.parser')
    parsed_text = soup.find('div', {'class': 'df-block-raw'}).get_text()

    parsed_info = (
        line.strip() for line in parsed_text.splitlines()
        if fnmatch(line, '*: *')
    )
    domain_info = {
        k: v.strip() for k, v in (line.split(':', 1) for line in parsed_info)
    }
    # make dates pretty
    _add_pretty_date(domain_info)

    return domain_info


async def _fetch_domains_info(domains: List[str]) -> List[dict]:
    url = "https://www.whois.com/whois/{}"
    headers = {
        'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/62.0.3202.62 Safari/537.36'
    }

    # Fetch all responses within one Client session,
    # keep connection alive for all requests.
    async with ClientSession(headers=headers) as session:
        tasks = []
        for domain in domains:
            task = asyncio.ensure_future(_fetch(url.format(domain), session))
            tasks.append(task)

        # you now have all response bodies in this variable
        resps = await asyncio.gather(*tasks,
                                     # return_exceptions=True
                                     )
        # filter out errors
        resps, errs = partition(lambda x: not isinstance(x, Exception), resps)

        for err in errs:
            logging.error(err)

        return [_extract_info_from_request(resp) for resp in resps]


def fetch_domains_info(domains: (List[str], Tuple[str])) -> List[dict] or False:
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(_fetch_domains_info(domains))
    return loop.run_until_complete(future)


print(fetch_domains_info(['skavo.ru', 'terminal-firm.ru']))
print(fetch_domains_info(['skavo.ru', 'terminal-firm.ru']))
