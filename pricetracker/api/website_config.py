from fastapi import APIRouter

from pricetracker.api.basic_crud import mount
from pricetracker.models import WebsiteConfig
from pricetracker.models_orm import WebsiteConfigORM

router = APIRouter()

mount("WebsiteConfig", router, WebsiteConfig, WebsiteConfigORM)
