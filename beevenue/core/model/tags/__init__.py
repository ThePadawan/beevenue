from collections import defaultdict
import re

from ....models import Tag, TagAlias, MediaTags, Medium

from ....spindex.signals import tag_renamed

VALID_TAG_REGEX_INNER = "(?P<category>[a-z]+:)?([a-zA-Z0-9.]+)"
VALID_TAG_REGEX = re.compile(f"^{VALID_TAG_REGEX_INNER}$")


def get(context, name):
    session = context.session()
    all_tags = session.query(Tag).filter_by(tag=name).all()
    if len(all_tags) != 1:
        return None

    return all_tags[0]


def get_similarity_matrix(context):
    session = context.session()

    tag_names = session.query(Tag).all()

    tag_name_dict = {t.id: t.tag for t in tag_names}

    media_tags = session.query(MediaTags).all()

    grouped_media_ids = defaultdict(set)

    for mt in media_tags:
        grouped_media_ids[mt.tag_id].add(mt.medium_id)

    nodes = {tag_name_dict[k]: {"size": len(v)} for k, v in grouped_media_ids.items()}

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

            similarity_row[tag_name_dict[tag2_id]] = {
                "similarity": similarity,
                "relevance": union_size
            }

        similarities[tag_name_dict[tag1_id]] = similarity_row

    return {"nodes": nodes, "links": similarities}


def validate(tag_names):
    """
    Filters input iterable such that it only contains valid tag names.
    """
    return [n.strip() for n in tag_names if VALID_TAG_REGEX.match(n)]


def add_batch(context, tag_names, medium_ids):
    trimmed_tag_names = validate(tag_names)

    # User submitted no non-empty tag names
    if not trimmed_tag_names:
        return True

    if not medium_ids:
        return True

    session = context.session()
    all_tags = session.query(Tag).filter(Tag.tag.in_(trimmed_tag_names)).all()

    # User submitted only tags that don't exist yet.
    # Note: add_batch does not autocreate tags.
    if not all_tags:
        return True

    # load media by ids
    all_media = session.query(Medium).filter(Medium.id.in_(medium_ids)).all()

    # User submitted only ids for nonexistant media
    if not all_media:
        return True

    tags_by_name = {t.tag: t for t in all_tags}

    for tag_name in trimmed_tag_names:
        tag = tags_by_name[tag_name]
        for medium in all_media:
            if tag not in medium.tags:
                medium.tags.append(tag)

    session.commit()
    return True


def create(session, name):
    # Don't create tag if there is another tag that has the same 'name'
    maybe_conflict = session.query(Tag).filter_by(tag=name).first()
    if maybe_conflict:
        return False

    # Don't create tag if there is another tag that has 'name' as an alias
    maybe_conflict = session.query(TagAlias).filter_by(alias=name).first()
    if maybe_conflict:
        return False

    return Tag.create(name)


def get_statistics(context):
    session = context.session()
    all_tags = session.query(Tag).all()
    return all_tags


def delete_orphans(context):
    session = context.session()

    tags_to_delete = session.query(Tag).outerjoin(MediaTags)\
        .filter(MediaTags.c.tag_id.is_(None))\
        .all()

    # Only delete tags if they're not implied by anything
    def is_deletable(tag):
        return len(tag.implying_this) == 0

    tags_to_delete = [t for t in tags_to_delete if is_deletable(t)]

    for t in tags_to_delete:
        session.delete(t)

    if tags_to_delete:
        session.commit()


def rename(context, old_name, new_name):
    if not new_name:
        return "You must specify a new name", False

    session = context.session()

    old_tags = session.query(Tag).filter(Tag.tag == old_name).all()

    if len(old_tags) != 1:
        return "Could not find tag with that name", False

    old_tag = old_tags[0]

    new_tags = session.query(Tag).filter(Tag.tag == new_name).all()

    if len(new_tags) < 1:
        # New tag doesn't exist yet. We can simply rename "old_tag".
        old_tag.tag = new_name
        session.commit()
        tag_renamed.send((old_name, new_name,))
        return "Successfully renamed tag", True

    new_tag = new_tags[0]

    # if new_tag does exist, UPDATE all medium tags
    # to reference new_tag instead of old_tag, then remove old_tag
    MediaTags.update().where(MediaTags.c.tag_id == old_tag.id)\
        .values(tag_id=new_tag.id)

    session.delete(old_tag)
    session.commit()

    tag_renamed.send((old_name, new_name,))
    return "Successfully renamed tag", True
