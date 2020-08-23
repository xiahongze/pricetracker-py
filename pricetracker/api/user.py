from typing import Optional

from fastapi import APIRouter
from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy.orm.session import Session

from ..models import create_session


class User(BaseModel):
    id: Optional[int]
    name: Optional[str]
    po_user: Optional[str]
    po_device: Optional[str]


router = APIRouter()


@router.get('/')
def get_user(idx: int, sess: Session = Depends(create_session)):
    pass


@router.get('/list')
def get_users(sess: Session = Depends(create_session)):
    pass


@router.delete('/')
def delete_user(idx: int, sess: Session = Depends(create_session)):
    pass


@router.put('/')
def create_user(user: User, sess: Session = Depends(create_session)):
    pass


@router.post('/')
def update_user(user: User, sess: Session = Depends(create_session)):
    pass
