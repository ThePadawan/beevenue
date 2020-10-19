import pytest

from beevenue.core.tags import VALID_TAG_REGEX

invalid_tag_names = ["u:", "c:3:b", ":3", "toradora!", ""]

valid_tag_names = ["u:rwby", "c:ruby.rose", "potato", "X"]


@pytest.mark.parametrize("tag_name", invalid_tag_names)
def test_invalid_tag_names(tag_name):
    actual = VALID_TAG_REGEX.match(tag_name)
    assert actual is None


@pytest.mark.parametrize("tag_name", valid_tag_names)
def test_valid_tag_names(tag_name):
    actual = VALID_TAG_REGEX.match(tag_name)
    assert actual is not None
