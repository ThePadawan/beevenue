from ...models import Tag, MediaTags


def get_statistics(context):
    session = context.session()
    all_tags = session.query(Tag).all()
    return all_tags


def delete_orphans(context):
    session = context.session()

    tags_to_delete = session.query(Tag).outerjoin(MediaTags)\
        .filter(MediaTags.c.tag_id == None)\
        .all()

    for t in tags_to_delete:
        session.delete(t)
    
    if tags_to_delete:
        session.commit()
