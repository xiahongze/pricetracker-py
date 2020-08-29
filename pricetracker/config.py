import logging
import os

import yaml
from pydantic import BaseModel


class Config(BaseModel):
    db_path: str = 'sqlite:///db.sqlite3'
    debug: bool = True
    log_output: str = 'app.log'
    po_app_token: str = ''  # pushover
    max_retry: int = 10
    chrome_driver_path: str = 'chromedriver'
    gecko_driver_path: str = 'geckodriver'
    headless: bool = True
    use_chrome: bool = True
    timeout: int = 10

    def __init__(self, **data):
        if 'CONFIG' in os.environ:
            data = yaml.safe_load(os.environ['CONFIG'])
        for k in Config.schema()['properties']:  # only the first layer not cover nested models
            if k.upper() in os.environ:
                data[k] = os.environ[k.upper()]
        super().__init__(**data)


def get_logger(config: Config):
    logger = logging.getLogger('pricetracker')
    logger.setLevel(logging.INFO)
    if config.debug:
        logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(config.log_output)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(filename)s.%(funcName)s: %(message)s")
    fh.setFormatter(fmt)

    logger.addHandler(fh)

    return logger


config = Config()

logger = get_logger(config)

logger.info(config.__dict__)
