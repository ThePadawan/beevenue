def test_cannot_delete_medium_without_login(client):
    res = client.delete("/medium/1")
    assert res.status_code == 401


def test_cannot_get_medium_without_login(client):
    res = client.get("/medium/1")
    assert res.status_code == 401
