def test_get_missing_any(client, asAdmin):
    r = client.get("/tags/missing/any")
    assert r.status_code == 200


def test_get_missing_specific(client, asAdmin):
    r = client.get("/tags/missing/1")
    assert r.status_code == 200
