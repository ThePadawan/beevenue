from io import BytesIO

from beevenue.core.model.md5sum import md5sum


def _assert_hash_is_now(client, expected_hash_func):
    res = client.get("/medium/3")
    assert res.status_code == 200

    json_result = res.get_json()
    assert expected_hash_func(json_result["hash"])


def test_medium_replace_can_succeed(client, asAdmin, nsfw):
    """Replace the file of a medium, checking if the hash changes from the old to the new one."""

    with open("test/resources/medium_to_be_uploaded.png", "rb") as f:
        contents = f.read()

    expected_hash = md5sum(BytesIO(contents))

    _assert_hash_is_now(client, lambda h: h != expected_hash)

    res = client.patch(
        "/medium/3/file", data={"file": (BytesIO(contents), "example.foo")}
    )
    assert res.status_code == 200

    _assert_hash_is_now(client, lambda h: h == expected_hash)


def test_medium_replace_can_fail_due_to_invalid_mime_type(client, asAdmin, nsfw):
    with open("test/resources/text_file.txt", "rb") as f:
        contents = f.read()

    res = client.patch(
        "/medium/3/file", data={"file": (BytesIO(contents), "example.txt")}
    )
    assert res.status_code == 400


def test_medium_replace_can_fail_due_to_conflicting_medium(client, asAdmin, nsfw):
    """Try to replace a medium file with the same file. This should fail."""

    with open("test/resources/placeholder.jpg", "rb") as f:
        contents = f.read()

    res = client.patch(
        "/medium/3/file", data={"file": (BytesIO(contents), "placeholder.jpg")}
    )
    assert res.status_code == 200
    
    res = client.patch(
        "/medium/3/file", data={"file": (BytesIO(contents), "placeholder.jpg")}
    )
    assert res.status_code == 400
