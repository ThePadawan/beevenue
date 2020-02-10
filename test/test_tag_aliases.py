def test_can_add_and_remove_alias_as_admin(adminClient):
    res = adminClient.post("/tag/c:tinkerbell/aliases/c:tink")
    assert res.status_code == 200
    res = adminClient.delete("/tag/c:tinkerbell/aliases/c:tink")
    assert res.status_code == 200


def test_cant_add_alias_to_missing_tag(adminClient):
    res = adminClient.post("/tag/potato.famine/aliases/the.big.famine")
    assert res.status_code == 400


def test_cant_remove_alias_from_missing_tag(adminClient):
    res = adminClient.delete("/tag/potato.famine/aliases/the.big.famine")
    assert res.status_code == 200


def test_cant_remove_missing_alias_from_tag(adminClient):
    res = adminClient.delete("/tag/c:tinkerbell/aliases/c:tinkybinky")
    assert res.status_code == 200


def test_cant_add_duplicate_alias_to_multiple_tags(adminClient):
    res = adminClient.post("/tag/c:tinkerbell/aliases/c:that.one")
    assert res.status_code == 200
    res = adminClient.post("/tag/c:peter/aliases/c:that.one")
    assert res.status_code == 400


def test_cant_add_alias_with_current_tag_name(adminClient):
    res = adminClient.post("/tag/c:tinkerbell/aliases/c:peter")
    assert res.status_code == 400
