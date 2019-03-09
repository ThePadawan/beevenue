def test_cannot_get_missing_thumbs_without_logging_in(client):
    res = client.get('/thumbnail/missing')
    assert res.status_code == 401


def test_cannot_get_missing_thumbs_as_user(userClient):
    res = userClient.get('/thumbnail/missing')
    assert res.status_code == 403


def test_can_get_missing_thumbs_as_admin(adminClient):
    res = adminClient.get('/thumbnail/missing')
    assert res.status_code == 200
    print(res.json)
    assert len(res.json) == 3
