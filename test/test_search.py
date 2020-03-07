from urllib import parse
import pytest


def _when_searching(c, query):
    q = parse.urlencode({"q": query, "pageNumber": 1, "pageSize": 10})
    print(q)
    return c.get(f"/search?{q}")


def test_cannot_crash_search_with_weird_int_pagination(client, asUser):
    q = parse.urlencode({"q": "test", "pageNumber": 0, "pageSize": -200})
    print(q)
    res = client.get(f"/search?{q}")
    assert res.status_code != 500


def test_cannot_crash_search_with_invalid_pagination(client, asUser):
    q = parse.urlencode({"q": "test", "pageNumber": "foo", "pageSize": "bar"})
    print(q)
    res = client.get(f"/search?{q}")
    assert res.status_code != 500


def test_search_succeeds_on_unparseable_term(client, asUser):
    res = _when_searching(client, "__foo__?")
    assert res.status_code == 200
    assert "items" in res.get_json()
    assert res.get_json()["items"] == []


def test_search_succeeds_on_whitespace_term(client, asUser):
    res = _when_searching(client, "   ")
    assert res.status_code == 200
    assert "items" in res.get_json()
    assert res.get_json()["items"] == []


def test_search_without_login(client):
    res = client.get("/search")
    assert res.status_code == 401


def test_no_results_has_valid_schema(client, asAdmin):
    res = _when_searching(client, "asdgjhkasgdgas")
    assert res.status_code == 200
    assert "items" in res.get_json()
    assert res.get_json()["items"] == []


def test_search_with_only_negative_terms_succeeds(client, asUser):
    res = _when_searching(client, "-C")
    assert res.status_code == 200
    result = res.get_json()
    assert len(result["items"]) >= 1


def test_search_with_only_exact_terms_succeeds(client, asUser):
    res = _when_searching(client, "+C")
    assert res.status_code == 200
    result = res.get_json()
    assert len(result["items"]) >= 1


identical_group_search_terms = ["utags:1", "utags=1"]
identical_counting_search_terms = ["tags:2", "tags=2"]


@pytest.mark.parametrize("q", identical_group_search_terms)
def test_search_with_category_term_succeeds(client, asUser, q):
    res = _when_searching(client, q)
    assert res.status_code == 200
    result = res.get_json()
    print(result)
    assert len(result["items"]) == 1


@pytest.mark.parametrize("q", identical_counting_search_terms)
def test_search_colon_is_treated_the_same_as_equals(client, asUser, q):
    res = _when_searching(client, q)
    assert res.status_code == 200
    result = res.get_json()
    print(result)
    assert len(result["items"]) == 2


def test_search_with_combined_terms_succeeds(client, asUser):
    res = _when_searching(client, "c:tinkerbell tags>1")
    assert res.status_code == 200
    result = res.get_json()
    print(result)
    assert len(result["items"]) == 1


def test_search_with_alias_term_succeeds(client, asUser):
    res = _when_searching(client, "c:pete c:tinkerbell")
    assert res.status_code == 200
    result = res.get_json()
    print(result)
    assert len(result["items"]) == 1


def test_search_with_rating_term_succeeds(client, asAdmin, nsfw):
    res = _when_searching(client, "rating:s")
    assert res.status_code == 200
    result = res.get_json()
    print(result)
    assert len(result["items"]) == 3


def test_search_with_counting_term_succeeds(client, asAdmin, nsfw):
    res = _when_searching(client, "tags<2")
    assert res.status_code == 200
    result = res.get_json()
    print(result)
    assert len(result["items"]) == 2


def test_search_with_counting_term2_succeeds(client, asAdmin, nsfw):
    res = _when_searching(client, "tags<=1")
    assert res.status_code == 200
    result = res.get_json()
    print(result)
    assert len(result["items"]) == 2


def test_search_with_counting_term3_succeeds(client, asAdmin, nsfw):
    res = _when_searching(client, "tags>2")
    assert res.status_code == 200
    result = res.get_json()
    print(result)
    assert len(result["items"]) == 1


def test_search_with_counting_term4_succeeds(client, asAdmin, nsfw):
    res = _when_searching(client, "tags!=0")
    assert res.status_code == 200
    result = res.get_json()
    print(result)
    assert len(result["items"]) >= 3
