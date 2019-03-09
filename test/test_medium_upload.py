def test_cannot_upload_medium_without_login(client):
    res = client.post('/medium')
    assert res.status_code == 401


def test_cannot_upload_medium_as_user(userClient):
    res = userClient.post('/medium')
    assert res.status_code == 403


def test_uploading_medium_as_admin_requires_some_files_in_request(adminClient):
    res = adminClient.post('/medium')
    assert res.status_code == 400


def test_uploading_medium_as_admin_succeeds(adminClient):
    # TODO Implement (using temp file)
    pass
