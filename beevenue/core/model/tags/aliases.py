from ....models import Tag, TagAlias
from ....spindex.signals import alias_added, alias_removed


def add_alias(context, current_name, new_alias):
    session = context.session()

    old_tags = session.query(Tag).filter(Tag.tag == current_name).all()
    if len(old_tags) != 1:
        return "Could not find tag with that name", False

    new_alias = new_alias.strip()

    conflicting_aliases = \
        session.query(TagAlias).filter(TagAlias.alias == new_alias).all()
    if len(conflicting_aliases) > 0:
        return "This alias is already taken", False

    # Ensure that there is no tag with the new_alias as actual name
    conflicting_tags_count = \
        session.query(Tag).filter(Tag.tag == new_alias).count()
    if conflicting_tags_count > 0:
        return "This alias is already taken", False

    old_tag = old_tags[0]
    alias = TagAlias(old_tag.id, new_alias)
    session.add(alias)
    session.commit()
    alias_added.send((old_tag.tag, new_alias,))
    return "", True


def remove_alias(context, name, alias):
    session = context.session()

    old_tags = session.query(Tag).filter(Tag.tag == name).all()
    if len(old_tags) != 1:
        return "Could not find tag with that name", True

    current_aliases = \
        session.query(TagAlias).filter(TagAlias.alias == alias).all()
    if len(current_aliases) == 0:
        return "This alias does not exist", True

    session.delete(current_aliases[0])
    session.commit()
    alias_removed.send((old_tags[0].tag, alias,))
    return "Successfully removed alias", True
