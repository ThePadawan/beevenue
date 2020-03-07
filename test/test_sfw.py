def test_set_sfw(client, asUser):
    res = client.patch("/sfw", json={"sfwSession": False})
    assert res.status_code == 200
