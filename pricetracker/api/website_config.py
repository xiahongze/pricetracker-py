from typing import Optional

from fastapi import APIRouter

from ..models import WebsiteConfig
from ..models_orm import WebsiteConfigORM
from .basic_crud import mount

router = APIRouter()

mount('WebsiteConfig', router, WebsiteConfig, WebsiteConfigORM)
