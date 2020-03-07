def test_can_delete_medium_as_admin(client, asAdmin):
    res = client.delete("/medium/3")
    assert res.status_code == 200


def test_cannot_delete_nonexistant_medium_as_admin(client, asAdmin):
    res = client.delete("/medium/9999999")
    assert res.status_code == 404
