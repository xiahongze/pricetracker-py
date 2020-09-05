import pytest
from pricetracker.config import config
from pricetracker.webdriver import track
from selenium.common.exceptions import TimeoutException, WebDriverException


@pytest.fixture
def short_timeout():
    old = config.timeout
    config.timeout = 5
    yield
    config.timeout = old


@pytest.mark.skip("manually testing needed")
def test_woolies():
    url = "https://www.woolworths.com.au/shop/productdetails/77770/gold-n-canola-oil"
    xpath = '//div[@class="price price--large"] | //div[@class="price price--large ng-star-inserted"]'
    assert '$' in track(url, xpath)


@pytest.mark.skip("manually testing needed")
def test_coles():
    url = 'https://shop.coles.com.au/a/national/product/grinders-espresso-coffee-beans'
    xpath = '//span/strong[@class="product-price"] | //*[@id="main-content-inside"]/div[2]/div/header/div[3]/div/span[1]'
    assert '$' in track(url, xpath)


@pytest.mark.skip("manually testing needed")
def test_chemist():
    url = "https://www.chemistwarehouse.com.au/buy/1062/beconase-hayfever-nasal-spray-200-doses"
    xpath = '//span[@class="product__price"] | //div[@class="product__price"]'
    assert '$' in track(url, xpath)


@pytest.mark.skip("manually testing needed")
def test_chemist1():
    url = "https://www.chemistwarehouse.com.au/buy/78704/nasonex-allergy-280-dose"
    xpath = '//span[@class="product__price"] | //div[@class="product__price"]'
    assert '$' in track(url, xpath)


def test_coles_not_exist(short_timeout):
    url = 'https://shop.coles.com.au/a/national/product/goldn-canola-canola-oil'
    xpath = '//span/strong[@class="product-price not-exist"]'
    with pytest.raises(TimeoutException):
        track(url, xpath)


def test_not_exist_url(short_timeout):
    url = 'https://not-exist.com.au/rofl'
    xpath = '//span[0]'
    with pytest.raises((TimeoutException, WebDriverException)):
        track(url, xpath)
