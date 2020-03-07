def test_thumbnail_picks_generate(client, asAdmin, nsfw, withVideo):
    res = client.get("/medium/6/thumbnail/picks/3")
    assert res.status_code == 200
    assert "thumbs" in res.get_json()


def test_thumbnail_picks_generate_medium_does_not_exist(client, asAdmin, nsfw):
    res = client.get("/medium/5555/thumbnail/picks/3")
    assert res.status_code == 404


def test_thumbnail_picks_generate_medium_is_not_video(client, asAdmin, nsfw):
    res = client.get("/medium/1/thumbnail/picks/3")
    assert res.status_code == 400


def test_thumbnail_picks_pick_succeeds(client, asAdmin, nsfw, withVideo):
    res = client.patch("/medium/6/thumbnail/pick/0/3")
    assert res.status_code == 200


def test_thumbnail_picks_pick_medium_does_not_exist(client, asAdmin, nsfw):
    res = client.patch("/medium/5555/thumbnail/pick/0/3")
    assert res.status_code == 404
