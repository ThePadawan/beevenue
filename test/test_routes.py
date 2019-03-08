
# def test_present_tag_returns_200(client):
#     res = client.get('/tags/u:overwatch')
#     assert res.status_code == 200


def test_missing_tag_returns_404(client):
    res = client.get('/tags/someUnknownTag')
    assert res.status_code == 404
