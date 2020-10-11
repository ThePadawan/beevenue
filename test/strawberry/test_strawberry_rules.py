import json
import pytest

INVALID_RULES_JSONS = [
    '{"a": 3}',
    """[{
        "if": {
            "data": "maris_piper",
            "type": "hasPotatoes"
        },
        "then": [
            {
                "data": [
                    "A"
                ],
                "type": "hasAnyTagsIn"
            }
        ]
    }]""",
]


def test_get_rules(client, asAdmin):
    r = client.get("/rules")
    assert r.status_code == 200


def test_get_rules_json(client, asAdmin):
    r = client.get("/rules/rules.json")
    assert r.status_code == 200


def test_delete_nonexistant_rule(client, asAdmin):
    r = client.delete("/rules/123456")
    assert r.status_code >= 400 and r.status_code < 500


def test_delete_existing_rule(client, asAdmin):
    r = client.delete("/rules/0")
    assert r.status_code == 200


def test_validate_new_rules(client, asAdmin):
    with open("test/resources/testing_rules_simple.json", "r") as f:
        contents = f.read()

    res = client.post("/rules/validation", json=json.loads(contents))
    assert res.status_code == 200
    assert res.get_json()["ok"]


@pytest.mark.parametrize("rules_json", INVALID_RULES_JSONS)
def test_validate_invalid_rules(client, asAdmin, rules_json):
    res = client.post("/rules/validation", json=json.loads(rules_json))
    assert res.status_code == 200
    assert not res.get_json()["ok"]


def test_upload_new_rules(client, asAdmin):
    with open("test/resources/testing_rules_simple.json", "r") as f:
        contents = f.read()

    res = client.post("/rules", json=json.loads(contents))
    assert res.status_code == 200


@pytest.mark.parametrize("rules_json", INVALID_RULES_JSONS)
def test_upload_invalid_rules(client, asAdmin, rules_json):
    res = client.post("/rules", json=json.loads(rules_json))
    assert res.status_code == 400
