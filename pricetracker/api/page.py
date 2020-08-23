from datetime import datetime
from typing import Optional

from fastapi import APIRouter
from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy.orm.session import Session

from ..models import create_session
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


router = APIRouter()


@router.get('/')
def get_page(idx: int, sess: Session = Depends(create_session)):
    pass


@router.get('/list')
def get_pages(sess: Session = Depends(create_session)):
    pass


@router.delete('/')
def delete_page(idx: int, sess: Session = Depends(create_session)):
    pass


@router.put('/')
def create_page(page: Page, sess: Session = Depends(create_session)):
    pass


@router.post('/')
def update_page(page: Page, sess: Session = Depends(create_session)):
    pass
