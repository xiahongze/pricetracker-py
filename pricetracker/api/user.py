from typing import List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy.orm.session import Session
from starlette import status

from ..models import create_session, User as UserORM


class User(BaseModel):
    id: Optional[int]
    name: Optional[str]
    po_user: Optional[str]
    po_device: Optional[str]

    class Config:
        orm_mode = True


router = APIRouter()


@router.get('/')
def get_user(idx: int, sess: Session = Depends(create_session)):
    user = sess.query(UserORM).filter(UserORM.id == idx).one()
    return User.from_orm(user)


@router.get('/list', response_model=List[User])
def get_users(sess: Session = Depends(create_session)):
    return [User.from_orm(u) for u in sess.query(UserORM).all()]


@router.delete('/', response_model=User, status_code=status.HTTP_202_ACCEPTED)
def delete_user(idx: int, sess: Session = Depends(create_session)):
    user = sess.query(UserORM).filter(UserORM.id == idx).one()
    sess.delete(user)
    return User.from_orm(user)


@router.put('/', response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: User, sess: Session = Depends(create_session)):
    userOrm = UserORM(**user.dict(exclude_none=True, exclude_unset=True))
    sess.add(userOrm)
    sess.flush([userOrm])
    return User.from_orm(userOrm)


@router.post('/')
def update_user(user: User, sess: Session = Depends(create_session)):
    if user.id is None:
        raise HTTPException(400, "user id is not given")
    userOrm: UserORM = sess.query(UserORM).filter(UserORM.id == user.id).one()
    for f, v in user.dict(exclude_none=True, exclude_unset=True).items():
        setattr(userOrm, f, v)
    sess.add(userOrm)
    return
