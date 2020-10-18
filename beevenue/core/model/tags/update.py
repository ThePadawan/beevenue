from typing import Tuple, Union

from sqlalchemy.orm.scoping import scoped_session

from .... import db
from ....spindex.signals import tag_renamed
from ....models import Tag, MediaTags


def _rename(
    session: scoped_session, old_tag: Tag, new_name: str
) -> Tuple[str, bool]:
    if not new_name:
        return "You must specify a new name", False

    old_name = old_tag.tag

    new_tags = session.query(Tag).filter(Tag.tag == new_name).all()

    if len(new_tags) < 1:
        # New tag doesn't exist yet. We can simply rename "old_tag".
        old_tag.tag = new_name
        tag_renamed.send(
            (
                old_name,
                new_name,
            )
        )
        return "Successfully renamed tag", True

    new_tag = new_tags[0]

    # if new_tag does exist, UPDATE all medium tags
    # to reference new_tag instead of old_tag, then remove old_tag
    MediaTags.update().where(MediaTags.c.tag_id == old_tag.id).values(
        tag_id=new_tag.id
    )

    session.delete(old_tag)

    tag_renamed.send(
        (
            old_name,
            new_name,
        )
    )
    return "Successfully renamed tag", True


def update(tag_name: str, new_model: dict) -> Tuple[bool, Union[str, Tag]]:
    session = db.session()
    tag = session.query(Tag).filter(Tag.tag == tag_name).first()

    if not tag:
        return False, "Could not find tag with that name"

    if "tag" in new_model:
        msg, success = _rename(session, tag, new_model["tag"])
        if not success:
            return False, msg

    if "rating" in new_model:
        rating = new_model["rating"]
        if rating not in ("s", "q", "e"):
            return False, "Please specify a valid rating"

        tag.rating = rating

    session.commit()
    return True, tag
