import time
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Union

from .config import config, logger
from .models import Page, Price, WebsiteConfig, create_session_auto
from .pushover import send_message
from .webdriver import track

# TODO:
# - retry
# - exception
# - deactivate


def get_outdated_pages_and_configs() -> List[Tuple[Page, WebsiteConfig]]:
    with create_session_auto() as sess:
        return (
            sess
            .query(Page, WebsiteConfig)
            .filter(Page.next_check < datetime.now())
            .join(WebsiteConfig)
            .all()
        )


def update_page(page: Page):
    with create_session_auto() as sess:
        page.next_check = timedelta(seconds=page.retry * config.pulling_freq) + datetime.now()
        sess.add(page)


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


def check_db():
    while True:
        logger.info('checking db...')
        try:
            pages_configs = get_outdated_pages_and_configs()
            if not pages_configs:
                logger.info("no outdated pages found")
                time.sleep(config.pulling_freq)
                continue
            for page, conf in pages_configs:
                current_price = track(page.url, conf.xpath)
                last_price = get_prices(page, last_only=True)
                add_price(page, current_price)
                update_page(page)
                if last_price is None:
                    logger.info(f"found the first price for {page.name}")
                    continue
                if current_price == last_price.price:
                    logger.info(f"found the same price for {page.name}")
                    continue
                prices = get_prices(page, limit=config.fetch_limit)
                send_message(compose_message(page, conf, current_price, last_price.price, prices))
        except:
            logger.exception("encountered exception")
        time.sleep(config.pulling_freq)
