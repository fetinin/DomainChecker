import asyncio
import logging
import random
from typing import List, Set

from aiohttp import ClientSession
from bs4 import BeautifulSoup

logging.basicConfig(format='%(asctime)s |%(levelname)s| %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


async def _fetch(url: str, headers: dict) -> str:
    async with ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            logger.info(f"fetcing {url}")
            return await response.text()


def _extract_info_from_response(response: str) -> dict:
    soup = BeautifulSoup(response, 'html.parser')
    parsed_domain_info_block = soup.find('div', {'class': 'df-block'})
    parsed_domain_info = parsed_domain_info_block.find_all('div', {'class': 'df-row'})

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

    domains_info = []
    for domain in domains:
        await asyncio.sleep(random.randint(2, 6))
        try:
            resp = await _fetch(url.format(domain), headers)
            info = _extract_info_from_response(resp)
        except Exception as err:
            logging.error(err)
        else:
            domains_info.append(info)

    return domains_info
