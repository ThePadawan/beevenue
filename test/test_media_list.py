def test_cannot_list_media_without_login(client):
    res = client.get(
        '/media?pageNumber=1&pageSize=10',
        follow_redirects=True)
    assert res.status_code == 401


def test_can_only_list_s_media_as_user(userClient):
    res = userClient.get(
        '/media?pageNumber=1&pageSize=10',
        follow_redirects=True)
    assert res.status_code == 200
    json_result = res.json
    assert len(json_result["items"]) == 3


def test_can_list_s_media_as_sfw_admin(adminClient):
    res = adminClient.get(
        '/media?pageNumber=1&pageSize=10',
        follow_redirects=True)
    assert res.status_code == 200
    json_result = res.json
    assert len(json_result["items"]) == 3


def test_can_list_all_media_as_nsfw_admin(adminNsfwClient):
    res = adminNsfwClient.get(
        '/media?pageNumber=1&pageSize=10',
        follow_redirects=True)
    assert res.status_code == 200
    json_result = res.json
    assert len(json_result["items"]) == 4
