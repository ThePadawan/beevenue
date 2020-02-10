def test_spindex_get_status(adminClient):
    res = adminClient.get("/spindex/status")
    assert res.status_code == 200
    assert len(res.get_json()) > 0


def test_spindex_reindex(adminClient):
    res = adminClient.post("/spindex/reindex")
    assert res.status_code == 200
