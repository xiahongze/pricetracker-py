from datetime import datetime

from fastapi.testclient import TestClient
from pricetracker.models import Price, Session
from starlette import status


def test_price_api(testclient: TestClient, fresh_db, page):
    resp = testclient.get(f'/price/?page_id={page.id}')
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()) == 0

    # add one
    sess = Session()
    p = Price(price='$10.00', page_id=page.id)
    sess.add(p)
    sess.commit()

    resp = testclient.get(f'/price/?page_id={page.id}')
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()) == 1

    # test future time
    resp = testclient.get(f'/price/?page_id={page.id}&after={datetime.now().isoformat()}')
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()) == 0

    # delete
    resp = testclient.delete(f'/price/?idx={p.id}')
    assert resp.status_code == status.HTTP_202_ACCEPTED
