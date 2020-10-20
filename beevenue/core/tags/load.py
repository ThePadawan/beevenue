from typing import List, Optional, Set, Tuple

from flask import g

from ...models import Medium, Tag
from . import ValidTagName


def get(name: str) -> Optional[Tag]:
    session = g.db
    all_tags: List[Tag] = session.query(Tag).filter_by(tag=name).all()
    if len(all_tags) != 1:
        return None

    return all_tags[0]


def load(
    trimmed_tag_names: List[ValidTagName], medium_ids: Set[int]
) -> Optional[Tuple[Set[Tag], Set[Medium]]]:
    # User submitted no non-empty tag names
    if not trimmed_tag_names:
        return None

    if not medium_ids:
        return None

    all_tags = Tag.query.filter(Tag.tag.in_(trimmed_tag_names)).all()

    # User submitted only tags that don't exist yet.
    # Note: add_batch does not autocreate tags.
    if not all_tags:
        return None

    all_media = Medium.query.filter(Medium.id.in_(medium_ids)).all()

    # User submitted only ids for nonexistant media
    if not all_media:
        return None

    return all_tags, all_media
