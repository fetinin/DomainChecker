import asyncio
import logging
import random
from typing import List, Set
import settings

from bs4 import BeautifulSoup
from requestium import Session


logger = logging.getLogger(__name__)


def _fetch(url: str, session: Session) -> str:
    logger.info(f"fetcing {url}")
    session.driver.get(url)
    return session.driver.page_source


def _extract_info_from_response(response: str) -> dict:
    soup = BeautifulSoup(response, 'html.parser')
    parsed_domain_info_block = soup.find('div', {'class': 'df-block'})
    parsed_domain_info = parsed_domain_info_block.find_all('div', {'class': 'df-row'})

    domain_info = (line.get_text().split(':') for line in parsed_domain_info)
    domain_info = {k.lower().replace(' ', '_'): v for k, v in domain_info}

    return domain_info


async def fetch_domains_info(domains: List[str] or Set[str]) -> List[dict]:
    url = "https://www.whois.com/whois/{domain_name}"
    session = Session(
        webdriver_path=settings.WEBDRIVER_PATH,
        browser='chrome',
        default_timeout=15,
        webdriver_options={'arguments': ['headless']},
    )

    domains_info = []
    for domain in domains:
        await asyncio.sleep(random.randint(2, 6))
        try:
            resp = _fetch(url.format(domain_name=domain), session)
            info = _extract_info_from_response(resp)
        except Exception as err:
            logging.exception(err)
        else:
            domains_info.append(info)
        finally:
            session.driver.close()
            session.close()

    return domains_info
