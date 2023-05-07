from fastapi import APIRouter

from pricetracker.api.basic_crud import mount
from pricetracker.models import User, UserORM

router = APIRouter()

mount("user", router, User, UserORM)
