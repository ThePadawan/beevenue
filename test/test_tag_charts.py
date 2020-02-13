def test_can_get_tag_similarity_chart(adminClient):
    res = adminClient.get("/tags/similarity")
    assert res.status_code == 200
    assert "links" in res.get_json()
    assert "nodes" in res.get_json()


def test_can_get_tag_implications_chart(adminClient):
    res = adminClient.get("/tags/implications")
    assert res.status_code == 200
    assert "links" in res.get_json()
    assert "nodes" in res.get_json()
