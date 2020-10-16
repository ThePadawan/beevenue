from abc import ABCMeta, abstractmethod
from re import Match

from .....spindex.models import SpindexedMedium


class SearchTerm(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def from_match(cls, match: Match) -> "SearchTerm":
        """Construct this SearchTerm from the match of its regex."""

    @abstractmethod
    def applies_to(self, medium: SpindexedMedium) -> bool:
        """Does this SearchTerm apply to this medium?"""

    def __eq__(self, other: object) -> bool:
        return self.__hash__() == other.__hash__()

    def __hash__(self) -> int:
        return hash(self.__repr__())
