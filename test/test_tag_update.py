
def test_cannot_update_tag_without_login(client):
    res = client.patch('/tag/u:overwatch')
    assert res.status_code == 401


def test_cannot_update_tag_as_user(userClient):
    res = userClient.patch('/tag/u:overwatch')
    assert res.status_code == 403


def test_updating_missing_tag_as_admin_404s(adminClient):
    res = adminClient.patch('/tag/potatoCanister', json={
        'newName': 'u:tubular'
    })
    assert res.status_code == 404
    # TODO Assert correct notification format


def test_update_as_admin_validates_schema(adminClient):
    res = adminClient.patch('/tag/u:overwatch', json={
        'newNameButWrongField': 'u:overwatch2'
    })
    assert res.status_code == 400
    # TODO Assert correct notification format


def test_can_update_current_tag_as_admin(adminClient):
    res = adminClient.patch('/tag/u:overwatch', json={
        'newName': 'u:overwatch2'
    })
    assert res.status_code == 200
    # TODO Assert correct notification format


def test_can_merge_current_tag_as_admin(adminClient):
    res = adminClient.patch('/tag/A', json={
        'newName': 'B'
    })
    assert res.status_code == 200
