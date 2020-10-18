from .... import db
from ....models import MediaTags, Tag


def delete_orphans() -> None:
    session = db.session()

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
