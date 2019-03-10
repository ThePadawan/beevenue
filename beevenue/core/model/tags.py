from ...models import Tag, TagAlias, TagImplication, MediaTags


def get(context, name):
    session = context.session()
    all_tags = session.query(Tag).filter_by(tag=name).all()
    if len(all_tags) != 1:
        return None

    return all_tags[0]


def get_statistics(context):
    session = context.session()
    all_tags = session.query(Tag).all()
    return all_tags


def delete_orphans(context):
    session = context.session()

    tags_to_delete = session.query(Tag).outerjoin(MediaTags)\
        .filter(MediaTags.c.tag_id is None)\
        .all()

    # TODO: Only delete tags if they're not implied
    # by anything.

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
        session.query(TagAlias).filter(TagAlias.alias == new_alias).count()
    if conflicting_tags_count > 0:
        return "This alias is already taken", False

    old_tag = old_tags[0]
    alias = TagAlias(old_tag.id, new_alias)
    session.add(alias)
    session.commit()
    return "", True


def remove_alias(context, name, alias):
    session = context.session()

    old_tags = session.query(Tag).filter(Tag.tag == name).all()
    if len(old_tags) != 1:
        return "Could not find tag with that name", False

    current_aliases = \
        session.query(TagAlias).filter(TagAlias.alias == alias).all()
    if len(current_aliases) == 0:
        return "This alias does not exist", True

    session.delete(current_aliases[0])
    session.commit()
    return "Successfully removed alias", True


def _identify_implication_tags(session, implying, implied):
    implying_tags = session.query(Tag).filter(Tag.tag == implying).all()
    implied_tags = session.query(Tag).filter(Tag.tag == implied).all()
    if len(implying_tags) != 1 or len(implied_tags) != 1:
        return False, "Could not find both tags"

    return True, (implying_tags[0], implied_tags[0])


def _would_create_implication_chain(session, implying_tag, implied_tag):
    # * Does "implied" imply something?
    # * Does something imply "implying"?
    conflicting_implications_count = \
        session.query(TagImplication)\
        .filter(TagImplication.c.implying_tag_id == implied_tag.id
                or TagImplication.c.implied_tag_id == implying_tag.id)\
        .count()

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
        .filter(TagImplication.c.implying_tag_id == implying_tag.id
                and TagImplication.c.implied_tag_id == implied_tag.id)\
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
        .filter(TagImplication.c.implying_tag_id == implying_tag.id
                and TagImplication.c.implied_tag_id == implied_tag.id)\
        .all()

    if len(maybe_current_implications) < 1:
        return 'This implication was not configured', True

    implying_tag.implied_by_this.remove(implied_tag)
    session.commit()
    return 'Success', 200
