from typing import Iterable, Optional, Set, Tuple
from sqlalchemy.orm.scoping import scoped_session

from .... import db
from ....models import Tag, Medium, TagAlias
from ....spindex.signals import medium_updated
from . import ValidTagName, validate
from .load import load


def _add_all(
    trimmed_tag_names: Iterable[ValidTagName],
    session: scoped_session,
    tags: Set[Tag],
    media: Set[Medium],
) -> int:
    tags_by_name = {t.tag: t for t in tags}

    added_count = 0
    for tag_name in trimmed_tag_names:
        if tag_name not in tags_by_name:
            # User might have entered a valid, but non-existant tag
            continue

        tag = tags_by_name[tag_name]
        for medium in media:
            if tag not in medium.tags:
                medium.tags.append(tag)
                added_count += 1

    session.commit()

    for medium in media:
        medium_updated.send(medium.id)

    return added_count


def add_batch(tag_names: Iterable[str], medium_ids: Set[int]) -> Optional[int]:
    trimmed_tag_names = validate(tag_names)
    loaded = load(trimmed_tag_names, medium_ids)

    if not loaded:
        return None

    added_count = _add_all(trimmed_tag_names, *loaded)
    return added_count


def create(name: ValidTagName) -> Tuple[bool, Optional[Tag]]:
    """
    Returns tuple of (needs_to_be_inserted, matching_tag)
    """
    session = db.session()

    # Don't create tag if there is another tag that has the same 'name'
    maybe_conflict = session.query(Tag).filter_by(tag=name).first()
    if maybe_conflict:
        return False, None

    # Don't create tag if there is another tag that has 'name' as an alias
    maybe_conflict = session.query(TagAlias).filter_by(alias=name).first()
    if maybe_conflict:
        return False, maybe_conflict.tag

    return True, Tag.create(name)
