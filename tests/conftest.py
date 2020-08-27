import atexit
import os
from tempfile import mktemp

import pytest
from fastapi.testclient import TestClient

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
def fresh_db():
    from pricetracker.models import Price, Session, User, WebsiteConfig

    sess = Session()
    sess.query(Price).delete()
    sess.query(WebsiteConfig).delete()
    sess.query(User).delete()
    sess.commit()
    yield


atexit.register(lambda: os.unlink(tmp_db))
