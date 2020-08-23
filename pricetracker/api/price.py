from datetime import datetime
from typing import Optional

from fastapi import APIRouter
from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy.orm.session import Session

from ..models import create_session
from .page import Page


class Price(BaseModel):
    id: Optional[int]
    price: str
    created_time: datetime

    page_id: Optional[int]
    page: Optional[Page]


router = APIRouter()


@router.get('/')
def get_prices(page_id: int, after: datetime = None, sess: Session = Depends(create_session)):
    pass


@router.delete('/')
def delete_price(idx: int, sess: Session = Depends(create_session)):
    pass
