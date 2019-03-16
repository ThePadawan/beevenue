from ....models import Tag, TagAlias, MediaTags

from . import aliases, implications


def get(context, name):
    session = context.session()
    all_tags = session.query(Tag).filter_by(tag=name).all()
    if len(all_tags) != 1:
        return None

    return all_tags[0]


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
        old_tag.tag = new_name
        session.commit()
        return "Successfully renamed tag", True

    new_tag = new_tags[0]

    # if new_tag does exist, UPDATE all medium tags
    # to reference new_tag instead of old_tag, then remove old_tag
    MediaTags.update().where(MediaTags.c.tag_id == old_tag.id)\
        .values(tag_id=new_tag.id)

    session.delete(old_tag)
    session.commit()
    return "Successfully renamed tag", True
