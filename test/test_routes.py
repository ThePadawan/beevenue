def test_cannot_get_present_tag_as_user(client):
    res = client.get("/tag/u:overwatch")
    assert res.status_code == 401


def test_present_tag_returns_200(client, asAdmin):
    res = client.get("/tag/u:overwatch")
    assert res.status_code == 200


def test_missing_tag_returns_404(client, asAdmin):
    res = client.get("/tag/someUnknownTag")
    assert res.status_code == 404
