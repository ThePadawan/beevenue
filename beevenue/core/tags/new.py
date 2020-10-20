from typing import Iterable, Optional, Set, Tuple

from flask import g

from ...models import Tag, Medium, TagAlias
from ...signals import medium_updated
from . import ValidTagName, validate
from .load import load


def _add_all(
    trimmed_tag_names: Iterable[ValidTagName],
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

    g.db.commit()

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


def create(name: ValidTagName) -> Tuple[bool, Tag]:
    """Return tuple of (needs_to_be_inserted, matching_tag)."""

    # Don't create tag if there is another tag that has 'name' as an alias
    maybe_conflict = g.db.query(TagAlias).filter_by(alias=name).first()
    if maybe_conflict:
        return False, maybe_conflict.tag

    return True, Tag.create(name)  # type: ignore
