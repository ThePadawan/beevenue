from sqlalchemy.sql import func

from .base import SearchTerm
from .....models import MediaTags

OPS = {
    ':': lambda x, y: x == y,
    '=': lambda x, y: x == y,
    '<': lambda x, y: x < y,
    '>': lambda x, y: x > y,
    '<=': lambda x, y: x <= y,
    '>=': lambda x, y: x >= y,
    '!=': lambda x, y: x != y,
}


class CountingSearchTerm(SearchTerm):
    def __init__(self, operator, number):
        self.operator = operator
        self.number = int(number)

    @classmethod
    def from_match(cls, match):
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


class CategorySearchTerm(SearchTerm):
    def __init__(self, category, operator, number):
        self.category = category
        self.operator = operator
        self.number = int(number)

    @classmethod
    def from_match(cls, match):
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
