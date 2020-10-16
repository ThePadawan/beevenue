from collections import defaultdict
from typing import Callable, Dict, List

from sqlalchemy.orm.scoping import scoped_session

from beevenue.context import BeevenueContext

from .... import db
from ....models import Tag, TagImplication
from ....spindex.spindex import SPINDEX
from .tag_summary import TagSummary, TagSummaryEntry

SingleCountType = Dict[str, int]
CountsType = Dict[str, SingleCountType]


def _load_tags(context: BeevenueContext, session: scoped_session) -> List[Tag]:
    filter = None

    if context.user_role != "admin":
        if context.is_sfw:
            filter = Tag.rating == "s"
        else:
            filter = Tag.rating.in_(["s", "q"])

    q = session.query(Tag.id, Tag.tag, Tag.rating)
    if filter is not None:
        q = q.filter(*[filter])

    all_tags: List[Tag] = q.all()
    return all_tags


def _load_media_counts(session: scoped_session) -> CountsType:
    """
    Returns a data structure that answers the question
    "Given this tag, how many media of each rating exist?".

    i.e. d["foo"] = {"q": 2, "e": 1, "s": 0, "u": 0}
    """

    all_media = SPINDEX.all()
    counts: CountsType = defaultdict(lambda: defaultdict(int))

    for m in all_media:
        for name in m.tag_names.innate:
            counts[name][m.rating] += 1

    return counts


def _get_censor_func(
    context: BeevenueContext,
) -> Callable[[SingleCountType], int]:
    def no_censor(counts: SingleCountType) -> int:
        return sum(counts.values())

    def sfw_censor(counts: SingleCountType) -> int:
        return counts["s"]

    def q_censor(counts: SingleCountType) -> int:
        return counts["s"] + counts["q"]

    if context.user_role == "admin":
        return no_censor
    if context.is_sfw:
        return sfw_censor

    return q_censor


def get_summary(context: BeevenueContext) -> TagSummary:
    session = db.session()

    all_tags = _load_tags(context, session)

    media_counts = _load_media_counts(session)

    all_direct_implications = session.query(TagImplication).all()

    all_implied_ids = frozenset(
        [i.implied_tag_id for i in all_direct_implications]
    )

    censor_func = _get_censor_func(context)

    results = []

    for t in all_tags:
        r: TagSummaryEntry = {
            "tag": t.tag,
            "rating": t.rating,
            "implied_by_something": t.id in all_implied_ids,
            "media_count": censor_func(media_counts[t.tag]),
        }

        results.append(r)

    return TagSummary(results)
