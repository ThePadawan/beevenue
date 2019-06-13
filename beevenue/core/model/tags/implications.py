from sqlalchemy import or_, and_
from sqlalchemy.sql import func

from ....models import Tag, TagImplication, MediaTags


def _identify_implication_tags(session, implying, implied):
    implying_tags = session.query(Tag).filter(Tag.tag == implying).all()
    implied_tags = session.query(Tag).filter(Tag.tag == implied).all()
    if len(implying_tags) != 1 or len(implied_tags) != 1:
        return False, "Could not find both tags"

    return True, (implying_tags[0], implied_tags[0])


def _would_create_implication_chain(session, implying_tag, implied_tag):
    # * Does "implied" imply something?
    # * Does something imply "implying"?
    q = \
        session.query(TagImplication)\
        .filter(or_(TagImplication.c.implying_tag_id == implied_tag.id,
                    TagImplication.c.implied_tag_id == implying_tag.id))

    conflicting_implications_count = q.count()

    # If any of those are true, we have a chain.
    return conflicting_implications_count > 0


def add_implication(context, implying, implied):
    session = context.session()

    did_find_tags, tags_or_message = _identify_implication_tags(
        session,
        implying,
        implied)

    if not did_find_tags:
        return tags_or_message, False

    implying_tag, implied_tag = tags_or_message

    # Check if the same implication already exists
    current_implication_count = \
        session.query(TagImplication)\
        .filter(and_(TagImplication.c.implying_tag_id == implying_tag.id,
                     TagImplication.c.implied_tag_id == implied_tag.id))\
        .count()

    if current_implication_count > 0:
        return 'This implication is already configured', True

    would_create_implication_chain = _would_create_implication_chain(
        session,
        implying_tag,
        implied_tag
    )

    if would_create_implication_chain:
        return 'This would create a chain of implications', False

    implying_tag.implied_by_this.append(implied_tag)
    session.commit()
    return 'Success', True


def remove_implication(context, implying, implied):
    session = context.session()

    did_find_tags, tags_or_message = _identify_implication_tags(
        session,
        implying,
        implied)

    if not did_find_tags:
        return tags_or_message, False

    implying_tag, implied_tag = tags_or_message

    maybe_current_implications = \
        session.query(TagImplication)\
        .filter(and_(TagImplication.c.implying_tag_id == implying_tag.id,
                     TagImplication.c.implied_tag_id == implied_tag.id))\
        .all()

    if len(maybe_current_implications) < 1:
        return 'This implication was not configured', True

    implying_tag.implied_by_this.remove(implied_tag)
    session.commit()
    return 'Success', 200


def simplify_implied(context, tag):
    """ If 'tag' (T1) is implied by any other tags (T2),
        it no longer makes sense for a medium to be tagged
        as both T1 and T2. This functions will remove
        T1 from all media tagged "T1 Tx" iff Tx => T1."""

    session = context.session()

    implied_tag = session.query(Tag).filter_by(tag=tag).first()
    if not implied_tag:
        return False

    implying_tags = implied_tag.implying_this

    tag_ids = set([implied_tag.id])
    tag_ids |= set([t.id for t in implying_tags])

    media_ids_to_clean = \
        session.query(MediaTags.c.medium_id)\
        .filter(MediaTags.c.tag_id.in_(tag_ids))\
        .group_by(MediaTags.c.medium_id)\
        .having(func.count(MediaTags.c.tag_id) > 1)\
        .all()

    if not media_ids_to_clean:
        return False

    media_ids_to_clean = [m[0] for m in media_ids_to_clean]

    d = MediaTags\
        .delete()\
        .where(
            and_(
                MediaTags.c.tag_id == implied_tag.id,
                MediaTags.c.medium_id.in_(media_ids_to_clean))
        )

    session.execute(d)
    session.commit()


def get_all(context):
    session = context.session()

    all = session.query(Tag).filter(Tag.implied_by_this != None).all()

    return {row.tag: [t.tag for t in row.implied_by_this] for row in all}
