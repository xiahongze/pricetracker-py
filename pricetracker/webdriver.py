import re
from functools import partial
from pathlib import Path

from fake_useragent import FakeUserAgentError, UserAgent
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pricetracker.config import config

try:
    ua = UserAgent()
    ua_chrome = ua.chrome
    ua_firefox = ua.firefox
except FakeUserAgentError:
    ua_chrome = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2"  # noqa: E501
    ua_firefox = "Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1"  # noqa: E501


def make_chrome_options():
    options = webdriver.ChromeOptions()
    excluded_flags = ["enable-automation", "ignore-certificate-errors"]
    if config.headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    if config.user_agent:
        options.add_argument(f"--user-agent={config.user_agent}")
    else:
        options.add_argument(f"--user-agent={ua_chrome}")
    options.add_experimental_option("excludeSwitches", excluded_flags)
    options.add_argument("--profile-directory=Default")
    options.add_argument("--incognito")
    options.add_argument("--start-maximized")
    # below is important to chrome 78+
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    # options.add_argument("--disable-plugins-discovery")
    # options.add_argument('--disable-extensions')
    return options


def make_firefox_options():
    options = webdriver.FirefoxOptions()
    options.headless = config.headless
    profile = webdriver.FirefoxProfile()
    if config.user_agent:
        profile.set_preference("general.useragent.override", config.user_agent)
    else:
        profile.set_preference("general.useragent.override", ua_firefox)
    profile.set_preference("dom.webdriver.enabled", False)
    options.profile = profile
    return options


init_js = Path(__file__).parent.joinpath("assets/init.js").read_text()

spaces = re.compile(r"\s*")


def clean_text(text: str):
    return spaces.sub("", text)


def track(url: str, xpath: str, use_chrome=config.use_chrome):
    if use_chrome:
        make_driver = partial(
            webdriver.Chrome,
            executable_path=config.chrome_driver_path,
            options=make_chrome_options(),
        )
    else:
        make_driver = partial(
            webdriver.Firefox,
            executable_path=config.gecko_driver_path,
            options=make_firefox_options(),
        )

    with make_driver() as driver:
        driver.set_page_load_timeout(config.timeout)
        driver.set_window_size(1034, 768)
        driver.execute_script(init_js)
        driver.get(url)
        # breakpoint()
        el = WebDriverWait(driver, config.timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        logger.info(f"fetch page {driver.title}")
        text = clean_text(el.text)
        logger.info(f"Xpath ({xpath}): {text}")
        return text
