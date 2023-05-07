from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm.session import Session
from starlette import status

from pricetracker.api.basic_crud import mount
from pricetracker.models import Page, PageORM, UserORM, WebsiteConfigORM, create_session

router = APIRouter()

mount("page", router, Page, PageORM, ignored={"create", "list"})


@router.get("/list", response_model=List[Page])
def get_pages(user_id: int, sess: Session = Depends(create_session)):
    return [
        Page.from_orm(u)
        for u in sess.query(PageORM).filter(PageORM.user_id == user_id).all()
    ]


@router.put("/", response_model=Page, status_code=status.HTTP_201_CREATED)
def create_page(page: Page, sess: Session = Depends(create_session)):
    if page.user_id is None or page.config_id is None:
        raise HTTPException(400, "user or config id is not given")
    user = sess.query(UserORM).filter(UserORM.id == page.user_id).scalar()
    if not user:
        raise HTTPException(400, f"user id ({page.user_id}) does not exist")
    config = (
        sess.query(WebsiteConfigORM)
        .filter(WebsiteConfigORM.id == page.config_id)
        .scalar()
    )
    if not config:
        raise HTTPException(400, f"config id ({page.config_id}) does not exist")
    pageOrm = PageORM(**page.dict(exclude_none=True, exclude_unset=True))
    sess.add(pageOrm)
    sess.flush([pageOrm])
    return Page.from_orm(pageOrm)
