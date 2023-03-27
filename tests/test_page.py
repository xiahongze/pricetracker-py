import json

from fastapi import status
from fastapi.testclient import TestClient


def test_page_api(testclient: TestClient, fresh_db, user, config):
    # create
    # no user_id specified
    page = dict(name="testpage", url="http://dfad.com", config_id=config.id)
    resp = testclient.put("/api/page/", content=json.dumps(page))
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # no config_ specified
    page = dict(name="testpage", url="http://dfad.com", user_id=user.id)
    resp = testclient.put("/api/page/", content=json.dumps(page))
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # specified non existent user
    page["user_id"] = 11  # not exists
    page["config_id"] = config.id
    resp = testclient.put("/api/page/", content=json.dumps(page))
    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    # specified non existent config
    page["user_id"] = user.id
    page["config_id"] = 11  # not exists
    resp = testclient.put("/api/page/", content=json.dumps(page))
    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    # legal request
    page["user_id"] = user.id
    page["config_id"] = config.id
    resp = testclient.put("/api/page/", content=json.dumps(page))
    assert resp.status_code == status.HTTP_201_CREATED
    page1 = resp.json()

    # get
    resp = testclient.get(f"/api/page?idx={page1['id']}")
    assert resp.status_code == status.HTTP_200_OK
    assert page1 == resp.json()

    # update
    page1["name"] = "page2"
    page1["url"] = "new url"
    resp = testclient.post("/api/page/", content=json.dumps(page1))
    assert resp.status_code == status.HTTP_200_OK

    # get
    resp = testclient.get(f"/api/page?idx={page1['id']}")
    assert resp.status_code == status.HTTP_200_OK
    assert page1 == resp.json()

    # add another
    page = dict(
        name="testpage3", url="http://dfad33.com", user_id=user.id, config_id=config.id
    )
    resp = testclient.put("/api/page/", content=json.dumps(page))
    assert resp.status_code == status.HTTP_201_CREATED
    page2 = resp.json()

    # list
    resp = testclient.get(f"/api/page/list?user_id={user.id}")
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()) == 2

    # delete
    resp = testclient.delete(f"/api/page/?idx={page2['id']}")
    assert resp.status_code == status.HTTP_202_ACCEPTED
    # list
    resp = testclient.get(f"/api/page/list?user_id={user.id}")
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()) == 1
