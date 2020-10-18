def test_cannot_list_media_without_login(client):
    res = client.get("/media?pageNumber=1&pageSize=10", follow_redirects=True)
    assert res.status_code == 401


def test_can_only_list_s_media_as_user(client, asUser):
    res = client.get("/media?pageNumber=1&pageSize=10", follow_redirects=True)
    assert res.status_code == 200
    json_result = res.get_json()
    assert len(json_result["items"]) == 3


def test_can_list_s_media_as_sfw_admin(client, asAdmin):
    res = client.get("/media?pageNumber=1&pageSize=10", follow_redirects=True)
    assert res.status_code == 200
    assert res.mimetype == "application/json"
    json_result = res.get_json()
    print(res.data)
    print(res.get_json())
    assert len(json_result["items"]) == 3


def test_can_list_all_media_as_nsfw_admin(client, asAdmin, nsfw):
    res = client.get("/media?pageNumber=1&pageSize=10", follow_redirects=True)
    assert res.status_code == 200
    json_result = res.get_json()
    assert len(json_result["items"]) == 5

    # Note that these follow camelCase convention (for JS consumption)
    assert "pageCount" in json_result
    assert "pageNumber" in json_result
    assert "pageSize" in json_result
