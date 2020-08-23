import logging
import os

import yaml
from pydantic import BaseModel


class Config(BaseModel):
    db_path: str = 'sqlite:///db.sqlite3'
    debug: bool = False
    log_output: str = 'app.log'
    po_app_token: str = ''  # pushover


def get_logger(config: Config):
    logger = logging.getLogger('pricetracker')
    logger.setLevel(logging.INFO)
    if config.debug:
        logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(config.log_output)
    fmt = logging.Formatter()
    fh.setFormatter(fmt)

    logger.addHandler(fh)

    return logger


config = Config()
if 'CONFIG' in os.environ:
    data = yaml.safe_load(os.environ['CONFIG'])
    config = Config(**data)

logger = get_logger(config)

logger.info(config)
