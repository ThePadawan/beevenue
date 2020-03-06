from collections import defaultdict
from .... import db
from ....models import Tag, TagImplication


class TagStatistics(object):
    def __init__(self, tags):
        self.tags = tags


def _load_tags(context, session):
    filter = None

    if context.user_role != "admin":
        if context.is_sfw:
            filter = Tag.rating == "s"
        else:
            filter = Tag.rating.in_(["s", "q"])

    q = session.query(Tag)
    if filter is not None:
        q = q.filter(*[filter])

    return q.all()


def _censored_media_count(context, media):
    if context.user_role == "admin":
        return len(media)
    if context.is_sfw:
        return len([m for m in media if m.rating == "s"])

    return len([m for m in media if m.rating in ["s", "q"]])


def get_statistics(context):
    session = db.session()

    all_tags = _load_tags(context, session)

    all_direct_implications = session.query(TagImplication).all()

    implying_this_count = defaultdict(int)
    implied_by_this_count = defaultdict(int)

    for i in all_direct_implications:
        implying_this_count[i.implied_tag_id] += 1
        implied_by_this_count[i.implying_tag_id] += 1

    for t in all_tags:
        t.implied_by_this_count = implied_by_this_count[t.id]
        t.implying_this_count = implying_this_count[t.id]
        t.media_count = _censored_media_count(context, t.media)

    return TagStatistics(all_tags)
