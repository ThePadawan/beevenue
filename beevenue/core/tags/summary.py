from collections import defaultdict
from typing import Callable, Dict, List

from flask import g

from beevenue.flask import BeevenueContext

from ...models import Tag, TagImplication
from .tag_summary import TagSummary, TagSummaryEntry

SingleCountType = Dict[str, int]
CountsType = Dict[str, SingleCountType]


def _load_tags(context: BeevenueContext) -> List[Tag]:
    tag_filter = None

    if context.user_role != "admin":
        if context.is_sfw:
            tag_filter = Tag.rating == "s"
        else:
            tag_filter = Tag.rating.in_(["s", "q"])

    query = g.db.query(Tag.id, Tag.tag, Tag.rating)
    if tag_filter is not None:
        query = query.filter(tag_filter)

    all_tags: List[Tag] = query.all()
    return all_tags


def _load_media_counts() -> CountsType:
    """
    Returns a data structure that answers the question
    "Given this tag, how many media of each rating exist?".

    i.e. d["foo"] = {"q": 2, "e": 1, "s": 0, "u": 0}
    """

    all_media = g.spindex.all()
    counts: CountsType = defaultdict(lambda: defaultdict(int))

    for medium in all_media:
        for name in medium.tag_names.innate:
            counts[name][medium.rating] += 1

    return counts


def _get_censor_func(
    context: BeevenueContext,
) -> Callable[[SingleCountType], int]:
    def _no_censor(counts: SingleCountType) -> int:
        return sum(counts.values())

    def _sfw_censor(counts: SingleCountType) -> int:
        return counts["s"]

    def _q_censor(counts: SingleCountType) -> int:
        return counts["s"] + counts["q"]

    if context.user_role == "admin":
        return _no_censor
    if context.is_sfw:
        return _sfw_censor

    return _q_censor


def get_summary(context: BeevenueContext) -> TagSummary:
    """Get short summary of all current tags."""

    censor_func = _get_censor_func(context)

    all_tags = _load_tags(context)
    media_counts = _load_media_counts()

    all_direct_implications = g.db.query(TagImplication).all()

    all_implied_ids = frozenset(
        [i.implied_tag_id for i in all_direct_implications]
    )

    entries = []

    for tag in all_tags:
        entry: TagSummaryEntry = {
            "tag": tag.tag,
            "rating": tag.rating,
            "implied_by_something": tag.id in all_implied_ids,
            "media_count": censor_func(media_counts[tag.tag]),
        }

        entries.append(entry)

    return TagSummary(entries)
