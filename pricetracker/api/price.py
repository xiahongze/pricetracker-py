from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy.orm.session import Session

from ..models import Page as PageORM
from ..models import create_session
from .page import Page


class Price(BaseModel):
    id: Optional[int]
    price: str
    created_time: datetime

    page_id: Optional[int]
    page: Optional[Page]


router = APIRouter()


@router.get('/', response_model=List[Price])
def get_prices(page_id: int, after: datetime = None, sess: Session = Depends(create_session)):
    if page_id is None:
        raise HTTPException(400, "page id is not given")
    if not after:
        after = datetime.now() - timedelta(days=30)
    prices = sess.query(PageORM).filter(PageORM.created_time >= after).order_by(PageORM.created_time.desc()).all()
    return [Price.from_orm(p) for p in prices]


@router.delete('/', response_model=Price)
def delete_price(idx: int, sess: Session = Depends(create_session)):
    pass
