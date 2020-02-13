def test_cannot_get_e_rated_medium_as_user(userClient):
    res = userClient.get("/medium/3")
    assert res.status_code == 403


def test_can_get_s_rated_medium_as_user(userClient):
    res = userClient.get("/medium/1")
    assert res.status_code == 200


def test_can_get_missing_medium_as_user(userClient):
    res = userClient.get("/medium/141341")
    assert res.status_code == 404


def test_cannot_get_e_rated_medium_as_admin_in_sfw_mode(adminClient):
    res = adminClient.get("/medium/3")
    assert res.status_code // 100 == 4
