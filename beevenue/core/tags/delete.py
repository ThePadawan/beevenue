from flask import g

from ...models import MediaTags, Tag


def delete_orphans() -> None:
    session = g.db

    tags_to_delete = (
        session.query(Tag)
        .outerjoin(MediaTags)
        .filter(MediaTags.c.tag_id.is_(None))
        .all()
    )

    def is_deletable(tag: Tag) -> bool:
        return len(tag.implying_this) == 0 and len(tag.aliases) == 0

    tags_to_delete = [t for t in tags_to_delete if is_deletable(t)]

    for tag in tags_to_delete:
        session.delete(tag)

    if tags_to_delete:
        session.commit()
