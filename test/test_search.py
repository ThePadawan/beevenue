import json
from urllib import parse


def _when_searching(c, query):
    q = parse.urlencode({'q': query, 'pageNumber': 1, 'pageSize': 10})
    print(q)
    return c.get(f'/search?{q}')


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


def test_search_with_combined_terms_succeeds(userClient):
    res = _when_searching(userClient, 'c:tinkerbell tags>1')
    assert res.status_code == 200
    result = json.loads(res.data)
    print(result)
    assert len(result["items"]) == 1


def test_search_with_alias_term_succeeds(userClient):
    res = _when_searching(userClient, 'c:pete c:tinkerbell')
    assert res.status_code == 200
    result = json.loads(res.data)
    print(result)
    assert len(result["items"]) == 1


def test_search_with_rating_term_succeeds(adminNsfwClient):
    res = _when_searching(adminNsfwClient, 'rating:s')
    assert res.status_code == 200
    result = json.loads(res.data)
    print(result)
    assert len(result["items"]) == 3


def test_search_with_counting_term_succeeds(adminNsfwClient):
    res = _when_searching(adminNsfwClient, 'tags<2')
    assert res.status_code == 200
    result = json.loads(res.data)
    print(result)
    assert len(result["items"]) == 1


def test_search_with_counting_term2_succeeds(adminNsfwClient):
    res = _when_searching(adminNsfwClient, 'tags<=1')
    assert res.status_code == 200
    result = json.loads(res.data)
    print(result)
    assert len(result["items"]) == 1


def test_search_with_counting_term3_succeeds(adminNsfwClient):
    res = _when_searching(adminNsfwClient, 'tags>2')
    assert res.status_code == 200
    result = json.loads(res.data)
    print(result)
    assert len(result["items"]) == 1


def test_search_with_counting_term4_succeeds(adminNsfwClient):
    res = _when_searching(adminNsfwClient, 'tags!=0')
    assert res.status_code == 200
    result = json.loads(res.data)
    print(result)
    assert len(result["items"]) == 3
