def test_cannot_create_thumb_without_logging_in(client):
    res = client.patch('/thumbnail/1')
    assert res.status_code == 401


def test_cannot_create_thumb_as_user(userClient):
    res = userClient.patch('/thumbnail/1')
    assert res.status_code == 403


def test_cannot_create_thumb_for_missing_file(adminClient):
    res = adminClient.patch('/thumbnail/15433425')
    assert res.status_code == 404


def test_can_create_thumb_for_current_file(adminClient):
    pass
    # res = adminClient.patch('/thumbnail/1')
    # assert res.status_code == 200

    # TODO: Assert that thumb exists
