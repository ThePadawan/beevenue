import pytest


def test_get_missing_any(client, asAdmin):
    r = client.get("/tags/missing/any")
    assert r.status_code == 200


@pytest.mark.parametrize("id", [1, 2, 3, 4, 5])
def test_get_missing_specific(client, asAdmin, id):
    r = client.get(f"/tags/missing/{id}")
    assert r.status_code == 200


@pytest.mark.parametrize("id", [1, 2, 3, 4, 5])
def test_trivial_rules_always_succeed(client, asAdmin, withTrivialRules, id):
    r = client.get(f"/tags/missing/{id}")
    assert r.status_code == 200
    assert str(id) in r.get_json()
    assert r.get_json()[str(id)] == []
