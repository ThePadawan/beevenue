
def test_cannot_delete_orphan_tags_without_login(client):
    res = client.delete('/tags/orphans')
    assert res.status_code == 401


def test_cannot_delete_orphan_tags_as_user(userClient):
    res = userClient.delete('/tags/orphans')
    assert res.status_code == 403


def test_can_delete_orphan_tags_as_admin(adminClient):
    res = adminClient.delete('/tags/orphans')
    assert res.status_code == 200
