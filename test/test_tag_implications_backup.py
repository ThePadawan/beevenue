def test_tag_batch_update(client, asAdmin):
    res = client.get("/tag/implications/backup")
    assert res.status_code == 200
