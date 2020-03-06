def test_cannot_access_magic_thumbs_without_logging_in(client):
    res = client.get("/thumbs/1")
    assert res.status_code == 401


def test_cannot_access_files_without_logging_in(client):
    res = client.get("/files/hash1.jpg")
    assert res.status_code == 401


def test_cannot_access_magic_thumbs_for_nonexistant_medium(adminClient):
    res = adminClient.get("/thumbs/1253452")
    assert res.status_code == 404


def test_can_access_files(adminClient):
    res = adminClient.get("/files/hash1.jpg")
    assert res.status_code == 200


def test_can_access_magic_thumbs_without_client_hint(adminClient):
    res = adminClient.get("/thumbs/1")
    assert res.status_code == 200


def test_can_access_magic_thumbs_with_small_vw_client_hint(adminClient):
    res = adminClient.get("/thumbs/1", headers={"Viewport-Width": "900"})
    assert res.status_code == 200


def test_can_access_magic_thumbs_with_large_vw_client_hint(adminClient):
    res = adminClient.get("/thumbs/1", headers={"Viewport-Width": "1600"})
    assert res.status_code == 200
