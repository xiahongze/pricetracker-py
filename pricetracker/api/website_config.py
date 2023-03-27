from fastapi import APIRouter

from pricetracker.models import WebsiteConfig
from pricetracker.models_orm import WebsiteConfigORM
from pricetracker.api.basic_crud import mount

router = APIRouter()

mount("WebsiteConfig", router, WebsiteConfig, WebsiteConfigORM)
