from sqlalchemy.sql import column

from ...spindex.signals import medium_updated
from ...models import Medium, Tag, MediaTags
from ... import db

from . import tags


def update_rating(medium, new_rating):
    # Update rating
    if medium.rating != new_rating and new_rating != "u":
        medium.rating = new_rating
        return True
    return False


def _distinguish(new_tags):
    # Lookup ids for all input tags
    if len(new_tags) == 0:
        existing_tags = []
    else:
        existing_tags = Tag.query.filter(Tag.tag.in_(new_tags)).all()

    existing_tag_id_by_name = {}
    for t in existing_tags:
        existing_tag_id_by_name[t.tag] = t.id

    existing_tag_names = existing_tag_id_by_name.keys()

    # foreach tag not found in database, create tag
    unknown_tag_names = set(new_tags) - set(existing_tag_names)

    return unknown_tag_names, existing_tag_id_by_name.values()


def _autocreate(unknown_tag_names):
    new_tags = []
    need_to_commit = False

    session = db.session()

    for unknown_tag_name in unknown_tag_names:
        needs_to_be_inserted, matching_tag = tags.create(unknown_tag_name)
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


def _ensure(medium, existing_tag_ids, new_tags):
    session = db.session()

    target_tag_ids = set(existing_tag_ids) | set([t.id for t in new_tags])

    # ensure that medium_tags contains exactly that set
    d = MediaTags.delete().where(column("medium_id") == medium.id)
    session.execute(d)
    session.commit()

    values = []
    for tag_id in target_tag_ids:
        values.append({"medium_id": medium.id, "tag_id": tag_id})

    if values:
        insert = MediaTags.insert().values(values)
        session.execute(insert)
        session.commit()


def update_tags(medium, new_tags):
    if new_tags is None:
        return False

    validated_tags = tags.validate(new_tags)

    unknown_tag_names, existing_tag_ids = _distinguish(validated_tags)
    new_tags = _autocreate(unknown_tag_names)
    _ensure(medium, existing_tag_ids, new_tags)

    tags.delete_orphans()


def update_medium(medium_id, new_rating, new_tags):
    maybe_medium = Medium.query.get(medium_id)
    if not maybe_medium:
        return False

    update_rating(maybe_medium, new_rating)
    update_tags(maybe_medium, new_tags)
    medium_updated.send(maybe_medium.id)
    return True
