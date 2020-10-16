from re import Match
from typing import Callable, Dict

from .....spindex.models import SpindexedMedium
from .base import SearchTerm

OPS: Dict[str, Callable[[int, int], bool]] = {
    ":": lambda x, y: x == y,
    "=": lambda x, y: x == y,
    "<": lambda x, y: x < y,
    ">": lambda x, y: x > y,
    "<=": lambda x, y: x <= y,
    ">=": lambda x, y: x >= y,
    "!=": lambda x, y: x != y,
}


class CountingSearchTerm(SearchTerm):
    def __init__(self, operator: str, number: str):
        self.operator = operator
        # Normalize operator such that "tags=5" and "tags:5"
        # have the same object hash and are treated identically.
        if operator == ":":
            self.operator = "="
        self.number = int(number)

    @classmethod
    def from_match(cls, match: Match) -> "CountingSearchTerm":
        return CountingSearchTerm(**match.groupdict())

    def applies_to(self, medium: SpindexedMedium) -> bool:
        op = OPS.get(self.operator, None)
        if not op:
            raise Exception(f"Unknown operator in {self}")

        # Note! Only count *innate* tags, not implications, aliases, etc...
        return op(len(medium.tag_names.innate), self.number)

    def __repr__(self) -> str:
        return f"tags{self.operator}{self.number}"


class CategorySearchTerm(SearchTerm):
    def __init__(self, category: str, operator: str, number: str):
        self.category = category
        self.operator = operator
        # Normalize operator such that "tags=5" and "tags:5"
        # have the same object hash and are treated identically.
        if operator == ":":
            self.operator = "="
        self.number = int(number)

    @classmethod
    def from_match(cls, match: Match) -> "CategorySearchTerm":
        return CategorySearchTerm(**match.groupdict())

    def applies_to(self, medium: SpindexedMedium) -> bool:
        matching_tag_names = [
            t
            for t in medium.tag_names.innate
            if t.startswith(f"{self.category}:")
        ]

        op = OPS.get(self.operator, None)
        if not op:
            raise Exception(f"Unknown operator in {self}")

        return op(len(matching_tag_names), self.number)

    def __repr__(self) -> str:
        return f"{self.category}tags{self.operator}{self.number}"
