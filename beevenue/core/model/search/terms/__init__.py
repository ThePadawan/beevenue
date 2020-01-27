import re
from collections import namedtuple

from .simple import NegativeSearchTerm, PositiveSearchTerm, RatingSearchTerm
from .complex import CategorySearchTerm, CountingSearchTerm

SearchTerms = namedtuple(
    'SearchTerms',
    ['positive', 'negative', 'category', 'rating', 'counting'])

COMPARISON = r'(?P<operator>(:|=|<|>|<=|>=|!=))(?P<number>[0-9]+)'

COUNTING_TERM_REGEX = re.compile(
    r'tags' + COMPARISON)
CATEGORY_TERM_REGEX = re.compile(
    r'(?P<category>[a-z]+)tags' + COMPARISON)
RATING_TERM_REGEX = re.compile(
    r'rating:(u|s|e|q)')
POSITIVE_TERM_REGEX = re.compile('\"?([a-zA-Z0-9:.]+)\"?')
NEGATIVE_TERM_REGEX = re.compile('-\"?([a-zA-Z0-9:.]+)\"?')


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
