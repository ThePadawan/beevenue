import json


def _when_searching(c, query):
    return c.get(f'/search?q={query}&pageNumber=1&pageSize=10')


def test_cannot_search_without_login(client):
    res = client.get('/search')
    assert res.status_code == 401


def test_no_results_has_valid_schema(adminClient):
    res = _when_searching(adminClient, 'asdgjhkasgdgas')
    assert res.status_code == 200
    assert json.loads(res.data) == {}


def test_search_with_only_negative_terms_succeeds(userClient):
    res = _when_searching(userClient, '-C')
    assert res.status_code == 200
    result = json.loads(res.data)
    assert len(result["items"]) >= 1


def test_search_with_category_term_succeeds(userClient):
    res = _when_searching(userClient, 'utags:1')
    assert res.status_code == 200
    result = json.loads(res.data)
    print(result)
    assert len(result["items"]) == 1
