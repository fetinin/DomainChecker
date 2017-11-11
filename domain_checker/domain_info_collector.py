import asyncio
import logging
from typing import List, Set
import random

from aiohttp import ClientSession
from bs4 import BeautifulSoup

from db import db
from helpers import partition

logging.basicConfig(format='%(asctime)s |%(levelname)s| %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


async def _fetch(url: str, headers: dict, with_delay=False) -> str:
    if with_delay:
        await asyncio.sleep(random.randint(0, 60))
    async with ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            logger.info(f"fetcing {url}")
            return await response.text()


def _extract_info_from_request(response: str) -> dict:
    soup = BeautifulSoup(response, 'html.parser')
    parsed_domain_info_block = soup.find('div', {'class': 'df-block'})
    if parsed_domain_info_block:
        parsed_domain_info = parsed_domain_info_block.find_all('div', {'class': 'df-row'})
    else:
        print("FAILED")
        return None

    domain_info = (line.get_text().split(':') for line in parsed_domain_info)
    domain_info = {k.lower().replace(' ', '_'): v for k, v in domain_info}

    return domain_info


async def fetch_domains_info(domains: List[str] or Set[str]) -> List[dict]:
    url = "https://www.whois.com/whois/{}"
    headers = {
        'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/62.0.3202.62 Safari/537.36'
    }

    # Fetch all responses within one Client session,
    # keep connection alive for all requests.
    tasks = []
    with_delay = True if len(domains) > 2 else False
    for domain in domains:
        task = asyncio.ensure_future(_fetch(url.format(domain), headers, with_delay))
        tasks.append(task)

    # you now have all response bodies in this variable
    resps = await asyncio.gather(*tasks)
    # filter out errors
    resps, errs = partition(lambda x: not isinstance(x, Exception), resps)
    for err in errs:
        logging.error(err)

    return [_extract_info_from_request(resp) for resp in resps]