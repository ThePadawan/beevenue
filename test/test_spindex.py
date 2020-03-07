def test_spindex_get_status(client, asAdmin):
    res = client.get("/spindex/status")
    assert res.status_code == 200
    assert len(res.get_json()) > 0


def test_spindex_reindex(client, asAdmin):
    res = client.post("/spindex/reindex")
    assert res.status_code == 200
