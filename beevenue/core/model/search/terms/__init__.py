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
    positive = []
    negative = []
    category = []
    rating = []
    counting = []

    filters = [
            (COUNTING_TERM_REGEX, CountingSearchTerm, counting),
            (CATEGORY_TERM_REGEX, CategorySearchTerm, category),
            (RATING_TERM_REGEX, RatingSearchTerm, rating),
            (NEGATIVE_TERM_REGEX, NegativeSearchTerm, negative),
            (POSITIVE_TERM_REGEX, PositiveSearchTerm, positive),
        ]

    def _maybe_match(term):
        for (regex, klass, result) in filters:
            maybe_match = regex.match(term)
            if maybe_match:
                result.append(klass.from_match(maybe_match))
                return

    for term in search_term_list:
        _maybe_match(term)

    return SearchTerms(
        positive=set(positive),
        negative=set(negative),
        category=set(category),
        rating=rating[:1],
        counting=set(counting))
