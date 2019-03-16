
def test_cannot_update_medium_without_logging_in(client):
    res = client.patch('/medium/3')
    assert res.status_code == 401


def test_cannot_update_medium_as_user(userClient):
    res = userClient.patch('/medium/3')
    assert res.status_code == 403


def test_can_update_medium_as_admin(adminClient):
    res = adminClient.patch('/medium/3', json={
        'rating': 'q',
        'tags': [' some_new_tag   ', 'A']
    })
    assert res.status_code == 200


def test_cant_update_medium_to_unknown_rating(adminNsfwClient):
    res = adminNsfwClient.patch('/medium/3', json={
        'rating': 'u',
        'tags': ['A']
    })
    assert res.status_code == 200

    res = adminNsfwClient.get('/medium/3')
    assert res.status_code == 200
    json_result = res.json
    assert json_result["rating"] == 'e'


def test_cant_update_medium_to_same_rating(adminNsfwClient):
    res = adminNsfwClient.patch('/medium/3', json={
        'rating': 'e',
        'tags': ['A']
    })
    assert res.status_code == 200


def test_cant_update_missing_medium(adminNsfwClient):
    res = adminNsfwClient.patch('/medium/233', json={
        'rating': 'e',
        'tags': ['A']
    })
    assert res.status_code == 400


def test_not_specifiying_tags_means_leave_them_as_is(adminNsfwClient):
    res = adminNsfwClient.patch('/medium/2', json={
        'rating': 'q'
    })
    assert res.status_code == 200
    res = adminNsfwClient.get('/medium/2')
    assert res.status_code == 200
    json_result = res.json
    assert len(json_result["tags"]) > 0


def test_specifiying_empty_tags_means_remove_all(adminNsfwClient):
    res = adminNsfwClient.patch('/medium/2', json={
        'rating': 'q',
        'tags': []
    })
    assert res.status_code == 200
    res = adminNsfwClient.get('/medium/2')
    assert res.status_code == 200
    json_result = res.json
    assert len(json_result["tags"]) == 0


def test_can_update_medium_with_duplicate_tags(adminClient):
    res = adminClient.patch('/medium/3', json={
        'rating': 'q',
        'tags': ['new_tag', 'new_tag', 'c:pete']
    })
    assert res.status_code == 200
