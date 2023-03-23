from fastapi.testclient import TestClient
from starlette import status

from pricetracker.models import Price


def test_price_api(testclient: TestClient, fresh_db, page):
    resp = testclient.get(f"/api/price/?page_id={page.id}")
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()) == 0

    # add one
    price = Price(price="$10.00")
    resp = testclient.put("/api/price/", content=price.json(exclude_unset=True))
    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    price = Price(price="$10.00", page_id=222)
    resp = testclient.put("/api/price/", content=price.json(exclude_unset=True))
    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    price = Price(price="$10.00", page_id=page.id)
    resp = testclient.put("/api/price/", content=price.json(exclude_unset=True))
    assert resp.status_code == status.HTTP_201_CREATED
    price = Price(**resp.json())

    resp = testclient.get(f"/api/price/?page_id={page.id}")
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()) == 1

    # test future time
    resp = testclient.get(f"/api/price/?page_id={page.id}&after=2000-01-01")
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()) == 1

    # delete
    resp = testclient.delete(f"/api/price/?idx={price.id}")
    assert resp.status_code == status.HTTP_202_ACCEPTED
