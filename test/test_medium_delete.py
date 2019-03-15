
def test_can_delete_medium_as_admin(adminClient):
    res = adminClient.delete('/medium/3')
    assert res.status_code == 200
