from datetime import datetime

from pricetracker.models import Price
from pricetracker.models_orm import PageORM, create_session_auto
from pricetracker.task import (_check_once, add_price, check_, check_price,
                               compose_message,
                               get_outdated_pages_with_configs_users,
                               get_prices, reduce_prices)


def test_price_add_get(fresh_db, page):
    assert get_prices(page, last_only=True) is None
    assert get_prices(page) == []

    p = add_price(page, "$1.00")
    assert get_prices(page, last_only=True).price == p.price


def test_get_outdate(fresh_db, page):
    assert len(get_outdated_pages_with_configs_users()) == 1


def test_msg(fresh_db, page, config):
    p1 = add_price(page, "$1.00")
    p2 = add_price(page, "$1.10")

    s = compose_message(page, config, "$1.10", "$1.00", [p1, p2])
    assert s.count('\n') == 4
    assert "url" in s and "xpath" in s
    assert "$1.10" in s and "$1.00" in s


def test_check_price_except(fresh_db, mock_track_except, page, config, user, caplog):
    assert check_price(page, config, user) is None
    assert len(get_outdated_pages_with_configs_users()) == 0
    with create_session_auto() as sess:
        page = sess.query(PageORM).filter(PageORM.id == page.id).one()
        assert page.retry == 1
        assert page.next_check > datetime.now()
        assert "Failed to process page" in caplog.text


def test_check_price(fresh_db, mock_track_two_dollar, page, config, user, caplog):
    assert check_price(page, config, user) == "$2.00"
    assert len(get_outdated_pages_with_configs_users()) == 0
    with create_session_auto() as sess:
        page = sess.query(PageORM).filter(PageORM.id == page.id).one()
        assert page.retry == 0
        assert page.next_check > datetime.now()
        assert "Failed to process page" not in caplog.text


def test_check_except(fresh_db, mock_track_except, page, config, user, caplog):
    check_(page, config, user)
    assert "Failed to process page" in caplog.text


def test_check_two_dollar(fresh_db, mock_track_two_dollar, page, config, user, caplog):
    check_(page, config, user)
    assert "found the first price" in caplog.text
    check_(page, config, user)
    assert "found the same price" in caplog.text


def test_check_once(fresh_db, mock_track_two_dollar, page, config, caplog):
    _check_once()
    assert "found the first price" in caplog.text
    _check_once()
    assert "no outdated pages found" in caplog.text


def test_reduce_price(caplog):
    reduce_prices([])
    assert 'found empty prices' in caplog.text
    p1 = Price(price='1')
    p2 = Price(price='2')
    assert len(reduce_prices([p1])) == 1
    assert len(reduce_prices([p1, p2])) == 2
    assert len(reduce_prices([p1, p1, p2])) == 2
    assert len(reduce_prices([p1, p1, p2, p2, p2])) == 2
