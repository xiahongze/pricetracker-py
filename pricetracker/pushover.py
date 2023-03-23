import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import config, logger

s = requests.Session()

retries = Retry(
    total=config.max_retry,
    backoff_factor=config.backoff_factor,
    status_forcelist=[500, 502, 503, 504],
)

s.mount("http://", HTTPAdapter(max_retries=retries))
s.mount("https://", HTTPAdapter(max_retries=retries))


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
    resp = s.post(url="https://api.pushover.net/1/messages.json", json=d)
    if resp.status_code != 200:
        logger.warning(f"pushover resp status: {resp.status_code}")
        logger.warning(f"pushover resp: {resp.content.decode()}")
        return
    logger.info("pushover message sent")
