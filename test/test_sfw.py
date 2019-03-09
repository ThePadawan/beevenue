def test_set_sfw(userClient):
    res = userClient.patch('/sfw', json={
        'sfwSession': False
    })
    assert res.status_code == 200
