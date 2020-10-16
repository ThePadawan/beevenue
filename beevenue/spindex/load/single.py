from typing import Iterable, Optional, Set, Tuple

from sqlalchemy.orm.scoping import scoped_session

from . import AbstractDataSource, create_spindexed_medium
from ... import db
from ...models import Medium, Tag, TagAlias, TagImplication
from ..models import SpindexedMedium


class _SingleLoadDataSource(AbstractDataSource):
    def __init__(self, session: scoped_session):
        self.session = session

    def alias_names(self, tag_ids: Iterable[int]) -> Set[str]:
        tag_alias_entities = (
            self.session.query(TagAlias)
            .filter(TagAlias.tag_id.in_(tag_ids))
            .with_entities(TagAlias.alias)
            .all()
        )

        return set([t[0] for t in tag_alias_entities])

    def implied(self, tag_ids: Iterable[int]) -> Tuple[Set[int], Set[str]]:
        implied_tag_id_entities = (
            self.session.query(TagImplication)
            .filter(TagImplication.c.implying_tag_id.in_(tag_ids))
            .with_entities(TagImplication.c.implied_tag_id)
            .all()
        )
        implied_tag_ids = set([t[0] for t in implied_tag_id_entities])

        implied_tag_name_entities = (
            self.session.query(Tag)
            .filter(Tag.id.in_(implied_tag_ids))
            .with_entities(Tag.tag)
            .all()
        )
        implied_tag_names = set([t[0] for t in implied_tag_name_entities])

        return implied_tag_ids, implied_tag_names


def single_load(id: int) -> Optional[SpindexedMedium]:
    session = db.session()

    matching_media = session.query(Medium).filter_by(id=id).all()
    if not matching_media:
        return None

    matching_medium = matching_media[0]

    return create_spindexed_medium(
        _SingleLoadDataSource(session), matching_medium
    )
