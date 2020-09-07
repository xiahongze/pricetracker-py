from fastapi import status
from fastapi.testclient import TestClient
from pricetracker.models import Page
from pricetracker.models_orm import PageORM, create_session_auto


def test_randomize_check(testclient: TestClient, fresh_db, page: Page):
    assert testclient.get('/utils/randomize_checks/').status_code == status.HTTP_200_OK
    assert testclient.get('/utils/randomize_checks/?within=24').status_code == status.HTTP_200_OK
    with create_session_auto() as sess:
        p = sess.query(PageORM).one()
        assert p.id == page.id
        assert p.next_check > page.next_check  # usually should be fine
