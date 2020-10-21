from typing import Iterable, List, Set

from ..models import Medium
from ..types import TagNamesField, MediumDocument


class SpindexedMediumTagNames(TagNamesField):
    """In-memory representation of a medium's tag names."""

    __slots__: List[str] = []

    def __init__(self, innate: Iterable[str], searchable: Iterable[str]):
        self.innate = set(innate)
        self.searchable = set(searchable)


class SpindexedMedium(MediumDocument):
    """In-memory representation of a medium."""

    __slots__: List[str] = []

    @staticmethod
    def create(
        medium: Medium,
        innate_tag_names: Set[str],
        searchable_tag_names: Set[str],
    ) -> "SpindexedMedium":
        """Create in-memory representation of a Medium from the SQL database."""

        return SpindexedMedium(
            medium.id,
            str(medium.aspect_ratio),
            medium.hash,
            medium.mime_type,
            medium.rating,
            medium.tiny_thumbnail,
            SpindexedMediumTagNames(innate_tag_names, searchable_tag_names),
        )

    def __init__(
        self,
        medium_id: int,
        aspect_ratio: str,
        medium_hash: str,
        mime_type: str,
        rating: str,
        tiny_thumbnail: bytes,
        tag_names: SpindexedMediumTagNames,
    ) -> None:
        self.medium_id = medium_id  # pylint: disable=invalid-name
        self.aspect_ratio = aspect_ratio
        self.medium_hash = medium_hash
        self.mime_type = mime_type
        self.rating = rating
        self.tiny_thumbnail = tiny_thumbnail
        self.tag_names = tag_names

    def __str__(self) -> str:
        return f"<SpindexedMedium {self.medium_id}>"

    def __repr__(self) -> str:
        return self.__str__()
