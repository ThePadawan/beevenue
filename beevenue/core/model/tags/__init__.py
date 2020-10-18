from typing import Iterable, List, NewType
import re

from ....models import Tag

VALID_TAG_REGEX_INNER = "(?P<category>[a-z]+:)?([a-zA-Z0-9.]+)"
VALID_TAG_REGEX = re.compile(f"^{VALID_TAG_REGEX_INNER}$")

ValidTagName = NewType("ValidTagName", str)


def tag_name_selector(tag: Tag) -> str:
    name: str = tag.tag
    return name


def validate(tag_names: Iterable[str]) -> List[ValidTagName]:
    """
    Filters input iterable such that it only contains valid tag names.
    """
    return [
        ValidTagName(n.strip()) for n in tag_names if VALID_TAG_REGEX.match(n)
    ]
