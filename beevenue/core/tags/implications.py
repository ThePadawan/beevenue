from collections import deque
from typing import Dict, List, Optional, Tuple

from flask import g
from sqlalchemy import and_
from sqlalchemy.orm.query import Query

from ...models import Tag, TagImplication
from ...signals import implication_added, implication_removed
from .delete import delete_orphans


def _identify_implication_tags(
    implying: str, implied: str
) -> Optional[Tuple[Tag, Tag]]:
    session = g.db
    implying_tags = session.query(Tag).filter(Tag.tag == implying).all()
    implied_tags = session.query(Tag).filter(Tag.tag == implied).all()
    if len(implying_tags) != 1 or len(implied_tags) != 1:
        return None

    return implying_tags[0], implied_tags[0]


def _would_create_implication_cycle(
    implying_tag: Tag, implied_tag: Tag
) -> bool:
    # If we add the edge (implying, implied) to the implication graph,
    # would that form a cycle?
    # Equivalent:
    # * Gather "implied"s transitive neighbors
    # * If they include "implying", we found a cycle, return True
    # * If they stop growing, we can add the edge, return False
    session = g.db

    visited = set()
    visited.add(implying_tag.id)

    queue: deque = deque()
    queue.append(implied_tag.id)

    while queue:
        current = queue.pop()

        neighbors = (
            session.query(TagImplication)
            .filter(TagImplication.c.implying_tag_id == current)
            .all()
        )

        neighbor_ids = [n.implied_tag_id for n in neighbors]

        for neighbor_id in neighbor_ids:
            if neighbor_id in visited:
                return True
            queue.append(neighbor_id)

    return False


def _tag_implication_query(implying_tag: Tag, implied_tag: Tag) -> Query:
    return g.db.query(TagImplication).filter(
        and_(
            TagImplication.c.implying_tag_id == implying_tag.id,
            TagImplication.c.implied_tag_id == implied_tag.id,
        )
    )


def add_implication(implying: str, implied: str) -> Optional[str]:
    """Add an implication between two tags.

    Returns error on failure, else None."""

    tags = _identify_implication_tags(implying, implied)

    if not tags:
        return "Could not find both tags"

    implying_tag, implied_tag = tags

    # Check if the same implication already exists
    current_implication_count = _tag_implication_query(
        implying_tag, implied_tag
    ).count()

    if current_implication_count > 0:
        return None

    would_create_implication_cycle = _would_create_implication_cycle(
        implying_tag, implied_tag
    )

    if would_create_implication_cycle:
        return "This would create a cycle of implications"

    implying_tag.implied_by_this.append(implied_tag)
    g.db.commit()
    implication_added.send(
        (
            implying,
            implied,
        )
    )
    return None


def remove_implication(implying: str, implied: str) -> None:
    """Remove an implication between two tags."""

    tags = _identify_implication_tags(implying, implied)

    if not tags:
        return None

    implying_tag, implied_tag = tags

    maybe_current_implications = _tag_implication_query(
        implying_tag, implied_tag
    ).all()

    if len(maybe_current_implications) < 1:
        return None

    implying_tag.implied_by_this.remove(implied_tag)
    g.db.commit()
    delete_orphans()
    implication_removed.send(
        (
            implying,
            implied,
        )
    )
    return None


def get_all() -> Dict[str, List[str]]:
    rows = (
        g.db.query(Tag)
        .filter(
            Tag.implied_by_this != None  # pylint: disable=singleton-comparison
        )
        .all()
    )
    return {row.tag: [t.tag for t in row.implied_by_this] for row in rows}
