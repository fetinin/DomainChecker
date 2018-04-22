import logging
from typing import List, Set
from settings import API_KEY

import aiohttp

logger = logging.getLogger(__name__)

API_URL = f"https://api.jsonwhois.io/whois/domain?key={API_KEY}&domain={{domain}}"


async def _fetch(url: str, session: aiohttp.ClientSession) -> dict:
    async with session.get(url) as resp:
        logger.info(f"fetcing {url}")
        return await resp.json()


def _extract_info_from_response(response: dict) -> dict:
    result = response["result"]
    return {
        "domain": result["name"],
        "nameservers": ", ".join(result["nameservers"] or []),
        "registration_date": result["created"],
        "expiration_date": result["expires"],
        "status": ", ".join(result["status"] or []),
        "extra_info": result,
    }


async def fetch_domains_info(domains: List[str] or Set[str]) -> List[dict]:
    url = API_URL
    async with aiohttp.ClientSession() as session:

        domains_info = []
        for domain in domains:
            try:
                resp = await _fetch(url.format(domain=domain), session)
                info = _extract_info_from_response(resp)
            except Exception as err:
                logging.exception(err)
            else:
                domains_info.append(info)

    return domains_info
