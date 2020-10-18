def test_can_add_and_remove_implications_as_admin(client, asAdmin):
    res = client.patch("/tag/c:tinkerbell/implications/A")
    assert res.status_code == 200
    res = client.delete("/tag/c:tinkerbell/implications/A")
    assert res.status_code == 200


def test_cant_add_missing_implication(client, asAdmin):
    res = client.patch("/tag/c:tinkerbell/implications/nothing")
    assert res.status_code == 400


def test_cant_add_duplicate_to_current_implication(client, asAdmin):
    res = client.patch("/tag/c:tinkerbell/implications/A")
    assert res.status_code == 200
    res = client.patch("/tag/c:tinkerbell/implications/A")
    assert res.status_code == 200


def test_cant_add_implication_cycle(client, asAdmin):
    res = client.patch("/tag/c:tinkerbell/implications/A")
    assert res.status_code == 200
    res = client.patch("/tag/A/implications/c:tinkerbell")
    assert res.status_code == 400


def test_cant_add_implication_three_cycle(client, asAdmin):
    res = client.patch("/tag/A/implications/B")
    assert res.status_code == 200
    res = client.patch("/tag/B/implications/C")
    assert res.status_code == 200
    res = client.patch("/tag/C/implications/A")
    assert res.status_code == 400


def test_can_add_implication_three_chain(client, asAdmin):
    res = client.patch("/tag/A/implications/B")
    assert res.status_code == 200
    res = client.patch("/tag/B/implications/C")
    assert res.status_code == 200


def test_removing_implication_for_missing_tag_succeeds(client, asAdmin):
    res = client.delete("/tag/c:tinkerbell/implications/nothing")
    assert res.status_code == 200


def test_removing_missing_implication_succeeds(client, asAdmin):
    res = client.delete("/tag/c:tinkerbell/implications/A")
    assert res.status_code == 200
