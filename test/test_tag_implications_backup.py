def test_tag_batch_update(adminClient):
    res = adminClient.get("/tag/implications/backup")
    assert res.status_code == 200
