from fastapi import APIRouter
from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    po_user: str
    po_token: str


router = APIRouter()


@router.get('/')
def get_user(idx: int):
    pass


@router.get('/list')
def get_users():
    pass


@router.delete('/')
def get_users(idx: int):
    pass


@router.put('/')
def create_user(user: User):
    pass


@router.post('/')
def update_user(user: User):
    pass
