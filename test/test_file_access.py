def test_cannot_access_thumbs_without_logging_in(client):
    res = client.get("/thumbs/1/s.jpg")
    assert res.status_code == 401


def test_cannot_access_files_without_logging_in(client):
    res = client.get("/files/hash1.jpg")
    assert res.status_code == 401
