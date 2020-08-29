from fastapi import status
from fastapi.testclient import TestClient
from pricetracker.api.website_config import WebsiteConfig


def test_website_config_api(testclient: TestClient, fresh_db):
    # create
    config = WebsiteConfig(name='testconfig', xpath='some xpath')
    resp = testclient.put('/website-config/', config.json(exclude_unset=True))
    assert resp.status_code == status.HTTP_201_CREATED
    config1 = WebsiteConfig(**resp.json())

    # get
    resp = testclient.get(f'/website-config?idx={config1.id}')
    assert resp.status_code == status.HTTP_200_OK
    assert config1 == WebsiteConfig(**resp.json())

    # update
    config1.name = 'config2'
    config1.xpath = 'new xpath'
    resp = testclient.post(f'/website-config/', config1.json(exclude_unset=True))
    assert resp.status_code == status.HTTP_200_OK

    # get
    resp = testclient.get(f'/website-config?idx={config1.id}')
    assert resp.status_code == status.HTTP_200_OK
    assert config1 == WebsiteConfig(**resp.json())

    # add another
    config = WebsiteConfig(name='testconfig2', xpath='some xpath2')
    resp = testclient.put('/website-config/', config.json(exclude_unset=True))
    assert resp.status_code == status.HTTP_201_CREATED
    config2 = WebsiteConfig(**resp.json())

    # list
    resp = testclient.get(f'/website-config/list/')
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()) == 2

    # delete
    resp = testclient.delete(f'/website-config/?idx={config2.id}')
    assert resp.status_code == status.HTTP_202_ACCEPTED
    # list
    resp = testclient.get(f'/website-config/list/')
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()) == 1
