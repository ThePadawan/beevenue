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


def get_search_terms(search_term_list):
    result = set()

    filters = [
        (COUNTING_TERM_REGEX, CountingSearchTerm),
        (CATEGORY_TERM_REGEX, CategorySearchTerm),
        (RATING_TERM_REGEX, RatingSearchTerm),
        (EXACT_TERM_REGEX, ExactSearchTerm),
        (POSITIVE_TERM_REGEX, PositiveSearchTerm),
    ]

    def _maybe_match(term):
        if len(term) < 1:
            return

        do_negate = False
        if term[0] == "-":
            do_negate = True
            term = term[1:]

        for (regex, klass) in filters:
            maybe_match = regex.match(term)
            if maybe_match:
                term_obj = klass.from_match(maybe_match)
                if do_negate:
                    term_obj = Negative(term_obj)
                result.add(term_obj)
                return

    for term in search_term_list:
        _maybe_match(term)

    return result
