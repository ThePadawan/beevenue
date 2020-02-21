def test_cannot_get_tag_stats_without_login(client):
    res = client.get("/tags")
    assert res.status_code == 401


def test_can_get_tag_stats_as_user(userClient):
    res = userClient.get("/tags")
    assert res.status_code == 200


def test_can_get_tag_stats_as_admin(adminClient):
    res = adminClient.get("/tags")
    assert res.status_code == 200
    result_json = res.get_json()
    assert len(result_json) >= 4
    assert len([t for t in result_json if t["mediaCount"] == 0]) >= 1
    assert len([t for t in result_json if t["mediaCount"] == 1]) >= 2
    assert len([t for t in result_json if t["mediaCount"] == 2]) >= 1
