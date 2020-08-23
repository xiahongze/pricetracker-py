from typing import Optional

from fastapi import APIRouter
from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy.orm.session import Session

from ..models import create_session


class WebsiteConfig(BaseModel):
    id: Optional[int]
    name: Optional[str]
    regex: Optional[str]


router = APIRouter()


@router.get('/')
def get_config(idx: int, sess: Session = Depends(create_session)):
    pass


@router.get('/list')
def get_configs(sess: Session = Depends(create_session)):
    pass


@router.delete('/')
def delete_config(idx: int, sess: Session = Depends(create_session)):
    pass


@router.put('/')
def create_config(config: WebsiteConfig, sess: Session = Depends(create_session)):
    pass


@router.post('/')
def update_config(config: WebsiteConfig, sess: Session = Depends(create_session)):
    pass
