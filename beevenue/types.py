from abc import ABC
from typing import Set


class TagNamesField(ABC):
    """Flattened in-memory representation of a medium's tags."""

    innate: Set[str]
    searchable: Set[str]


class MediumDocument(ABC):
    """Flattened in-memory representation of a medium."""

    medium_id: int
    aspect_ratio: str
    medium_hash: str
    mime_type: str
    rating: str
    tiny_thumbnail: bytes
    tag_names: TagNamesField
