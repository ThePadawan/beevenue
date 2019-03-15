from io import BytesIO


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
    with open('test/resources/placeholder.jpg', 'rb') as f:
        contents = f.read()
    res = adminClient.post(
        '/medium', data={'file': (BytesIO(contents), 'example.foo')})
    assert res.status_code == 200


def test_uploading_medium_with_taggy_filename_succeeds(adminClient):
    with open('test/resources/placeholder.jpg', 'rb') as f:
        contents = f.read()
    res = adminClient.post(
        '/medium', data={
            'file': (
                BytesIO(contents),
                '1234 - rating_q example.tag u_overwatch A.jpg')})
    assert res.status_code == 200
