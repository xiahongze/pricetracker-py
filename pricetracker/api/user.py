from fastapi import APIRouter

from pricetracker.api.basic_crud import mount
from pricetracker.models import User
from pricetracker.models_orm import UserORM

router = APIRouter()

mount("user", router, User, UserORM)
