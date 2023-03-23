import time
from datetime import datetime, timedelta
from itertools import islice
from typing import List, Optional, Tuple, Union

from selenium.common.exceptions import TimeoutException, WebDriverException

from .config import config, logger
from .models import Page, Price, User, WebsiteConfig
from .models_orm import (
    PageORM,
    PriceORM,
    UserORM,
    WebsiteConfigORM,
    create_session_auto,
)
from .pushover import send_message
from .webdriver import track


def get_outdated_pages_with_configs_users() -> List[Tuple[Page, WebsiteConfig, User]]:
    with create_session_auto() as sess:
        page_config_orms = (
            sess.query(PageORM, WebsiteConfigORM, UserORM)
            .filter(PageORM.next_check < datetime.now())
            .filter(PageORM.active)
            .filter(WebsiteConfigORM.active)
            .join(WebsiteConfigORM)
            .all()
        )
        return [
            (Page.from_orm(p), WebsiteConfig.from_orm(c), User.from_orm(u))
            for p, c, u in page_config_orms
        ]


def reduce_prices(prices: List[Price]):
    if len(prices) == 0:
        logger.warning("found empty prices")
        return []
    prices_reduced = [prices[0]]
    for p in islice(prices, 1, None):
        if p.price != prices_reduced[-1].price:
            prices_reduced.append(p)
    return prices_reduced


def get_prices(
    page: PageORM, limit=30, last_only=False
) -> Union[Optional[Price], List[Price]]:
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
        prices = [Price.from_orm(p) for p in q.limit(limit).all()]
        return reduce_prices(prices)


def add_price(page: Page, price: str) -> Price:
    with create_session_auto() as sess:
        price_orm = PriceORM(price=price, page_id=page.id)
        sess.add(price_orm)
        sess.flush([price_orm])
        return Price.from_orm(price_orm)


def compose_message(
    page: Page,
    conf: WebsiteConfig,
    current_price: str,
    last_price: str,
    prices: List[Price],
):
    return (
        f"{page.name} price changed from {last_price} to {current_price}\n"
        + f"Config: {conf}\nPage: {page}\n"
        + "\n".join(f"{p.created_time.isoformat()}: {p.price}" for p in prices)
    )


def check_price(page: Page, conf: WebsiteConfig, user: User) -> Optional[str]:
    with create_session_auto() as sess:
        page_orm = sess.query(PageORM).filter(PageORM.id == page.id).one()
        try:
            current_price = track(page_orm.url, conf.xpath)
            page_orm.next_check = timedelta(hours=page_orm.freq) + datetime.now()
            page_orm.retry = 0
        except (TimeoutException, WebDriverException) as e:
            page_orm.retry += 1
            msg = f"Failed to process page {page} with {conf}. Except: {e.__class__}."
            page_orm.next_check = (
                timedelta(seconds=page_orm.retry * config.pulling_freq) + datetime.now()
            )
            if page_orm.retry >= config.max_retry:
                page_orm.active = False
                msg = f"{msg} Deactivated."
            logger.error(msg)
            send_message(msg, user.po_user, user.po_device)
            return
        finally:
            sess.add(page_orm)
        return current_price


def check_(page: Page, conf: WebsiteConfig, user: User):
    current_price = check_price(page, conf, user)
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
    send_message(msg, user.po_user, user.po_device)


def _check_once():
    pages_configs_users = get_outdated_pages_with_configs_users()
    if not pages_configs_users:
        logger.info("no outdated pages found")
        return
    for page, conf, user in pages_configs_users:
        check_(page, conf, user)


def check_db_in_loop():
    while True:
        logger.info("checking db...")
        try:
            _check_once()
        except:  # noqa: E722
            logger.exception("encountered exception in while True")
        logger.info("done check once")
        time.sleep(config.pulling_freq)
