def test_tag_batch_update(adminClient):
    res = adminClient.post(
        "/tags/batch", json={"tags": ["C"], "mediumIds": [1]}
    )
    assert res.status_code == 200

    res = adminClient.get("/medium/1")
    assert res.status_code == 200
    assert "C" in res.get_json()["tags"]
