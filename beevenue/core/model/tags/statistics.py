from collections import defaultdict
from .... import db
from ....models import Tag, TagImplication
from ....spindex.spindex import SPINDEX


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

    q = session.query(Tag.id, Tag.tag, Tag.rating)
    if filter is not None:
        q = q.filter(*[filter])

    return q.all()


def _load_media_counts(session):
    """
        Returns a data structure that answers the question
        "Given this tag, how many media of each rating exist?".

        i.e. d["foo"] = {"q": 2, "e": 1, "s": 0, "u": 0}
    """

    all_media = SPINDEX.all()
    counts = defaultdict(lambda: defaultdict(int))

    for m in all_media:
        for name in m.tag_names.innate:
            counts[name][m.rating] += 1

    return counts


def _get_censor_func(context):
    def no_censor(counts):
        return sum(counts.values())

    def sfw_censor(counts):
        return counts["s"]

    def q_censor(counts):
        return counts["s"] + counts["q"]

    if context.user_role == "admin":
        return no_censor
    if context.is_sfw:
        return sfw_censor

    return q_censor


def get_statistics(context):
    session = db.session()

    all_tags = _load_tags(context, session)

    media_counts = _load_media_counts(session)

    all_direct_implications = session.query(TagImplication).all()

    implying_this_count = defaultdict(int)
    implied_by_this_count = defaultdict(int)

    for i in all_direct_implications:
        implying_this_count[i.implied_tag_id] += 1
        implied_by_this_count[i.implying_tag_id] += 1

    censor_func = _get_censor_func(context)

    results = []

    for t in all_tags:
        r = {
            "id": t.id,
            "tag": t.tag,
            "rating": t.rating,
            "implied_by_this_count": implied_by_this_count[t.id],
            "implying_this_count": implying_this_count[t.id],
            "media_count": censor_func(media_counts[t.tag]),
        }

        results.append(r)

    return TagStatistics(results)
