from typing import Iterable, Set

from ..models import Medium


class SpindexedMediumTagNames(object):
    def __init__(self, innate: Iterable[str], searchable: Iterable[str]):
        self.innate = set(innate)
        self.searchable = set(searchable)


class SpindexedMedium(object):
    @staticmethod
    def create(
        medium: Medium,
        innate_tag_names: Set[str],
        searchable_tag_names: Set[str],
    ) -> "SpindexedMedium":
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
        id: int,
        aspect_ratio: str,
        hash: str,
        mime_type: str,
        rating: str,
        tiny_thumbnail: bytes,
        tag_names: SpindexedMediumTagNames,
    ) -> None:
        self.id = id
        self.aspect_ratio = aspect_ratio
        self.hash = hash
        self.mime_type = mime_type
        self.rating = rating
        self.tiny_thumbnail = tiny_thumbnail
        self.tag_names = tag_names

    def __str__(self) -> str:
        return f"<SpindexedMedium {self.id}>"

    def __repr__(self) -> str:
        return self.__str__()
