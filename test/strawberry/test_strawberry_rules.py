import json


def test_get_rules(adminClient):
    r = adminClient.get("/rules")
    assert r.status_code == 200


def test_get_rules_json(adminClient):
    r = adminClient.get("/rules/rules.json")
    assert r.status_code == 200


def test_delete_nonexistant_rule(adminClient):
    r = adminClient.delete("/rules/123456")
    assert r.status_code >= 400 and r.status_code < 500


def test_delete_existing_rule(adminClient):
    r = adminClient.delete("/rules/0")
    assert r.status_code == 200


def test_validate_new_rules(adminClient):
    with open("test/resources/testing_rules_simple.json", "r") as f:
        contents = f.read()

    res = adminClient.post("/rules/validation", json=json.loads(contents))
    assert res.status_code == 200


def test_upload_new_rules(adminClient):
    with open("test/resources/testing_rules_simple.json", "r") as f:
        contents = f.read()

    res = adminClient.post("/rules", json=json.loads(contents))
    assert res.status_code == 200
