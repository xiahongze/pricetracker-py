from pricetracker.task import add_price, get_prices


def test_price_add_get(page):
    assert get_prices(page, last_only=True) == None
    assert get_prices(page) == []

    p = add_price(page, "$1.00")
    assert get_prices(page, last_only=True).price == p.price
