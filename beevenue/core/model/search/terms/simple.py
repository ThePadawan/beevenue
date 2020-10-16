from re import Match
from typing import NoReturn

from .....spindex.models import SpindexedMedium
from .base import SearchTerm


class BasicSearchTerm(SearchTerm):
    def __init__(self, term: str):
        self.term = term


class PositiveSearchTerm(BasicSearchTerm):
    def __repr__(self) -> str:
        return f"{self.term}"

    def applies_to(self, medium: SpindexedMedium) -> bool:
        return self.term in medium.tag_names.searchable

    @classmethod
    def from_match(cls, match: Match) -> "PositiveSearchTerm":
        return PositiveSearchTerm(match.group(0))


class ExactSearchTerm(BasicSearchTerm):
    def __repr__(self) -> str:
        return f"+{self.term}"

    def applies_to(self, medium: SpindexedMedium) -> bool:
        return self.term in medium.tag_names.innate

    @classmethod
    def from_match(cls, match: Match) -> "ExactSearchTerm":
        return ExactSearchTerm(match.group(1))


class RatingSearchTerm(SearchTerm):
    def __init__(self, rating: str):
        self.rating = rating

    @classmethod
    def from_match(cls, match: Match) -> "RatingSearchTerm":
        return RatingSearchTerm(match.group(1))

    def __repr__(self) -> str:
        return f"rating:{self.rating}"

    def applies_to(self, medium: SpindexedMedium) -> bool:
        return medium.rating == self.rating


class Negative(SearchTerm):
    def __init__(self, inner_term: SearchTerm):
        self.inner_term = inner_term

    @classmethod
    def from_match(cls, match: Match) -> NoReturn:
        raise NotImplementedError("Unsupported for this SearchTerm")

    def __repr__(self) -> str:
        return f"!{self.inner_term.__repr__()}"

    def applies_to(self, medium: SpindexedMedium) -> bool:
        return not self.inner_term.applies_to(medium)
