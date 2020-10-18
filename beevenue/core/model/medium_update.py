from typing import Iterable, List, Optional, Set, Tuple

from sqlalchemy.sql import column

from beevenue import request

from . import tags
from ... import db
from ...models import MediaTags, Medium, Tag
from ...spindex.signals import medium_updated
from ...spindex.spindex import SPINDEX
from .detail import MediumDetail
from .media import similar_media
from .tags import ValidTagName
from .tags.delete import delete_orphans
from .tags.new import create


def update_rating(medium: Medium, new_rating: str) -> bool:
    if new_rating not in (medium.rating, "u"):
        medium.rating = new_rating
        return True
    return False


def _distinguish(
    new_tags: List[ValidTagName],
) -> Tuple[Set[ValidTagName], Set[int]]:
    # Lookup ids for all input tags
    if len(new_tags) == 0:
        existing_tags = []
    else:
        existing_tags = Tag.query.filter(Tag.tag.in_(new_tags)).all()

    existing_tag_id_by_name = {}
    for tag in existing_tags:
        existing_tag_id_by_name[tag.tag] = tag.id

    existing_tag_names = existing_tag_id_by_name.keys()

    # foreach tag not found in database, create tag
    unknown_tag_names = set(new_tags) - set(existing_tag_names)

    return unknown_tag_names, set(existing_tag_id_by_name.values())


def _autocreate(unknown_tag_names: Set[ValidTagName]) -> List[Tag]:
    new_tags = []
    need_to_commit = False

    session = db.session()

    for unknown_tag_name in unknown_tag_names:
        needs_to_be_inserted, matching_tag = create(unknown_tag_name)
        if not matching_tag:
            continue
        if needs_to_be_inserted:
            session.add(matching_tag)
            need_to_commit = True
        new_tags.append(matching_tag)

    # We need this to get the ids to insert into MediaTags later!
    if need_to_commit:
        session.commit()

    return new_tags


def _ensure(
    medium: Medium, existing_tag_ids: Set[int], new_tags: Iterable[Tag]
) -> None:
    session = db.session()

    target_tag_ids = existing_tag_ids | {t.id for t in new_tags}

    # ensure that medium_tags contains exactly that set
    stmt = MediaTags.delete().where(column("medium_id") == medium.id)
    session.execute(stmt)
    session.commit()

    values = []
    for tag_id in target_tag_ids:
        values.append({"medium_id": medium.id, "tag_id": tag_id})

    if values:
        insert = MediaTags.insert().values(values)
        session.execute(insert)
        session.commit()


def update_tags(medium: Medium, new_tags: List[str]) -> bool:
    if new_tags is None:
        return False

    validated_tags = tags.validate(new_tags)

    unknown_tag_names, existing_tag_ids = _distinguish(validated_tags)
    created_tags = _autocreate(unknown_tag_names)
    _ensure(medium, existing_tag_ids, created_tags)

    delete_orphans()
    return True


def update_medium(
    medium_id: int, new_rating: str, new_tags: List[str]
) -> Optional[MediumDetail]:
    maybe_medium = Medium.query.get(medium_id)
    if not maybe_medium:
        return None

    update_rating(maybe_medium, new_rating)
    update_tags(maybe_medium, new_tags)
    medium_updated.send(maybe_medium.id)

    result = SPINDEX.get_medium(maybe_medium.id)

    if not result:
        return None

    return MediumDetail(result, similar_media(request.beevenue_context, result))
