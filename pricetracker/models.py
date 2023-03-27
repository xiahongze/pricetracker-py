from datetime import datetime
from typing import Optional, TypeVar

from pydantic import BaseModel


class User(BaseModel):
    id: Optional[int]
    name: str
    po_user: str
    po_device: str = ""

    class Config:
        orm_mode = True


class WebsiteConfig(BaseModel):
    id: Optional[int]
    name: str
    xpath: str
    active: bool = True

    class Config:
        orm_mode = True


class Page(BaseModel):
    id: Optional[int]
    name: str
    url: str
    created_time: Optional[datetime]
    next_check: Optional[datetime]
    freq: int = 24
    retry: int = 0
    active: bool = True

    user_id: int

    config_id: int

    class Config:
        orm_mode = True


class Price(BaseModel):
    id: Optional[int]
    price: str
    created_time: Optional[datetime]

    page_id: Optional[int]

    class Config:
        orm_mode = True


ModelTypeBoundPy = TypeVar("ModelTypeBoundPy", User, WebsiteConfig, Page, Price)
