from datetime import datetime
from typing import Optional

from fastapi import APIRouter
from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy.orm.session import Session

from ..models import Page as PageORM
from ..models import create_session
from .basic_crud import mount
from .user import User


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

    class Config:
        orm_mode = True


router = APIRouter()

mount('page', router, Page, PageORM, ignored={'create', 'list'})


@router.get('/list')
def get_pages(sess: Session = Depends(create_session)):
    pass


@router.put('/')
def create_page(page: Page, sess: Session = Depends(create_session)):
    pass
