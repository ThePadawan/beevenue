from abc import ABCMeta, abstractmethod
from re import Match

from ...types import MediumDocument


class SearchTerm(metaclass=ABCMeta):
    """Abstract base class for all search terms."""

    @classmethod
    @abstractmethod
    def from_match(cls, match: Match) -> "SearchTerm":
        """Construct this SearchTerm from the match of its regex."""

    @abstractmethod
    def applies_to(self, medium: MediumDocument) -> bool:
        """Does this SearchTerm apply to this medium?"""

    def __eq__(self, other: object) -> bool:
        """Support hash-based equality."""
        return self.__hash__() == other.__hash__()

    def __hash__(self) -> int:
        """Support hash-based equality based on __repr__.

        This allows us to easily parse multiple equal search term strings
        (["foo", "foo", "bar") into a set of Search Terms (set("foo", "bar")).
        """
        return hash(self.__repr__())
