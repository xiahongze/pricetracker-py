from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from ..models import User as UserORM
from .basic_crud import mount


class User(BaseModel):
    id: Optional[int]
    name: Optional[str]
    po_user: Optional[str]
    po_device: Optional[str]

    class Config:
        orm_mode = True


router = APIRouter()

mount('user', router, User, UserORM)
