import requests
from loguru import logger
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from pricetracker.config import config

session = requests.Session()
PUSHOVER_URL = "https://api.pushover.net/1/messages.json"

retries = Retry(
    total=config.max_retry,
    backoff_factor=config.backoff_factor,
    status_forcelist=[500, 502, 503, 504],
)

session.mount("http://", HTTPAdapter(max_retries=retries))
session.mount("https://", HTTPAdapter(max_retries=retries))


def send_message(msg: str, po_user: str, po_device: str):
    if not config.po_app_token or not po_user:
        # don't send message without an active account
        return
    d = {
        "message": msg,
        "token": config.po_app_token,
        "user": po_user,
        "device": po_device,
    }
    resp = session.post(url=PUSHOVER_URL, json=d)
    if resp.status_code != 200:
        logger.warning(f"pushover resp status: {resp.status_code}")
        logger.warning(f"pushover resp: {resp.content.decode()}")
        return
    logger.info("pushover message sent")
