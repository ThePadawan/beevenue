from collections import defaultdict
from itertools import groupby
from typing import Tuple
import re

from .... import db
from ....models import Tag, TagAlias, MediaTags, Medium, TagImplication
from ....spindex.signals import tag_renamed, medium_updated

from .censorship import Censorship

VALID_TAG_REGEX_INNER = "(?P<category>[a-z]+:)?([a-zA-Z0-9.]+)"
VALID_TAG_REGEX = re.compile(f"^{VALID_TAG_REGEX_INNER}$")


def get(name):
    session = db.session()
    all_tags = session.query(Tag).filter_by(tag=name).all()
    if len(all_tags) != 1:
        return None

    return all_tags[0]


def get_all_implications():
    session = db.session()
    all_rows = session.query(TagImplication).all()

    if not all_rows:
        return {"nodes": {}, "links": {}}

    all_tag_ids = set()
    for row in all_rows:
        all_tag_ids.add(row.implying_tag_id)
        all_tag_ids.add(row.implied_tag_id)

    tag_names = session.query(Tag).filter(Tag.id.in_(all_tag_ids)).all()
    tag_dict = {t.id: t for t in tag_names}

    censoring = Censorship(tag_dict, lambda t: t.tag)

    edges = {}
    for left_id, rows in groupby(all_rows, lambda r: r.implying_tag_id):
        left = censoring.get_name(left_id)
        right = [censoring.get_name(r.implied_tag_id) for r in rows]
        edges[left] = right

    nodes = {}
    for id in all_tag_ids:
        nodes[censoring.get_name(id)] = {}

    return {"nodes": nodes, "links": edges}


def _get_similarities(censoring, grouped_media_ids):
    similarities = {}
    for tag1_id, media1_ids in grouped_media_ids.items():
        similarity_row = {}

        for tag2_id, media2_ids in grouped_media_ids.items():
            if tag1_id == tag2_id:
                continue

            intersection_size = len(media1_ids & media2_ids)

            if intersection_size == 0:
                continue

            union_size = len(media1_ids | media2_ids)
            similarity = float(intersection_size) / float(union_size)

            similarity_row[censoring.get_name(tag2_id)] = {
                "similarity": similarity,
                "relevance": union_size,
            }

        similarities[censoring.get_name(tag1_id)] = similarity_row

    return similarities


def get_similarity_matrix():
    session = db.session()

    all_tags = session.query(Tag).all()
    tag_dict = {t.id: t for t in all_tags}

    media_tags = session.query(MediaTags).all()
    grouped_media_ids = defaultdict(set)

    for mt in media_tags:
        grouped_media_ids[mt.tag_id].add(mt.medium_id)

    censoring = Censorship(tag_dict, lambda t: t.tag)

    nodes = {
        censoring.get_name(k): {"size": len(v)} for k, v in grouped_media_ids.items()
    }

    similarities = _get_similarities(censoring, grouped_media_ids)

    return {"nodes": nodes, "links": similarities}


def validate(tag_names):
    """
    Filters input iterable such that it only contains valid tag names.
    """
    return [n.strip() for n in tag_names if VALID_TAG_REGEX.match(n)]


def _load(trimmed_tag_names, medium_ids):
    # User submitted no non-empty tag names
    if not trimmed_tag_names:
        return None

    if not medium_ids:
        return None

    session = db.session()
    all_tags = Tag.query.filter(Tag.tag.in_(trimmed_tag_names)).all()

    # User submitted only tags that don't exist yet.
    # Note: add_batch does not autocreate tags.
    if not all_tags:
        return None

    # load media by ids
    all_media = Medium.query.filter(Medium.id.in_(medium_ids)).all()

    # User submitted only ids for nonexistant media
    if not all_media:
        return None

    return session, all_tags, all_media


def _add_all(trimmed_tag_names, session, tags, media):
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


def add_batch(tag_names, medium_ids):
    trimmed_tag_names = validate(tag_names)
    loaded = _load(trimmed_tag_names, medium_ids)

    if not loaded:
        return None

    added_count = _add_all(trimmed_tag_names, *loaded)
    return len(trimmed_tag_names), added_count


def create(name):
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


def delete_orphans():
    session = db.session()

    tags_to_delete = (
        session.query(Tag)
        .outerjoin(MediaTags)
        .filter(MediaTags.c.tag_id.is_(None))
        .all()
    )

    def is_deletable(tag):
        return len(tag.implying_this) == 0 and len(tag.aliases) == 0

    tags_to_delete = [t for t in tags_to_delete if is_deletable(t)]

    for t in tags_to_delete:
        session.delete(t)

    if tags_to_delete:
        session.commit()


def _rename(session, old_tag: Tag, new_name: str) -> Tuple[str, bool]:
    if not new_name:
        return "You must specify a new name", False

    old_name = old_tag.tag

    new_tags = session.query(Tag).filter(Tag.tag == new_name).all()

    if len(new_tags) < 1:
        # New tag doesn't exist yet. We can simply rename "old_tag".
        old_tag.tag = new_name
        tag_renamed.send((old_name, new_name,))
        return "Successfully renamed tag", True

    new_tag = new_tags[0]

    # if new_tag does exist, UPDATE all medium tags
    # to reference new_tag instead of old_tag, then remove old_tag
    MediaTags.update().where(MediaTags.c.tag_id == old_tag.id).values(tag_id=new_tag.id)

    session.delete(old_tag)

    tag_renamed.send((old_name, new_name,))
    return "Successfully renamed tag", True


def update(tag_name: str, new_model: dict) -> None:
    session = db.session()
    tag = session.query(Tag).filter(Tag.tag == tag_name).first()

    if not tag:
        return False, "Could not find tag with that name"

    if "tag" in new_model:
        msg, success = _rename(session, tag, new_model["tag"])
        if not success:
            return False, msg

    if "rating" in new_model:
        rating = new_model["rating"]
        if rating not in ("s", "q", "e"):
            return False, "Please specify a valid rating"

        tag.rating = rating

    session.commit()
    return True, tag
