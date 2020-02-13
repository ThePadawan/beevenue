def test_tag_batch_update(adminClient):
    res = adminClient.post(
        "/tags/batch", json={"tags": ["C"], "mediumIds": [1]}
    )
    assert res.status_code == 200

    res = adminClient.get("/medium/1")
    assert res.status_code == 200
    assert "C" in res.get_json()["tags"]


def test_tag_cannot_add_tags_to_zero_media(adminClient):
    res = adminClient.post("/tags/batch", json={"tags": ["C"], "mediumIds": []})
    assert res.status_code == 200


def test_double_adding_tag_to_medium_does_not_fail(adminClient):
    res = adminClient.get("/medium/1")
    assert res.status_code == 200
    assert "A" in res.get_json()["tags"]

    res = adminClient.post(
        "/tags/batch", json={"tags": ["A"], "mediumIds": [1]}
    )
    assert res.status_code == 200

    res = adminClient.get("/medium/1")
    assert res.status_code == 200
    assert "A" in res.get_json()["tags"]


def test_tag_cannot_add_tags_to_missing_media(adminClient):
    res = adminClient.post(
        "/tags/batch", json={"tags": ["C"], "mediumIds": [55343]}
    )
    assert res.status_code == 200


def test_tag_cannot_add_zero_tags_to_medium(adminClient):
    res = adminClient.post("/tags/batch", json={"tags": [], "mediumIds": [1]})
    assert res.status_code == 200


def test_tag_cannot_add_new_tags_to_medium(adminClient):
    res = adminClient.post(
        "/tags/batch", json={"tags": ["klonoa"], "mediumIds": [1]}
    )
    assert res.status_code == 200

    res = adminClient.get("/medium/1")
    assert res.status_code == 200
    assert "klonoa" not in res.get_json()["tags"]
