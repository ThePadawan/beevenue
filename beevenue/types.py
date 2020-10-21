from abc import ABC
from typing import Set


class TagNamesField(ABC):
    """Flattened in-memory representation of a medium's tags."""

    __slots__ = ["innate", "searchable"]

    innate: Set[str]
    searchable: Set[str]


class MediumDocument(ABC):
    """Flattened in-memory representation of a medium."""

    __slots__ = [
        "medium_id",
        "aspect_ratio",
        "medium_hash",
        "mime_type",
        "rating",
        "tiny_thumbnail",
        "tag_names",
    ]

    medium_id: int
    aspect_ratio: str
    medium_hash: str
    mime_type: str
    rating: str
    tiny_thumbnail: bytes
    tag_names: TagNamesField
