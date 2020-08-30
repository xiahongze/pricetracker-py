import time
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Union

from selenium.common.exceptions import TimeoutException, WebDriverException

from .config import config, logger
from .models import Page, Price, WebsiteConfig, create_session_auto
from .pushover import send_message
from .webdriver import track


def get_outdated_pages_and_configs() -> List[Tuple[Page, WebsiteConfig]]:
    with create_session_auto() as sess:
        return (
            sess
            .query(Page, WebsiteConfig)
            .filter(Page.next_check < datetime.now())
            .filter(Page.active)
            .join(WebsiteConfig)
            .all()
        )


def get_prices(page: Page, limit=30, last_only=False) -> Union[Optional[Price], List[Price]]:
    with create_session_auto() as sess:
        q = (
            sess.query(Price)
            .filter(Price.page_id == page.id)
            .order_by(Price.created_time.desc())
        )
        if last_only:
            return q.first()
        return q.limit(limit)


def add_price(page: Page, price: str):
    with create_session_auto() as sess:
        price_orm = Price(price=price, page_id=page.id)
        sess.add(price_orm)


def compose_message(page: Page, conf: WebsiteConfig, current_price: str, last_price: str, prices: List[Price]):
    return f"""{page.name} price changed from {last_price} to {current_price}\n"""


def check_price(page: Page, conf: WebsiteConfig) -> Optional[str]:
    try:
        current_price = track(page.url, conf.xpath)
        page.next_check = timedelta(hours=page.freq) + datetime.now()
        page.retry = 0
    except (TimeoutException, WebDriverException) as e:
        page.retry += 1
        msg = f"Failed to process page {page} with {conf}. Except: {e.__class__}."
        logger.error(msg)
        page.next_check = timedelta(seconds=page.retry * config.pulling_freq) + datetime.now()
        if page.retry >= config.max_retry:
            page.active = False
            msg = f'{msg} Deactivated.'
        return
    finally:
        with create_session_auto() as sess:
            sess.add(page)
    return current_price


def check_(page: Page, conf: WebsiteConfig):
    current_price = check_price(page, conf)
    if not current_price:
        return

    add_price(page, current_price)
    last_price = get_prices(page, last_only=True)
    if last_price is None:
        logger.info(f"found the first price for {page.name}")
        return
    if current_price == last_price.price:
        logger.info(f"found the same price for {page.name}")
        return
    prices = get_prices(page, limit=config.fetch_limit)
    msg = compose_message(page, conf, current_price, last_price.price, prices)
    send_message(msg)


def _check_once():
    pages_configs = get_outdated_pages_and_configs()
    if not pages_configs:
        logger.info("no outdated pages found")
        return
    for page, conf in pages_configs:
        check_(page, conf)


def check_db_in_loop():
    while True:
        logger.info('checking db...')
        try:
            _check_once()
        except:
            logger.exception("encountered exception in while True")
        time.sleep(config.pulling_freq)
