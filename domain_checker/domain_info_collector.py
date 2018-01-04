import asyncio
import logging
import random
from typing import List, Set

from bs4 import BeautifulSoup
from requestium import Session


logger = logging.getLogger(__name__)


def _fetch(url: str, session: Session) -> str:
    logger.info(f"fetcing {url}")
    return session.get(url).text


def _extract_info_from_response(response: str) -> dict:
    soup = BeautifulSoup(response, 'html.parser')
    parsed_domain_info_block = soup.find('div', {'class': 'df-block'})
    parsed_domain_info = parsed_domain_info_block.find_all('div', {'class': 'df-row'})

    domain_info = (line.get_text().split(':') for line in parsed_domain_info)
    domain_info = {k.lower().replace(' ', '_'): v for k, v in domain_info}

    return domain_info


async def fetch_domains_info(domains: List[str] or Set[str]) -> List[dict]:
    url = "https://www.whois.com/whois/{domain_name}"
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/62.0.3202.62 Safari/537.36'
    }
    session = Session(
        webdriver_path='WEBDRIVER_PATH',
        browser='chrome',
        default_timeout=15,
        webdriver_options={'arguments': ['headless']},
    )
    session.headers.update(headers)

    domains_info = []
    for domain in domains:
        await asyncio.sleep(random.randint(2, 6))
        try:
            resp = _fetch(url.format(domain_name=domain), session)
            info = _extract_info_from_response(resp)
        except Exception as err:
            logging.error(err)
        else:
            domains_info.append(info)

    return domains_info
