import json


def test_cannot_search_without_login(client):
    res = client.get('/search')
    assert res.status_code == 401


def test_no_results_has_valid_schema(adminClient):
    res = adminClient.get('/search?q=asdgjhkasgdgas&pageNumber=1&pageSize=10')
    assert res.status_code == 200
    assert json.loads(res.data) == {}


def test_search_with_only_negative_terms_succeeds(userClient):
    res = userClient.get('/search?q=-C&pageNumber=1&pageSize=10')
    assert res.status_code == 200
    result = json.loads(res.data)
    assert len(result["items"]) == 1
