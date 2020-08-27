from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm.session import Session
from starlette import status

from ..models import create_session


def mount(name: str, router: APIRouter, klass_py, klass_orm, ignored=set()):
    """
    mount mounts common CRUD patterns onto the router

    :param klass_py: Pydantic Model
    :param klass_orm: sqlalchemy Model
    :param ignored: set of names to ignore, only from
        create, read, update, delete, list
    """
    def create(model_py: klass_py, sess: Session = Depends(create_session)):
        model_orm = klass_orm(**model_py.dict(exclude_none=True, exclude_unset=True))
        sess.add(model_orm)
        sess.flush([model_orm])
        return klass_py.from_orm(model_orm)

    def get(idx: int, sess: Session = Depends(create_session)):
        model_orm = sess.query(klass_orm).filter(klass_orm.id == idx).one()
        return klass_py.from_orm(model_orm)

    def update(model_py: klass_py, sess: Session = Depends(create_session)):
        if model_py.id is None:
            raise HTTPException(400, f"{name} id is not given")
        model_orm: klass_orm = sess.query(klass_orm).filter(klass_orm.id == model_py.id).one()
        for f, v in model_py.dict(exclude_none=True, exclude_unset=True).items():
            setattr(model_orm, f, v)
        sess.add(model_orm)
        return

    def delete(idx: int, sess: Session = Depends(create_session)):
        model_orm = sess.query(klass_orm).filter(klass_orm.id == idx).one()
        sess.delete(model_orm)
        return klass_py.from_orm(model_orm)

    def list_all(sess: Session = Depends(create_session)):
        return [klass_py.from_orm(u) for u in sess.query(klass_orm).all()]

    if 'create' not in ignored:
        router.put('/', response_model=klass_py, status_code=status.HTTP_201_CREATED)(create)
    if 'read' not in ignored:
        router.get('/', response_model=klass_py)(get)
    if 'update' not in ignored:
        router.post('/')(update)
    if 'delete' not in ignored:
        router.delete('/', response_model=klass_py, status_code=status.HTTP_202_ACCEPTED)(delete)
    if 'list' not in ignored:
        router.get('/list', response_model=List[klass_py])(list_all)
