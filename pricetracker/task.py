import time
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Union

from selenium.common.exceptions import TimeoutException, WebDriverException

from .config import config, logger
from .models import Page, Price, User, WebsiteConfig
from .models_orm import (PageORM, PriceORM, UserORM, WebsiteConfigORM,
                         create_session_auto)
from .pushover import send_message
from .webdriver import track


def get_outdated_pages_and_configs() -> List[Tuple[Page, WebsiteConfig]]:
    with create_session_auto() as sess:
        page_config_orms = (
            sess
            .query(PageORM, WebsiteConfigORM)
            .filter(PageORM.next_check < datetime.now())
            .filter(PageORM.active)
            .filter(WebsiteConfigORM.active)
            .join(WebsiteConfigORM)
            .all()
        )
        return [(Page.from_orm(p), WebsiteConfig.from_orm(c))
                for p, c in page_config_orms]


def get_prices(page: PageORM, limit=30, last_only=False) -> Union[Optional[Price], List[Price]]:
    with create_session_auto() as sess:
        q = (
            sess.query(PriceORM)
            .filter(PriceORM.page_id == page.id)
            .order_by(PriceORM.created_time.desc())
        )
        if last_only:
            p = q.first()
            if p:
                return Price.from_orm(p)
            return None
        return [Price.from_orm(p) for p in q.limit(limit).all()]


def add_price(page: Page, price: str) -> Price:
    with create_session_auto() as sess:
        price_orm = PriceORM(price=price, page_id=page.id)
        sess.add(price_orm)
        sess.flush([price_orm])
        return Price.from_orm(price_orm)


def get_user(user_id: int) -> User:
    with create_session_auto() as sess:
        user_orm = (
            sess.query(UserORM)
            .filter(UserORM.id == user_id)
            .one()
        )
        return User.from_orm(user_orm)


def compose_message(page: Page, conf: WebsiteConfig, current_price: str, last_price: str, prices: List[Price]):
    return f"{page.name} price changed from {last_price} to {current_price}\n" +\
        f"Config: {conf}\n" + '\n'.join(f"{p.created_time.isoformat()}: {p.price}" for p in prices)


def check_price(page: Page, conf: WebsiteConfig) -> Optional[str]:
    with create_session_auto() as sess:
        page = sess.query(PageORM).filter(PageORM.id == page.id).one()
        try:
            current_price = track(page.url, conf.xpath)
            page.next_check = timedelta(hours=page.freq) + datetime.now()
            page.retry = 0
        except (TimeoutException, WebDriverException) as e:
            page.retry += 1
            msg = f"Failed to process page {page} with {conf}. Except: {e.__class__}."
            page.next_check = timedelta(seconds=page.retry * config.pulling_freq) + datetime.now()
            if page.retry >= config.max_retry:
                page.active = False
                msg = f'{msg} Deactivated.'
            logger.error(msg)
            user = get_user(page.user_id)
            send_message(msg, user.po_user, user.po_device)
            return
        finally:
            sess.add(page)
        return current_price


def check_(page: Page, conf: WebsiteConfig):
    current_price = check_price(page, conf)
    if not current_price:
        return

    last_price = get_prices(page, last_only=True)
    add_price(page, current_price)
    if last_price is None:
        logger.info(f"found the first price for {page.name}")
        return
    if current_price == last_price.price:
        logger.info(f"found the same price for {page.name}")
        return
    prices = get_prices(page, limit=config.fetch_limit)
    msg = compose_message(page, conf, current_price, last_price.price, prices)
    user = get_user(page.user_id)
    send_message(msg, user.po_user, user.po_device)


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
        logger.info("done check once")
        time.sleep(config.pulling_freq)
