from fastapi import APIRouter

from pricetracker.models import User
from pricetracker.models_orm import UserORM
from pricetracker.api.basic_crud import mount

router = APIRouter()

mount("user", router, User, UserORM)
