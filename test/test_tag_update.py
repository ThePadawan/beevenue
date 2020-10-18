def test_cannot_update_tag_without_login(client):
    res = client.patch("/tag/u:overwatch")
    assert res.status_code == 401


def test_cannot_update_tag_as_user(client, asUser):
    res = client.patch("/tag/u:overwatch")
    assert res.status_code == 403


def test_updating_missing_tag_as_admin_404s(client, asAdmin):
    res = client.patch("/tag/potatoCanister", json={"tag": "u:tubular"})
    assert (res.status_code // 100) == 4


def test_update_as_admin_validates_schema(client, asAdmin):
    res = client.patch(
        "/tag/u:overwatch", json={"newNameButWrongField": "u:overwatch2"}
    )
    assert res.status_code == 400


def test_can_update_current_tag_as_admin(client, asAdmin):
    res = client.patch("/tag/u:overwatch", json={"tag": "u:overwatch2"})
    assert res.status_code == 200


def test_cannot_update_current_tag_to_whitespace(client, asAdmin):
    res = client.patch("/tag/u:overwatch", json={"tag": "   "})
    assert res.status_code == 400


def test_can_update_tag_rating(client, asAdmin):
    res = client.patch("/tag/u:overwatch", json={"rating": "q"})
    assert res.status_code == 200


def test_can_merge_current_tag_as_admin(client, asAdmin):
    res = client.patch("/tag/A", json={"tag": "B"})
    assert res.status_code == 200
