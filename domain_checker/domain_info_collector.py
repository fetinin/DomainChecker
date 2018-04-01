import asyncio
import logging
import random
from typing import List, Set
import time

from bs4 import BeautifulSoup
from requestium import Session

import settings

logger = logging.getLogger(__name__)


def _fetch(url: str, session: Session) -> str:
    logger.info(f"fetcing {url}")
    session.driver.get(url)
    session.driver.execute_script("refreshWhois();")
    time.sleep(2)  # wait for js to fetch data, async sleep doesn't work
    return session.driver.page_source


def _extract_info_from_response(response: str) -> dict:
    soup = BeautifulSoup(response, "html.parser")
    parsed_domain_info_block = soup.find("div", {"class": "df-block"})
    if parsed_domain_info_block is None:
        raise ValueError("Failed to find div.df-block in response html.")

    parsed_domain_info = parsed_domain_info_block.find_all("div", {"class": "df-row"})

    domain_info = (line.get_text().split(":") for line in parsed_domain_info)
    domain_info = {k.lower().replace(" ", "_"): v for k, v in domain_info}

    return domain_info


async def fetch_domains_info(domains: List[str] or Set[str]) -> List[dict]:
    url = "https://www.whois.com/whois/{domain_name}"
    session = Session(
        webdriver_path=settings.WEBDRIVER_PATH,
        browser="chrome",
        default_timeout=15,
        webdriver_options={
            "arguments": ["headless"], "binary_location": settings.GOOGLE_CHROME_SHIM
        },
    )

    domains_info = []
    try:
        for domain in domains:
            await asyncio.sleep(random.randint(2, 4))
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
