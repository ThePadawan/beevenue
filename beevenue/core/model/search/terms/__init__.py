import re

from ...tags import VALID_TAG_REGEX_INNER

from .simple import NegativeSearchTerm, PositiveSearchTerm, RatingSearchTerm
from .complex import CategorySearchTerm, CountingSearchTerm

COMPARISON = r'(?P<operator>(:|=|<|>|<=|>=|!=))(?P<number>[0-9]+)'

COUNTING_TERM_REGEX = re.compile(
    r'tags' + COMPARISON)
CATEGORY_TERM_REGEX = re.compile(
    r'(?P<category>[a-z]+)tags' + COMPARISON)
RATING_TERM_REGEX = re.compile(
    r'rating:(u|s|e|q)')
POSITIVE_TERM_REGEX = re.compile(VALID_TAG_REGEX_INNER)
NEGATIVE_TERM_REGEX = re.compile(f"-{VALID_TAG_REGEX_INNER}")


def get_search_terms(search_term_list):
    result = set()

    filters = [
            (COUNTING_TERM_REGEX, CountingSearchTerm),
            (CATEGORY_TERM_REGEX, CategorySearchTerm),
            (RATING_TERM_REGEX, RatingSearchTerm),
            (NEGATIVE_TERM_REGEX, NegativeSearchTerm),
            (POSITIVE_TERM_REGEX, PositiveSearchTerm),
        ]

    def _maybe_match(term):
        for (regex, klass) in filters:
            maybe_match = regex.match(term)
            if maybe_match:
                result.add(klass.from_match(maybe_match))
                return

    for term in search_term_list:
        _maybe_match(term)

    return result
