from datetime import datetime

from pricetracker.models_orm import PageORM, create_session_auto
from pricetracker.task import (_check_once, add_price, check_, check_price,
                               compose_message, get_outdated_pages_and_configs,
                               get_prices)


def test_price_add_get(fresh_db, page):
    assert get_prices(page, last_only=True) == None
    assert get_prices(page) == []

    p = add_price(page, "$1.00")
    assert get_prices(page, last_only=True).price == p.price


def test_get_outdate(fresh_db, page):
    l = get_outdated_pages_and_configs()
    assert len(l) == 1


def test_msg(fresh_db, page, config):
    p1 = add_price(page, "$1.00")
    p2 = add_price(page, "$1.10")

    s = compose_message(page, config, "$1.10", "$1.00", [p1, p2])
    assert s.count('\n') == 3
    assert "$1.10" in s and "$1.00" in s


def test_check_price_except(fresh_db, mock_track_except, page, config, caplog):
    assert check_price(page, config) == None
    l = get_outdated_pages_and_configs()
    assert len(l) == 0
    with create_session_auto() as sess:
        page = sess.query(PageORM).filter(PageORM.id == page.id).one()
        assert page.retry == 1
        assert page.next_check > datetime.now()
        assert "Failed to process page" in caplog.text


def test_check_price(fresh_db, mock_track_two_dollar, page, config, caplog):
    assert check_price(page, config) == "$2.00"
    l = get_outdated_pages_and_configs()
    assert len(l) == 0
    with create_session_auto() as sess:
        page = sess.query(PageORM).filter(PageORM.id == page.id).one()
        assert page.retry == 0
        assert page.next_check > datetime.now()
        assert "Failed to process page" not in caplog.text


def test_check_except(fresh_db, mock_track_except, page, config, caplog):
    check_(page, config)
    assert "Failed to process page" in caplog.text


def test_check_two_dollar(fresh_db, mock_track_two_dollar, page, config, caplog):
    check_(page, config)
    assert "found the first price" in caplog.text
    check_(page, config)
    assert "found the same price" in caplog.text


def test_check_once(fresh_db, mock_track_two_dollar, page, config, caplog):
    _check_once()
    assert "found the first price" in caplog.text
    _check_once()
    assert "no outdated pages found" in caplog.text
