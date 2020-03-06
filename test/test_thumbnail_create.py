def test_thumbnail_picks_generate(adminNsfwClientWithVideo):
    res = adminNsfwClientWithVideo.get("/medium/5/thumbnail/picks/3")
    assert res.status_code == 200
    assert "thumbs" in res.get_json()


def test_thumbnail_picks_generate_medium_does_not_exist(adminNsfwClient):
    res = adminNsfwClient.get("/medium/5555/thumbnail/picks/3")
    assert res.status_code == 404


def test_thumbnail_picks_generate_medium_is_not_video(adminNsfwClient):
    res = adminNsfwClient.get("/medium/1/thumbnail/picks/3")
    assert res.status_code == 400


def test_thumbnail_picks_pick_succeeds(adminNsfwClientWithVideo):
    res = adminNsfwClientWithVideo.patch("/medium/5/thumbnail/pick/0/3")
    assert res.status_code == 200


def test_thumbnail_picks_pick_medium_does_not_exist(adminNsfwClient):
    res = adminNsfwClient.patch("/medium/5555/thumbnail/pick/0/3")
    assert res.status_code == 404
