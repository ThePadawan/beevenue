def test_cannot_get_tag_stats_without_login(client):
    res = client.get("/tags")
    assert res.status_code == 401


def test_can_get_tag_stats_as_user(client, asUser):
    res = client.get("/tags")
    assert res.status_code == 200


def test_can_get_tag_stats_as_nsfw_user(client, asUser, nsfw):
    res = client.get("/tags")
    assert res.status_code == 200


def test_can_get_tag_stats_as_admin(client, asAdmin):
    res = client.get("/tags")
    assert res.status_code == 200
    result_json = res.get_json()
    assert "tags" in result_json
    result_json = result_json["tags"]
    assert len(result_json) >= 4
    assert len([t for t in result_json if t["mediaCount"] == 0]) >= 1
    assert len([t for t in result_json if t["mediaCount"] == 1]) >= 2
    assert len([t for t in result_json if t["mediaCount"] == 2]) >= 1
