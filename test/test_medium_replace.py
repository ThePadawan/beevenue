from io import BytesIO

import pytest

from beevenue.core.model.md5sum import md5sum


def _assert_hash_is_now(client, expected_hash_func):
    res = client.get("/medium/3")
    assert res.status_code == 200

    json_result = res.get_json()
    assert expected_hash_func(json_result["hash"])


def test_medium_replace_fails_without_file(client, asAdmin, nsfw):
    res = client.patch("/medium/3/file", data={})
    assert res.status_code == 400


def test_medium_replace_fails_on_nonexistant_medium(client, asAdmin, nsfw):
    with open(f"test/resources/medium_to_be_uploaded.png", "rb") as f:
        contents = f.read()

    res = client.patch(
        "/medium/12345/file", data={"file": (BytesIO(contents), "example.foo")}
    )
    assert res.status_code == 400


@pytest.mark.parametrize("local_file", ["tall.png", "wide.png"])
def test_medium_replace_can_succeed(client, asAdmin, nsfw, local_file):
    """Replace the file of a medium, checking if the hash changes from the old to the new one."""

    with open(f"test/resources/{local_file}", "rb") as f:
        contents = f.read()

    expected_hash = md5sum(BytesIO(contents))

    _assert_hash_is_now(client, lambda h: h != expected_hash)

    res = client.patch(
        "/medium/3/file", data={"file": (BytesIO(contents), "example.foo")}
    )
    assert res.status_code == 200

    _assert_hash_is_now(client, lambda h: h == expected_hash)


def test_medium_replace_can_fail_due_to_invalid_mime_type(
    client, asAdmin, nsfw
):
    with open("test/resources/text_file.txt", "rb") as f:
        contents = f.read()

    res = client.patch(
        "/medium/3/file", data={"file": (BytesIO(contents), "example.txt")}
    )
    assert res.status_code == 400


def test_medium_replace_can_fail_due_to_conflicting_medium(
    client, asAdmin, nsfw
):
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
