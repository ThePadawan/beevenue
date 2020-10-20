def test_cannot_get_e_rated_medium_as_sfw_user(client, asUser):
    res = client.get("/medium/3")
    assert res.status_code == 403


def test_cannot_get_q_rated_medium_as_sfw_user(client, asUser):
    res = client.get("/medium/12")
    assert res.status_code == 400


def test_can_get_q_rated_medium_as_nsfw_user(client, asUser, nsfw):
    res = client.get("/medium/5")
    assert res.status_code == 200


def test_cannot_get_e_rated_medium_as_nsfw_user(client, asUser, nsfw):
    res = client.get("/medium/3")
    assert res.status_code == 403


def test_can_get_s_rated_medium_as_user(client, asUser):
    res = client.get("/medium/1")
    assert res.status_code == 200


def test_cannot_get_missing_medium_as_user(client, asUser):
    res = client.get("/medium/141341")
    assert res.status_code == 404


def test_cannot_get_e_rated_medium_as_admin_in_sfw_mode(client, asAdmin):
    res = client.get("/medium/3")
    assert res.status_code // 100 == 4
