
def test_cannot_update_medium_without_logging_in(client):
    res = client.patch('/medium/3')
    assert res.status_code == 401


def test_cannot_update_medium_as_user(userClient):
    res = userClient.patch('/medium/3')
    assert res.status_code == 403


def test_can_update_medium_as_admin(adminClient):
    res = adminClient.patch('/medium/3', json={
        'rating': 'q',
        'tags': [' some_new_tag   ', 'A']
    })
    assert res.status_code == 200
