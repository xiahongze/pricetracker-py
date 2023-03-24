from typing import Optional

from pydantic import BaseSettings


class Config(BaseSettings):
    db_path: str = "sqlite:///db.sqlite3"
    debug: bool = False
    pulling_freq: int = 600  # seconds
    fetch_limit: int = 60  # for historical prices
    po_app_token: str = ""  # pushover
    max_retry: int = 10
    chrome_driver_path: str = "chromedriver"
    gecko_driver_path: str = "geckodriver"
    headless: bool = True
    use_chrome: bool = True
    timeout: int = 10
    backoff_factor: float = 1.0
    user_agent: Optional[str]
    disable_tracking: bool = False  # disable tracking thread

    class Config:
        env_file = ".env", ".env.prod"


config = Config()
