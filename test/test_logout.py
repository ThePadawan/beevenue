import json


def test_logout_no_longer_logged_in(userClient):
    res = userClient.post("/logout")
    assert res.status_code == 200

    res = userClient.get("/login")
    assert res.status_code == 200
    assert res.get_json() == False
