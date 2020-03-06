from collections import defaultdict
from .... import db
from ....models import Tag, TagImplication


class TagStatistics(object):
    def __init__(self, tags):
        self.tags = tags


def get_statistics(context):
    session = db.session()

    filter = None

    if context.user_role != "admin":
        if context.is_sfw:
            filter = Tag.rating == "s"
        else:
            filter = Tag.rating.in_(["s", "q"])

    q = session.query(Tag)
    if filter is not None:
        q = q.filter(*[filter])
    all_tags = q.all()

    all_direct_implications = session.query(TagImplication).all()

    implying_this_count = defaultdict(int)
    implied_by_this_count = defaultdict(int)

    for i in all_direct_implications:
        implying_this_count[i.implied_tag_id] += 1
        implied_by_this_count[i.implying_tag_id] += 1

    for t in all_tags:
        t.implied_by_this_count = implied_by_this_count[t.id]
        t.implying_this_count = implying_this_count[t.id]

        if context.user_role == "admin":
            t.media_count = len(t.media)
        else:
            if context.is_sfw:
                t.media_count = len([m for m in t.media if m.rating == "s"])
            else:
                t.media_count = len(
                    [m for m in t.media if m.rating in ["s", "q"]]
                )

    return TagStatistics(all_tags)
