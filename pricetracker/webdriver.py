import re
from functools import partial
from pathlib import Path

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .config import config, logger

ua = UserAgent()


def make_chrome_options():
    options = webdriver.ChromeOptions()
    excluded_flags = ['enable-automation', 'ignore-certificate-errors']
    options.headless = config.headless
    options.add_argument('--disable-gpu')
    options.add_argument(f"--user-agent={ua.chrome}")
    options.add_experimental_option("excludeSwitches", excluded_flags)
    options.add_argument('--profile-directory=Default')
    options.add_argument("--incognito")
    options.add_argument("--start-maximized")
    # below is important to chrome 78+
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--disable-plugins-discovery")
    # options.add_argument('--disable-extensions')
    return options


def make_firefox_options():
    options = webdriver.FirefoxOptions()
    options.headless = config.headless
    profile = webdriver.FirefoxProfile()
    profile.set_preference("general.useragent.override", ua.firefox)
    profile.set_preference("dom.webdriver.enabled", False)
    options.profile = profile
    return options


init_js = Path(__file__).with_name('init.js').read_text()

spaces = re.compile(r'\s*')


def clean_text(text: str):
    return spaces.sub('', text)


def track(url: str, xpath: str, use_chrome=config.use_chrome):
    if use_chrome:
        make_driver = partial(webdriver.Chrome, executable_path=config.chrome_driver_path,
                              options=make_chrome_options())
    else:
        make_driver = partial(webdriver.Firefox, executable_path=config.gecko_driver_path,
                              options=make_firefox_options())

    with make_driver() as driver:
        driver.set_page_load_timeout(config.timeout)
        driver.set_window_size(1034, 768)
        driver.execute_script(init_js)
        driver.get(url)
        # breakpoint()
        el = WebDriverWait(driver, config.timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, xpath)
            ))
        logger.info(f"fetch page {driver.title}")
        text = clean_text(el.text)
        logger.info(f"Xpath ({xpath}): {text}")
        return text
