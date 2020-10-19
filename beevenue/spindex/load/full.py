from collections import defaultdict
from typing import Dict, Iterable, Set, Tuple

from flask import g

from . import AbstractDataSource, create_spindexed_medium
from ...models import Medium, Tag, TagAlias, TagImplication


class _FullLoadDataSource(AbstractDataSource):
    def __init__(
        self,
        implied_by_this: Dict[int, Set[int]],
        aliases_by_id: Dict[int, Set[str]],
        tag_name_by_id: Dict[int, str],
    ):
        self.implied_by_this = implied_by_this
        self.aliases_by_id = aliases_by_id
        self.tag_name_by_id = tag_name_by_id

    def alias_names(self, tag_ids: Iterable[int]) -> Set[str]:
        result = set()
        for tag_id in tag_ids:
            result |= self.aliases_by_id[tag_id]
        return result

    def implied(self, tag_ids: Iterable[int]) -> Tuple[Set[int], Set[str]]:
        implied_ids = set()
        for tag_id in tag_ids:
            implied_ids |= self.implied_by_this[tag_id]

        implied_names = {self.tag_name_by_id[i] for i in implied_ids}

        return implied_ids, implied_names


def full_load() -> None:
    session = g.db
    all_media = Medium.query.all()

    all_implications = session.query(TagImplication).all()

    all_tags = session.query(Tag).all()
    tag_name_by_id = {t.id: t.tag for t in all_tags}

    # if Id=3 implies Id=5, implied_by_this[3] == set([5])
    implied_by_this = defaultdict(set)

    for i in all_implications:
        implied_by_this[i.implying_tag_id].add(i.implied_tag_id)

    all_aliases = session.query(TagAlias).all()

    aliases_by_id = defaultdict(set)
    for alias in all_aliases:
        aliases_by_id[alias.tag_id].add(alias.alias)

    media_to_cache = []

    data_source = _FullLoadDataSource(
        implied_by_this, aliases_by_id, tag_name_by_id
    )

    for medium in all_media:
        medium_to_cache = create_spindexed_medium(data_source, medium)
        media_to_cache.append(medium_to_cache)

    g.spindex.add_media(media_to_cache)
