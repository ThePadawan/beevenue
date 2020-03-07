def test_can_get_tag_similarity_chart(client, asAdmin):
    res = client.get("/tags/similarity")
    assert res.status_code == 200
    assert "links" in res.get_json()
    assert "nodes" in res.get_json()


def test_can_get_tag_similarity_chart_as_user(client, asUser):
    res = client.get("/tags/similarity")
    assert res.status_code == 200
    assert "links" in res.get_json()
    assert "nodes" in res.get_json()


def test_can_get_tag_similarity_chart_as_nsfw_user(client, asUser, nsfw):
    res = client.get("/tags/similarity")
    assert res.status_code == 200
    assert "links" in res.get_json()
    assert "nodes" in res.get_json()


def test_can_get_tag_implications_chart(client, asAdmin):
    res = client.get("/tags/implications")
    assert res.status_code == 200
    assert "links" in res.get_json()
    assert "nodes" in res.get_json()


def test_can_get_tag_implications_chart_as_user(client, asUser):
    res = client.get("/tags/implications")
    assert res.status_code == 200
    assert "links" in res.get_json()
    assert "nodes" in res.get_json()
