
from fastapi import APIRouter

from ..models import User
from ..models_orm import UserORM
from .basic_crud import mount

router = APIRouter()

mount('user', router, User, UserORM)
