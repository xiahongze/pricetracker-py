from datetime import datetime

from fastapi.testclient import TestClient
from pricetracker.models import Price
from starlette import status


def test_price_api(testclient: TestClient, fresh_db, page):
    resp = testclient.get(f'/price/?page_id={page.id}')
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()) == 0

    # add one
    price = Price(price='$10.00')
    resp = testclient.put('/price/', price.json(exclude_unset=True))
    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    price = Price(price='$10.00', page_id=222)
    resp = testclient.put('/price/', price.json(exclude_unset=True))
    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    price = Price(price='$10.00', page_id=page.id)
    resp = testclient.put('/price/', price.json(exclude_unset=True))
    assert resp.status_code == status.HTTP_201_CREATED
    price = Price(**resp.json())

    resp = testclient.get(f'/price/?page_id={page.id}')
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()) == 1

    # test future time
    resp = testclient.get(f'/price/?page_id={page.id}&after={datetime.now().isoformat()}')
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()) == 0

    # delete
    resp = testclient.delete(f'/price/?idx={price.id}')
    assert resp.status_code == status.HTTP_202_ACCEPTED
