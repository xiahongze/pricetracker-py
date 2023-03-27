from datetime import date, datetime, timedelta
from typing import List

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.params import Depends
from sqlalchemy.orm.session import Session
from starlette import status

from pricetracker.models import Price
from pricetracker.models_orm import PageORM, PriceORM, create_session

router = APIRouter()


@router.put("/", response_model=Price, status_code=status.HTTP_201_CREATED)
def create_price(price: Price, sess: Session = Depends(create_session)):
    if price.page_id is None:
        raise HTTPException(400, "page id is not given")
    page = sess.query(PageORM).filter(PageORM.id == price.page_id).scalar()
    if not page:
        raise HTTPException(400, f"page id ({price.page_id}) does not exist")
    priceOrm = PriceORM(**price.dict(exclude_none=True, exclude_unset=True))
    sess.add(priceOrm)
    sess.flush([priceOrm])
    return Price.from_orm(priceOrm)


@router.get("/", response_model=List[Price])
def get_prices(
    page_id: int, after: date = None, sess: Session = Depends(create_session)
):
    if page_id is None:
        raise HTTPException(400, "page id is not given")
    page = sess.query(PageORM).filter(PageORM.id == page_id).scalar()
    if not page:
        raise HTTPException(400, f"page id ({page_id}) does not exist")
    if not after:
        after = datetime.now() - timedelta(days=30)
    prices = (
        sess.query(PriceORM)
        .filter(PriceORM.page_id == page_id)
        .filter(PriceORM.created_time >= after)
        .order_by(PriceORM.created_time.desc())
        .all()
    )
    return [Price.from_orm(p) for p in prices]


@router.delete("/", response_model=Price, status_code=status.HTTP_202_ACCEPTED)
def delete_price(idx: int, sess: Session = Depends(create_session)):
    price_orm = sess.query(PriceORM).filter(PriceORM.id == idx).one()
    sess.delete(price_orm)
    return Price.from_orm(price_orm)
