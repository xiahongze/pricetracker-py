from fastapi import status
from fastapi.testclient import TestClient
from pricetracker.models import User


def test_user_api(testclient: TestClient, fresh_db):
    # create
    user = User(name='testuser1', po_user='pouser1', po_token='potoken1')
    resp = testclient.put('/api/user/', data=user.json(exclude_unset=True))
    assert resp.status_code == status.HTTP_201_CREATED
    user1 = User(**resp.json())

    # get
    resp = testclient.get(f'/api/user?idx={user1.id}')
    assert resp.status_code == status.HTTP_200_OK
    assert user1 == User(**resp.json())

    # update
    user1.name = 'user2'
    user1.po_user = 'newposuser'
    user1.po_device = 'device'
    resp = testclient.post('/api/user/', data=user1.json(exclude_unset=True))
    assert resp.status_code == status.HTTP_200_OK

    # get
    resp = testclient.get(f'/api/user?idx={user1.id}')
    assert resp.status_code == status.HTTP_200_OK
    assert user1 == User(**resp.json())

    # add another
    user = User(name='testuser2', po_user='pouser2', po_token='potoken2')
    resp = testclient.put('/api/user/', data=user.json(exclude_unset=True))
    assert resp.status_code == status.HTTP_201_CREATED
    user2 = User(**resp.json())

    # list
    resp = testclient.get('/api/user/list/')
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()) == 2

    # delete
    resp = testclient.delete(f'/api/user/?idx={user2.id}')
    assert resp.status_code == status.HTTP_202_ACCEPTED
    # list
    resp = testclient.get('/api/user/list/')
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()) == 1
