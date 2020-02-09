from .base import SearchTerm

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
        # Normalize operator such that "tags=5" and "tags:5"
        # have the same object hash and are treated identically.
        if operator == ":":
            self.operator = "="
        self.number = int(number)

    @classmethod
    def from_match(cls, match):
        return CountingSearchTerm(**match.groupdict())

    def applies_to(self, medium):
        op = OPS.get(self.operator, None)
        if not op:
            raise Exception(f"Unknown operator in {self}")

        # Note! Only count *innate* tags, not implications, aliases, etc...
        return op(len(medium.tag_names.innate), self.number)

    def __repr__(self):
        return f"tags{self.operator}{self.number}"


class CategorySearchTerm(SearchTerm):
    def __init__(self, category, operator, number):
        self.category = category
        self.operator = operator
        # Normalize operator such that "tags=5" and "tags:5"
        # have the same object hash and are treated identically.
        if operator == ":":
            self.operator = "="
        self.number = int(number)

    @classmethod
    def from_match(cls, match):
        return CategorySearchTerm(**match.groupdict())

    def applies_to(self, medium):
        matching_tag_names = [
            t for t in medium.tag_names.innate if t.startswith(f"{self.category}:")
        ]

        op = OPS.get(self.operator, None)
        if not op:
            raise Exception(f"Unknown operator in {self}")

        return op(len(matching_tag_names), self.number)

    def __repr__(self):
        return f"{self.category}tags{self.operator}{self.number}"
