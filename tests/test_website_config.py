from fastapi import status
from fastapi.testclient import TestClient

from pricetracker.models import WebsiteConfig


def test_website_config_api(testclient: TestClient, fresh_db):
    # create
    config = WebsiteConfig(name="testconfig", xpath="some xpath")
    resp = testclient.post(
        "/api/website-config/", content=config.json(exclude_unset=True)
    )
    assert resp.status_code == status.HTTP_201_CREATED
    config1 = WebsiteConfig(**resp.json())

    # get
    resp = testclient.get(f"/api/website-config?idx={config1.id}")
    assert resp.status_code == status.HTTP_200_OK
    assert config1 == WebsiteConfig(**resp.json())

    # update
    config1.name = "config2"
    config1.xpath = "new xpath"
    config1.active = False
    resp = testclient.put(
        "/api/website-config/", content=config1.json(exclude_unset=True)
    )
    assert resp.status_code == status.HTTP_200_OK

    # get
    resp = testclient.get(f"/api/website-config?idx={config1.id}")
    assert resp.status_code == status.HTTP_200_OK
    assert config1 == WebsiteConfig(**resp.json())

    # add another
    config = WebsiteConfig(name="testconfig2", xpath="some xpath2")
    resp = testclient.post(
        "/api/website-config/", content=config.json(exclude_unset=True)
    )
    assert resp.status_code == status.HTTP_201_CREATED
    config2 = WebsiteConfig(**resp.json())

    # list
    resp = testclient.get("/api/website-config/list/")
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()) == 2

    # delete
    resp = testclient.delete(f"/api/website-config/?idx={config2.id}")
    assert resp.status_code == status.HTTP_202_ACCEPTED
    # list
    resp = testclient.get("/api/website-config/list/")
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()) == 1
