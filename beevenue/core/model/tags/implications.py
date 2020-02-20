from collections import deque

from sqlalchemy import and_
from sqlalchemy.sql import func

from ....spindex.signals import implication_added, implication_removed
from ....models import Tag, TagImplication, MediaTags


def _identify_implication_tags(session, implying, implied):
    implying_tags = session.query(Tag).filter(Tag.tag == implying).all()
    implied_tags = session.query(Tag).filter(Tag.tag == implied).all()
    if len(implying_tags) != 1 or len(implied_tags) != 1:
        return False, "Could not find both tags"

    return True, (implying_tags[0], implied_tags[0])


def _would_create_implication_cycle(session, implying_tag, implied_tag):
    # If we add the edge (implying, implied) to the implication graph,
    # would that form a cycle?
    # Equivalent:
    # * Gather "implied"s transitive neighbors
    # * If they include "implying", we found a cycle, return True
    # * If they stop growing, we can add the edge, return False

    visited = set()
    visited.add(implying_tag.id)

    q = deque()
    q.append(implied_tag.id)

    while q:
        current = q.pop()

        neighbors = (
            session.query(TagImplication)
            .filter(TagImplication.c.implying_tag_id == current)
            .all()
        )

        neighbor_ids = [n.implied_tag_id for n in neighbors]

        for n in neighbor_ids:
            if n in visited:
                return True
            q.append(n)

    return False


def add_implication(context, implying, implied):
    session = context.session()

    did_find_tags, tags_or_message = _identify_implication_tags(
        session, implying, implied
    )

    if not did_find_tags:
        return tags_or_message, False

    implying_tag, implied_tag = tags_or_message

    # Check if the same implication already exists
    current_implication_count = (
        session.query(TagImplication)
        .filter(
            and_(
                TagImplication.c.implying_tag_id == implying_tag.id,
                TagImplication.c.implied_tag_id == implied_tag.id,
            )
        )
        .count()
    )

    if current_implication_count > 0:
        return "This implication is already configured", True

    would_create_implication_cycle = _would_create_implication_cycle(
        session, implying_tag, implied_tag
    )

    if would_create_implication_cycle:
        return "This would create a cycle of implications", False

    implying_tag.implied_by_this.append(implied_tag)
    session.commit()
    implication_added.send((implying, implied,))
    return "Success", True


def remove_implication(context, implying, implied):
    session = context.session()

    did_find_tags, tags_or_message = _identify_implication_tags(
        session, implying, implied
    )

    if not did_find_tags:
        return tags_or_message, False

    implying_tag, implied_tag = tags_or_message

    maybe_current_implications = (
        session.query(TagImplication)
        .filter(
            and_(
                TagImplication.c.implying_tag_id == implying_tag.id,
                TagImplication.c.implied_tag_id == implied_tag.id,
            )
        )
        .all()
    )

    if len(maybe_current_implications) < 1:
        return "This implication was not configured", True

    implying_tag.implied_by_this.remove(implied_tag)
    session.commit()
    implication_removed.send((implying, implied,))
    return "Success", 200


def get_all(context):
    session = context.session()
    all = session.query(Tag).filter(Tag.implied_by_this != None).all()
    return {row.tag: [t.tag for t in row.implied_by_this] for row in all}
