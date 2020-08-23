import logging
import os
from dataclasses import dataclass, fields


@dataclass
class Config:
    db_path: str = 'db.sqlite3'
    po_user: str = ''
    po_token: str = ''
    debug: bool = False
    log_output: str = 'app.log'

    def refresh_from_env(self):
        for field in fields(self):
            env = field.name.upper()
            if env in os.environ:
                setattr(self, field.name, field.type(os.environ[env]))


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

logger = get_logger(config)

logger.info(config)
