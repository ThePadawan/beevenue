import pytest
import subprocess


def test_thumbnail_picks_generate(client, asAdmin, nsfw, withVideo):
    res = client.get(f"/medium/{withVideo['medium_id']}/thumbnail/picks/3")
    assert res.status_code == 200
    assert "thumbs" in res.get_json()


def test_thumbnail_picks_generate_with_broken_ffmpeg(
    client, asAdmin, nsfw, withVideo, monkeypatch
):
    def fake_run(*args, **kwargs):
        class FakeResult:
            stderr = ""

        return FakeResult()

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(Exception):
        res = client.get(f"/medium/{withVideo['medium_id']}/thumbnail/picks/3")


def test_thumbnail_picks_generate_medium_does_not_exist(client, asAdmin, nsfw):
    res = client.get("/medium/5555/thumbnail/picks/3")
    assert res.status_code == 404


def test_thumbnail_picks_generate_medium_is_not_video(client, asAdmin, nsfw):
    res = client.get("/medium/1/thumbnail/picks/3")
    assert res.status_code == 400


def test_thumbnail_picks_pick_succeeds(client, asAdmin, nsfw, withVideo):
    res = client.patch(f"/medium/{withVideo['medium_id']}/thumbnail/pick/0/3")
    assert res.status_code == 200


def test_thumbnail_picks_pick_medium_does_not_exist(client, asAdmin, nsfw):
    res = client.patch("/medium/5555/thumbnail/pick/0/3")
    assert res.status_code == 404
