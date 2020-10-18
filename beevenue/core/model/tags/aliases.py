from typing import Optional

from .delete import delete_orphans
from .... import db
from ....models import Tag, TagAlias
from ....spindex.signals import alias_added, alias_removed


def add_alias(current_name: str, new_alias: str) -> Optional[str]:
    """Try to add ``new_alias`` as an alias to the tag ``current_name``.

    Returns error on failure, else None."""

    session = db.session()

    old_tags = session.query(Tag).filter(Tag.tag == current_name).all()
    if len(old_tags) != 1:
        return "Could not find tag with that name"

    new_alias = new_alias.strip()

    conflicting_aliases = (
        session.query(TagAlias).filter(TagAlias.alias == new_alias).all()
    )
    if len(conflicting_aliases) > 0:
        return "This alias is already taken"

    # Ensure that there is no tag with the new_alias as actual name
    conflicting_tags_count = (
        session.query(Tag).filter(Tag.tag == new_alias).count()
    )
    if conflicting_tags_count > 0:
        return "This alias is already taken"

    old_tag = old_tags[0]
    alias = TagAlias(old_tag.id, new_alias)
    session.add(alias)
    session.commit()
    alias_added.send(
        (
            old_tag.tag,
            new_alias,
        )
    )
    return None


def remove_alias(name: str, alias: str) -> None:
    """Remove alias ``alias`` from tag ``name``.

    Always succeeds, even if tag or alias do not exist."""
    session = db.session()

    old_tags = session.query(Tag).filter(Tag.tag == name).all()
    if len(old_tags) != 1:
        return None

    current_aliases = (
        session.query(TagAlias).filter(TagAlias.alias == alias).all()
    )
    if len(current_aliases) == 0:
        return None

    session.delete(current_aliases[0])
    session.commit()
    delete_orphans()
    alias_removed.send(alias)
    return None
