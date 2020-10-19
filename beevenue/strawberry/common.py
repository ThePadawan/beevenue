from abc import ABC, abstractmethod, abstractproperty
import re
from typing import FrozenSet, List, Optional

from flask import g


class RulePart(ABC):
    """Abstract base class for all rule parts (both iffs and thens)."""

    @abstractmethod
    def applies_to(self, medium_id: int) -> bool:
        """Does this part of the rule apply to the medium with that id?"""

    @abstractmethod
    def get_medium_ids(
        self, filtering_medium_ids: Optional[List[int]] = None
    ) -> List[int]:
        """Load media this Iff applies to OR filter ids this Then applies to."""


class Iff(RulePart):
    """Abstract base class for all Iff rule parts."""

    @abstractmethod
    def pprint_if(self) -> str:
        """Formats this part as an 'if' clause."""


class Then(RulePart):
    """Abstract base class for all Then rule parts."""

    @abstractmethod
    def pprint_then(self) -> str:
        """Formats this part as an 'if' clause."""


class IffAndThen(Iff, Then):
    """Flexible rule part that can be used as both an Iff and a Then.

    (Only really used for type hints, since the typing module does not have
    Sum[Iff, Then], only Union[Iff, Then]."""


class HasAnyTags(RulePart):
    """Abstract base class for rule parts that checks for presence of tags."""

    def __init__(self) -> None:
        self.tag_names: Optional[FrozenSet[str]] = None

    def _load_tag_names(self) -> None:
        """Preload the tag names (e.g. based on regexes) into self.tag_names."""

    @abstractproperty
    def _tags_as_str(self) -> str:
        """Pretty-printed version of self.tag_names for user display."""

    def _ensure_tag_names_loaded(self) -> None:
        if self.tag_names is not None:
            return

        self._load_tag_names()

    def applies_to(self, medium_id: int) -> bool:
        self._ensure_tag_names_loaded()
        if not self.tag_names:
            return False

        medium = g.spindex.get_medium(medium_id)
        if not medium:
            return False

        return len(self.tag_names & medium.tag_names.searchable) > 0

    def get_medium_ids(
        self, filtering_medium_ids: Optional[List[int]] = None
    ) -> List[int]:
        self._ensure_tag_names_loaded()
        if not self.tag_names:
            return []

        all_media = g.spindex.all()

        if filtering_medium_ids:
            all_media = [
                m for m in all_media if m.medium_id in filtering_medium_ids
            ]

        all_media = [
            m
            for m in all_media
            if len(self.tag_names & m.tag_names.searchable) > 0
        ]

        return [m.medium_id for m in all_media]


class HasAnyTagsLike(HasAnyTags, IffAndThen):
    """Rule part that checks if a medium has any tags matching some regexes."""

    def __init__(self, *regexes: str) -> None:
        HasAnyTags.__init__(self)
        if not regexes:
            raise Exception("You must configure at least one LIKE expression")

        self.regexes = regexes

    def _load_tag_names(self) -> None:
        tag_names = set()

        all_tag_names = set()
        for medium in g.spindex.all():
            all_tag_names |= medium.tag_names.searchable

        for regex in self.regexes:
            compiled_regex = re.compile(f"^{regex}$")
            for tag_name in all_tag_names:
                if compiled_regex.match(tag_name):
                    tag_names.add(tag_name)

        self.tag_names = frozenset(tag_names)

    @property
    def _tags_as_str(self) -> str:
        return ", ".join(self.regexes)

    def pprint_if(self) -> str:
        return f"Any medium with a tag like '{self._tags_as_str}'"

    def pprint_then(self) -> str:
        return f"should have a tag like '{self._tags_as_str}'."


class HasAnyTagsIn(HasAnyTags, IffAndThen):
    """Rule part that checks if a medium has any tags in a specified set."""

    def __init__(self, *tag_names: str) -> None:
        HasAnyTags.__init__(self)
        if not tag_names:
            raise Exception("You must configure at least one name")
        self.tag_names: FrozenSet[str] = frozenset(tag_names)

    @property
    def _tags_as_str(self) -> str:
        return ", ".join(self.tag_names)

    def pprint_if(self) -> str:
        return f"Any medium with a tag in '{self._tags_as_str}'"

    def pprint_then(self) -> str:
        return f"should have a tag in '{self._tags_as_str}'."


class HasRating(IffAndThen):
    """Flexible rule part that checks for the presence of a (specific) rating.

    I.e. HasRating() checks that a medium has any rating other than "unrated",
    but HasRating("s") checks that a medium has the rating "s".
    """

    def __init__(self, rating: Optional[str] = None):
        self.rating: Optional[str] = rating

    def get_medium_ids(
        self, filtering_medium_ids: Optional[List[int]] = None
    ) -> List[int]:
        all_media = g.spindex.all()

        if filtering_medium_ids:
            all_media = [
                m for m in all_media if m.medium_id in filtering_medium_ids
            ]

        if self.rating:
            all_media = [m for m in all_media if m.rating == self.rating]
        else:
            all_media = [m for m in all_media if m.rating != "u"]

        return [m.medium_id for m in all_media]

    def applies_to(self, medium_id: int) -> bool:
        medium = g.spindex.get_medium(medium_id)
        if not medium:
            return False

        if self.rating:
            has_correct_rating: bool = medium.rating == self.rating
            return has_correct_rating

        has_any_rating: bool = medium.rating != "u"
        return has_any_rating

    @property
    def _rating_str(self) -> str:
        if self.rating:
            return f"a rating of '{self.rating}'"
        return "a known rating"

    def pprint_then(self) -> str:
        return f"should have {self._rating_str}."

    def pprint_if(self) -> str:
        return f"Any medium with {self._rating_str}"
