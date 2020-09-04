from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    id: Optional[int]
    name: Optional[str]
    po_user: Optional[str]
    po_device: Optional[str]

    class Config:
        orm_mode = True


class WebsiteConfig(BaseModel):
    id: Optional[int]
    name: Optional[str]
    xpath: Optional[str]

    class Config:
        orm_mode = True


class Page(BaseModel):
    id: Optional[int]
    name: Optional[str]
    url: Optional[str]
    created_time: Optional[datetime]
    updated_time: Optional[datetime]
    freq: Optional[int]
    retry: Optional[int]
    active: Optional[bool]

    user_id: Optional[int]
    user: Optional[User]

    config_id: Optional[int]
    config: Optional[WebsiteConfig]

    class Config:
        orm_mode = True


class Price(BaseModel):
    id: Optional[int]
    price: str
    created_time: Optional[datetime]

    page_id: Optional[int]
    page: Optional[Page]

    class Config:
        orm_mode = True
