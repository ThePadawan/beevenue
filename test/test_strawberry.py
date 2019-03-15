
def test_get_rules(adminClient):
    r = adminClient.get("/rules")
    assert r.status_code == 200


def test_get_missing_all(adminClient):
    r = adminClient.get("/tags/missing/all")
    assert r.status_code == 200


def test_get_missing_any(adminClient):
    r = adminClient.get("/tags/missing/any")
    assert r.status_code == 200


def test_get_missing_specific(adminClient):
    r = adminClient.get("/tags/missing/1")
    assert r.status_code == 200
