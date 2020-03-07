def test_thumbnail_recreate_succeeds(client, asAdmin):
    res = client.patch("/thumbnail/4")
    assert res.status_code == 200


def test_thumbnail_recreate_fails_on_404(client, asAdmin):
    res = client.patch("/thumbnail/1243")
    assert res.status_code == 404
