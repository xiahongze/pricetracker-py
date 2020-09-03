import atexit
import os
from tempfile import mktemp

import pytest
from fastapi.testclient import TestClient
from starlette import status

# sqlite:///:memory: (or, sqlite://)
# sqlite:///relative/path/to/file.db
# sqlite:////absolute/path/to/file.db
tmp_db = mktemp(suffix='.sqlite3')
os.environ['DB_PATH'] = f'sqlite:///{tmp_db}'


@pytest.fixture(scope="session")
def testclient():
    from pricetracker.main import app

    return TestClient(app)


@pytest.fixture
def user(testclient):
    # don't import at the beginning of the file
    # because we need to set the env before the package is loaded
    from pricetracker.api.user import User

    # add user
    user = User(name='testuser1', po_user='pouser1', po_token='potoken1')
    resp = testclient.put('/user/', user.json(exclude_unset=True))
    assert resp.status_code == status.HTTP_201_CREATED
    user = User(**resp.json())
    yield user
    resp = testclient.delete(f'/user/?idx={user.id}')
    assert resp.status_code == status.HTTP_202_ACCEPTED


@pytest.fixture
def config(testclient):
    # don't import at the beginning of the file
    # because we need to set the env before the package is loaded
    from pricetracker.api.website_config import WebsiteConfig

    # add config
    config = WebsiteConfig(name='config1', xpath='interestingxpath')
    resp = testclient.put('/website-config/', config.json(exclude_unset=True))
    assert resp.status_code == status.HTTP_201_CREATED
    config = WebsiteConfig(**resp.json())
    yield config
    resp = testclient.delete(f'/website-config/?idx={config.id}')
    assert resp.status_code == status.HTTP_202_ACCEPTED


@pytest.fixture
def page(user, config, testclient):
    from pricetracker.api.page import Page

    # breakpoint()
    page = Page(name='coffee', url='http://example.com/xxx', user_id=user.id, config_id=config.id)
    resp = testclient.put('/page/', page.json(exclude_unset=True))
    assert resp.status_code == status.HTTP_201_CREATED
    page = Page(**resp.json())
    yield page
    resp = testclient.delete(f'/page/?idx={page.id}')
    assert resp.status_code == status.HTTP_202_ACCEPTED


@pytest.fixture
def fresh_db():
    # this fixture needs to be put before other db related fixtures, such as
    # user and config (above)
    from pricetracker.models_orm import PriceORM, Session, UserORM, WebsiteConfigORM

    sess = Session()
    sess.query(PriceORM).delete()
    sess.query(WebsiteConfigORM).delete()
    sess.query(UserORM).delete()
    sess.commit()
    yield


atexit.register(lambda: os.path.exists(tmp_db) and os.unlink(tmp_db))
