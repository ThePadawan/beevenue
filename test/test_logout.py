import json


def test_logout_no_longer_logged_in(client, asUser):
    res = client.post("/logout")
    assert res.status_code == 200

    res = client.get("/login")
    assert res.status_code == 200
    assert res.get_json() == False
