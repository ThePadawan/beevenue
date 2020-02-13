import json
from urllib import parse
import pytest


def _when_searching(c, query):
    q = parse.urlencode({"q": query, "pageNumber": 1, "pageSize": 10})
    print(q)
    return c.get(f"/search?{q}")


def test_cannot_search_without_login(client):
    res = client.get("/search")
    assert res.status_code == 401


def test_no_results_has_valid_schema(adminClient):
    res = _when_searching(adminClient, "asdgjhkasgdgas")
    assert res.status_code == 200
    assert "items" in res.get_json()
    assert res.get_json()["items"] == []


def test_search_with_only_negative_terms_succeeds(userClient):
    res = _when_searching(userClient, "-C")
    assert res.status_code == 200
    result = res.get_json()
    assert len(result["items"]) >= 1


identical_group_search_terms = ["utags:1", "utags=1"]
identical_counting_search_terms = ["tags:2", "tags=2"]


@pytest.mark.parametrize("q", identical_group_search_terms)
def test_search_with_category_term_succeeds(userClient, q):
    res = _when_searching(userClient, q)
    assert res.status_code == 200
    result = res.get_json()
    print(result)
    assert len(result["items"]) == 1


@pytest.mark.parametrize("q", identical_counting_search_terms)
def test_search_colon_is_treated_the_same_as_equals(userClient, q):
    res = _when_searching(userClient, q)
    assert res.status_code == 200
    result = res.get_json()
    print(result)
    assert len(result["items"]) == 2


def test_search_with_combined_terms_succeeds(userClient):
    res = _when_searching(userClient, "c:tinkerbell tags>1")
    assert res.status_code == 200
    result = res.get_json()
    print(result)
    assert len(result["items"]) == 1


def test_search_with_alias_term_succeeds(userClient):
    res = _when_searching(userClient, "c:pete c:tinkerbell")
    assert res.status_code == 200
    result = res.get_json()
    print(result)
    assert len(result["items"]) == 1


def test_search_with_rating_term_succeeds(adminNsfwClient):
    res = _when_searching(adminNsfwClient, "rating:s")
    assert res.status_code == 200
    result = res.get_json()
    print(result)
    assert len(result["items"]) == 3


def test_search_with_counting_term_succeeds(adminNsfwClient):
    res = _when_searching(adminNsfwClient, "tags<2")
    assert res.status_code == 200
    result = res.get_json()
    print(result)
    assert len(result["items"]) == 1


def test_search_with_counting_term2_succeeds(adminNsfwClient):
    res = _when_searching(adminNsfwClient, "tags<=1")
    assert res.status_code == 200
    result = res.get_json()
    print(result)
    assert len(result["items"]) == 1


def test_search_with_counting_term3_succeeds(adminNsfwClient):
    res = _when_searching(adminNsfwClient, "tags>2")
    assert res.status_code == 200
    result = res.get_json()
    print(result)
    assert len(result["items"]) == 1


def test_search_with_counting_term4_succeeds(adminNsfwClient):
    res = _when_searching(adminNsfwClient, "tags!=0")
    assert res.status_code == 200
    result = res.get_json()
    print(result)
    assert len(result["items"]) >= 3
