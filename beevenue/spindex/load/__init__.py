from abc import ABC, abstractmethod
from collections import deque
from typing import Iterable, List, Set, Tuple

from ...models import Medium
from ..models import SpindexedMedium


class AbstractDataSource(ABC):
    @abstractmethod
    def alias_names(self, tag_ids: Iterable[int]) -> Set[str]:
        """Returns all names of aliases for the given tag_ids."""

    def implied(self, tag_ids: Iterable[int]) -> Tuple[Set[int], Set[str]]:
        """Returns ids and names of tags implied by the given tag_ids."""


def create_spindexed_medium(
    data_source: AbstractDataSource, medium: Medium
) -> SpindexedMedium:
    # First, get innate tags. These will never change.
    innate_tag_names = set([t.tag for t in medium.tags])

    # Follow chain of implications. Gather implied tags
    # and aliases until that queue is empty.
    extra_searchable_tags = _non_innate_tags(data_source, medium)

    searchable_tag_names = innate_tag_names | extra_searchable_tags

    return SpindexedMedium.create(
        medium, innate_tag_names, searchable_tag_names
    )


def _non_innate_tags(
    data_source: AbstractDataSource, medium: Medium
) -> Set[str]:
    extra: Set[str] = set()

    q: deque = deque()
    initial_tag_ids = set([t.id for t in medium.tags])
    q.append(initial_tag_ids)

    while q:
        tag_ids: List[int] = q.pop()
        if not tag_ids:
            continue

        extra |= data_source.alias_names(tag_ids)

        implied_tag_ids, implied_tag_names = data_source.implied(tag_ids)
        extra |= implied_tag_names

        q.append(implied_tag_ids)

    return extra
