import re

from ...tags import VALID_TAG_REGEX_INNER

from .simple import (
    PositiveSearchTerm,
    RatingSearchTerm,
    ExactSearchTerm,
    Negative,
)
from .complex import CategorySearchTerm, CountingSearchTerm

COMPARISON = r"(?P<operator>(:|=|<|>|<=|>=|!=))(?P<number>[0-9]+)"

COUNTING_TERM_REGEX = re.compile(r"tags" + COMPARISON)
CATEGORY_TERM_REGEX = re.compile(r"(?P<category>[a-z]+)tags" + COMPARISON)
RATING_TERM_REGEX = re.compile(r"rating:(u|s|e|q)")
EXACT_TERM_REGEX = re.compile(r"\+(" + VALID_TAG_REGEX_INNER + ")")
POSITIVE_TERM_REGEX = re.compile(VALID_TAG_REGEX_INNER)


FILTERS = [
    (COUNTING_TERM_REGEX, CountingSearchTerm),
    (CATEGORY_TERM_REGEX, CategorySearchTerm),
    (RATING_TERM_REGEX, RatingSearchTerm),
    (EXACT_TERM_REGEX, ExactSearchTerm),
    (POSITIVE_TERM_REGEX, PositiveSearchTerm),
]


def _maybe_match(term):
    if len(term) < 1:
        return set()

    do_negate = False
    if term[0] == "-":
        do_negate = True
        term = term[1:]

    match = None
    matching_class = None
    for (regex, klass) in FILTERS:
        match = regex.match(term)
        matching_class = klass
        if match:
            break

    if not match:
        return set()

    term_obj = matching_class.from_match(match)
    if do_negate:
        term_obj = Negative(term_obj)
    return set([term_obj])


def get_search_terms(search_term_list):
    result = set()

    for term in search_term_list:
        result |= _maybe_match(term)

    return result
