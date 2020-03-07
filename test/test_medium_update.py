def test_cannot_update_medium_without_logging_in(client):
    res = client.patch("/medium/3")
    assert res.status_code == 401


def test_cannot_update_medium_as_user(client, asUser):
    res = client.patch("/medium/3")
    assert res.status_code == 403


def test_can_update_medium_as_admin(client, asAdmin):
    res = client.patch(
        "/medium/3",
        json={"rating": "q", "tags": [" some_new_tag   ", "A", "mango"]},
    )
    assert res.status_code == 200


def test_cant_update_medium_to_unknown_rating(client, asAdmin, nsfw):
    res = client.patch("/medium/3", json={"rating": "u", "tags": ["A"]})
    assert res.status_code == 200

    res = client.get("/medium/3")
    assert res.status_code == 200
    json_result = res.get_json()
    assert json_result["rating"] == "e"


def test_cant_update_medium_to_same_rating(client, asAdmin, nsfw):
    res = client.patch("/medium/3", json={"rating": "e", "tags": ["A"]})
    assert res.status_code == 200


def test_cant_update_missing_medium(client, asAdmin, nsfw):
    res = client.patch("/medium/233", json={"rating": "e", "tags": ["A"]})
    assert res.status_code == 400


def test_not_specifiying_tags_means_leave_them_as_is(client, asAdmin, nsfw):
    res = client.patch("/medium/2", json={"rating": "q"})
    assert res.status_code == 200
    res = client.get("/medium/2")
    assert res.status_code == 200
    json_result = res.get_json()
    assert len(json_result["tags"]) > 0


def test_specifiying_empty_tags_means_remove_all(client, asAdmin, nsfw):
    res = client.patch("/medium/2", json={"rating": "q", "tags": []})
    assert res.status_code == 200
    res = client.get("/medium/2")
    assert res.status_code == 200
    json_result = res.get_json()
    assert len(json_result["tags"]) == 0


def test_can_update_medium_with_duplicate_tags(client, asAdmin):
    res = client.patch(
        "/medium/3",
        json={"rating": "q", "tags": ["new_tag", "new_tag", "c:pete"]},
    )
    assert res.status_code == 200
