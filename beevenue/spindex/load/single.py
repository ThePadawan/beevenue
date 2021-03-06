from typing import Iterable, Optional, Set, Tuple

from flask import g

from . import AbstractDataSource, create_spindexed_medium
from ...models import Medium, Tag, TagAlias, TagImplication
from ...types import MediumDocument


class _SingleLoadDataSource(AbstractDataSource):
    def __init__(self) -> None:
        self.session = g.db

    def alias_names(self, tag_ids: Iterable[int]) -> Set[str]:
        tag_alias_entities = (
            self.session.query(TagAlias)
            .filter(TagAlias.tag_id.in_(tag_ids))
            .with_entities(TagAlias.alias)
            .all()
        )

        return {t[0] for t in tag_alias_entities}

    def implied(self, tag_ids: Iterable[int]) -> Tuple[Set[int], Set[str]]:
        implied_tag_id_entities = (
            self.session.query(TagImplication)
            .filter(TagImplication.c.implying_tag_id.in_(tag_ids))
            .with_entities(TagImplication.c.implied_tag_id)
            .all()
        )
        implied_tag_ids = {t[0] for t in implied_tag_id_entities}

        implied_tag_name_entities = (
            self.session.query(Tag)
            .filter(Tag.id.in_(implied_tag_ids))
            .with_entities(Tag.tag)
            .all()
        )
        implied_tag_names = {t[0] for t in implied_tag_name_entities}

        return implied_tag_ids, implied_tag_names


def single_load(medium_id: int) -> Optional[MediumDocument]:
    matching_medium = g.db.query(Medium).filter_by(id=medium_id).first()
    return create_spindexed_medium(_SingleLoadDataSource(), matching_medium)
