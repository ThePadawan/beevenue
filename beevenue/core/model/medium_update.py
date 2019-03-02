from sqlalchemy.sql import column

from ...models import Medium, Tag, MediaTags


def update_rating(session, medium, new_rating):
    # Update rating
    if (medium.rating != new_rating and new_rating != 'u'):
        medium.rating = new_rating
        return True
    return False


def update_tags(session, medium, new_tags):
    # Nothing to do
    if new_tags is None:
        return False

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

    inserted_tags = []

    for unknown_tag_name in unknown_tag_names:
        t = Tag(unknown_tag_name)
        session.add(t)
        inserted_tags.append(t)

    # We need this to get the ids to insert into MediaTags later!
    if inserted_tags:
        session.commit()

    # take set of tag ids
    target_tag_ids = set(existing_tag_id_by_name.values()) | set([t.id for t in inserted_tags])

    # ensure that medium_tags contains exactly that set
    d = MediaTags\
        .delete()\
        .where(column('medium_id') == medium.id)
    session.execute(d)
    session.commit()

    values = []
    for tag_id in target_tag_ids:
        values.append({"medium_id": medium.id, "tag_id": tag_id})

    print(f"Now inserting {values}")
    if values:
        insert = MediaTags.insert().values(values)
        session.execute(insert)
        session.commit()


def update_medium(context, medium_id, new_rating, new_tags):
    session = context.session()

    maybe_medium = Medium.query.get(medium_id)
    if not maybe_medium:
        return False

    update_rating(session, maybe_medium, new_rating)
    update_tags(session, maybe_medium, new_tags)
    return True
