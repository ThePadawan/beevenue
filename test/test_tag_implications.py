def test_can_add_and_remove_implications_as_admin(adminClient):
    res = adminClient.patch('/tag/c:tinkerbell/implications/A')
    assert res.status_code == 200
    res = adminClient.delete('/tag/c:tinkerbell/aliases/A')
    assert res.status_code == 200


def test_cant_add_missing_implication(adminClient):
    res = adminClient.patch('/tag/c:tinkerbell/implications/nothing')
    assert res.status_code == 400


def test_cant_add_duplicate_to_current_implication(adminClient):
    res = adminClient.patch('/tag/c:tinkerbell/implications/A')
    assert res.status_code == 200
    res = adminClient.patch('/tag/c:tinkerbell/implications/A')
    assert res.status_code == 200


def test_cant_add_implication_cycle(adminClient):
    res = adminClient.patch('/tag/c:tinkerbell/implications/A')
    assert res.status_code == 200
    res = adminClient.patch('/tag/A/implications/c:tinkerbell')
    assert res.status_code == 400


def test_can_simplify_implications(adminClient):
    res = adminClient.patch('/tag/u:peter.pan/clean')
    assert res.status_code == 200
