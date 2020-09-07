from datetime import datetime, timedelta
from random import randint

from fastapi import APIRouter
from starlette import status

from ..models_orm import PageORM, create_session_auto


def random_future(within: int) -> datetime:
    """
    return a random future within X minutes from now
    """
    dt = timedelta(minutes=randint(1, within))
    return datetime.now() + dt


router = APIRouter()


@router.get('/randomize_checks/', status_code=status.HTTP_200_OK,
            description="distribute checks within future X minutes")
def randomize_check(within: int = 24*60):
    with create_session_auto() as sess:
        pages = sess.query(PageORM).all()
        for p in pages:
            p.next_check = random_future(within)
        sess.add_all(pages)
