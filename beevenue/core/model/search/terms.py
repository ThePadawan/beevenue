import re
from collections import namedtuple

from sqlalchemy.sql import func

from ....models import MediaTags

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


OPS = {
    ':': lambda x, y: x == y,
    '=': lambda x, y: x == y,
    '<': lambda x, y: x < y,
    '>': lambda x, y: x > y,
    '<=': lambda x, y: x <= y,
    '>=': lambda x, y: x >= y,
    '!=': lambda x, y: x != y,
}


class CountingSearchTerm(object):
    def __init__(self, operator, number):
        self.operator = operator
        self.number = int(number)

    @staticmethod
    def from_match(match):
        return CountingSearchTerm(**match.groupdict())

    def contains_zero(self):
        if self.operator in (':', '=', '>='):
            result = self.number == 0
        elif self.operator in ('<'):
            result = self.number > 0
        elif self.operator in ('<='):
            result = self.number >= 0
        elif self.operator in ('>'):
            result = False
        elif self.operator in ('!='):
            result = self.number != 0
        else:
            raise Exception(f"Unknown operator in {self.operator}")

        return result

    def having_expr(self):
        op = OPS.get(self.operator, None)
        if not op:
            raise Exception(f"Unknown operator in {self}")

        return op(func.count(MediaTags.c.tag_id), self.number)

    def with_(self, operator=None, number=None):
        operator = operator or self.operator
        number = number or self.number
        return CountingSearchTerm(operator, number)

    def __repr__(self):
        return f"tags{self.operator}{self.number}"


class CategorySearchTerm(object):
    def __init__(self, category, operator, number):
        self.category = category
        self.operator = operator
        self.number = int(number)

    @staticmethod
    def from_match(match):
        return CategorySearchTerm(**match.groupdict())

    def having(self, value):
        op = OPS.get(self.operator, None)
        if not op:
            raise Exception(f"Unknown operator in {self}")

        return op(value, self.number)

    def with_(self, operator=None, number=None):
        operator = operator or self.operator
        number = number or self.number
        return CategorySearchTerm(self.category, operator, number)

    def __repr__(self):
        return f"{self.category}tags{self.operator}{self.number}"


class NegativeSearchTerm(object):
    def __init__(self, term, is_quoted):
        self.term = term
        self.is_quoted = is_quoted

    @staticmethod
    def from_match(match):
        return NegativeSearchTerm(
            match.group(1), "\"" in match.group(0))

    def __repr__(self):
        return f"-{self.term}"


class PositiveSearchTerm(object):
    def __init__(self, term, is_quoted):
        self.term = term
        self.is_quoted = is_quoted

    @staticmethod
    def from_match(match):
        return PositiveSearchTerm(
            match.group(1), "\"" in match.group(0))

    def __repr__(self):
        return f"{self.term}"


class RatingSearchTerm(object):
    def __init__(self, rating):
        self.rating = rating

    @staticmethod
    def from_match(match):
        return RatingSearchTerm(match.group(1))

    def __repr__(self):
        return f"rating:{self.rating}"


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
