import atexit
import os
from tempfile import mktemp

import pytest
from fastapi.testclient import TestClient
from starlette import status

# sqlite:///:memory: (or, sqlite://)
# sqlite:///relative/path/to/file.db
# sqlite:////absolute/path/to/file.db
tmp_db = mktemp(suffix=".sqlite3")
os.environ["DB_PATH"] = f"sqlite:///{tmp_db}"


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
    user = User(name="testuser1", po_user="pouser1", po_token="potoken1")
    resp = testclient.put("/api/user/", data=user.json(exclude_unset=True))
    assert resp.status_code == status.HTTP_201_CREATED
    user = User(**resp.json())
    yield user
    resp = testclient.delete(f"/api/user/?idx={user.id}")
    assert resp.status_code == status.HTTP_202_ACCEPTED


@pytest.fixture
def config(testclient):
    # don't import at the beginning of the file
    # because we need to set the env before the package is loaded
    from pricetracker.models import WebsiteConfig

    # add config
    config = WebsiteConfig(name="config1", xpath="interestingxpath")
    resp = testclient.put("/api/website-config/", data=config.json(exclude_unset=True))
    assert resp.status_code == status.HTTP_201_CREATED
    config = WebsiteConfig(**resp.json())
    yield config
    resp = testclient.delete(f"/api/website-config/?idx={config.id}")
    assert resp.status_code == status.HTTP_202_ACCEPTED


@pytest.fixture
def page(user, config, testclient):
    from pricetracker.models import Page

    # breakpoint()
    page = Page(
        name="coffee",
        url="http://example.com/xxx",
        user_id=user.id,
        config_id=config.id,
    )
    resp = testclient.put("/api/page/", data=page.json(exclude_unset=True))
    assert resp.status_code == status.HTTP_201_CREATED
    page = Page(**resp.json())
    yield page
    resp = testclient.delete(f"/api/page/?idx={page.id}")
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


@pytest.fixture
def mock_track_except():
    from selenium.common.exceptions import TimeoutException

    from pricetracker import task

    def throw(*args):
        raise TimeoutException()

    origin = task.track
    task.track = throw
    yield
    task.track = origin


@pytest.fixture
def mock_track_two_dollar():
    from pricetracker import task

    origin = task.track
    task.track = lambda *args: "$2.00"
    yield
    task.track = origin


atexit.register(lambda: os.path.exists(tmp_db) and os.unlink(tmp_db))
