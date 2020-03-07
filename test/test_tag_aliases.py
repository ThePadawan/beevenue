def test_can_add_and_remove_alias_as_admin(client, asAdmin):
    res = client.post("/tag/c:tinkerbell/aliases/c:tink")
    assert res.status_code == 200
    res = client.delete("/tag/c:tinkerbell/aliases/c:tink")
    assert res.status_code == 200


def test_cant_add_alias_to_missing_tag(client, asAdmin):
    res = client.post("/tag/potato.famine/aliases/the.big.famine")
    assert res.status_code == 400


def test_cant_remove_alias_from_missing_tag(client, asAdmin):
    res = client.delete("/tag/potato.famine/aliases/the.big.famine")
    assert res.status_code == 200


def test_cant_remove_missing_alias_from_tag(client, asAdmin):
    res = client.delete("/tag/c:tinkerbell/aliases/c:tinkybinky")
    assert res.status_code == 200


def test_cant_add_duplicate_alias_to_multiple_tags(client, asAdmin):
    res = client.post("/tag/c:tinkerbell/aliases/c:that.one")
    assert res.status_code == 200
    res = client.post("/tag/c:peter/aliases/c:that.one")
    assert res.status_code == 400


def test_cant_add_alias_with_current_tag_name(client, asAdmin):
    res = client.post("/tag/c:tinkerbell/aliases/c:peter")
    assert res.status_code == 400
