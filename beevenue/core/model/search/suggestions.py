from enum import Enum
from typing import NamedTuple
import re

from fuzzywuzzy import process

from ..tags.censorship import Censorship
from .... import db
from ....spindex.spindex import SPINDEX


RATING_REGEXP = re.compile("rating:?")


# TODO: This is really inefficient, but the performance might just be
#       "good enough". Otherwise add additional spindex fields
#       for tags and categories and keep them in sync.
def _load():
    media = SPINDEX.all()
    categories = set()
    tags = set()
    for m in media:
        tags |= m.tag_names.searchable
        for t in m.tag_names.searchable:
            if ":" in t:
                categories.add(t.split(":")[0])

    return categories, tags


def _censor(data):
    categories, tags = data

    # TODO: It is really wasteful to load this from the DB once per query.
    # Move towards expanding SPINDEX
    # (Note that this might requiring flushing SPINDEX if its schema/version changed)
    censorship = Censorship(db.session())

    censored_categories = set(
        [c for c in categories if not censorship.is_category_censored(c)]
    )
    censored_tags = set([t for t in tags if not censorship.is_tag_censored(t)])

    return censored_categories, censored_tags


class ChoiceKind(Enum):
    hint = 1
    term = 2


class Choice(NamedTuple):
    kind: ChoiceKind
    value: str


def _term(v):
    return Choice(ChoiceKind.term, v)


def _hint(v):
    return Choice(ChoiceKind.hint, v)


def get(query):
    """ "
    Get search suggestions for the given query.

    Returns "hints" (values that cannot be used as-is (like "ctags"),
    but users can refine their queries based on them)

    and

    "terms", which can be used as-is (i.e. "image").
    """
    choices = []

    categories, tags = _censor(_load())

    # Case 1: EXACT and NEGATIVE
    if len(query) > 1 and query[0] in ("+", "-"):
        query = query[1:]

    # Case 2: Counting
    choices.append(_hint("tags"))

    # Case 3: Category
    for category in categories:
        choices.append(_hint(f"{category}tags"))

    # Case 4: Rating
    if RATING_REGEXP.match(query):
        for rating in ("s", "q", "e", "u"):
            choices.append(_term(f"rating:{rating}"))
    else:
        choices.append(_hint("rating"))

    # Case 5: Positive
    for tag in tags:
        choices.append(_term(tag))

    # Because the processor is run on the query and each choice,
    # it needs to be able to handle both types
    # (so we can't use a simpler lambda)
    def processor(q):
        if type(q) == str:
            return q
        return q.value

    best_choices = process.extractBests(
        query, choices, processor, score_cutoff=80, limit=5
    )

    hints = []
    terms = []

    for choice in best_choices:
        chosen_value = choice[0]
        if chosen_value.kind == ChoiceKind.hint:
            hints.append(chosen_value.value)
        else:
            terms.append(chosen_value.value)

    return {
        "hints": hints,
        "terms": terms,
    }
