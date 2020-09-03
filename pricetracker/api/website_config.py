from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from ..models import WebsiteConfigORM
from .basic_crud import mount


class WebsiteConfig(BaseModel):
    id: Optional[int]
    name: Optional[str]
    xpath: Optional[str]

    class Config:
        orm_mode = True


router = APIRouter()

mount('WebsiteConfig', router, WebsiteConfig, WebsiteConfigORM)
