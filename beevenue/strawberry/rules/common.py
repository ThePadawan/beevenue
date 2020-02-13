from abc import abstractproperty, ABCMeta
import re

from ...spindex.spindex import SPINDEX


class HasAnyTags(metaclass=ABCMeta):
    def __init__(self):
        self.tag_names = None

    def _load_tag_names(self):
        pass

    @abstractproperty
    def _tags_as_str(self):
        pass

    def _ensure_tag_names_loaded(self):
        if self.tag_names is not None:
            return

        self._load_tag_names()

    def applies_to(self, medium_id):
        self._ensure_tag_names_loaded()
        if not self.tag_names:
            return False

        m = SPINDEX.get_medium(medium_id)
        return len(self.tag_names & m.tag_names.searchable) > 0

    def get_medium_ids(self, filtering_medium_ids=[]):
        self._ensure_tag_names_loaded()
        if not self.tag_names:
            return []

        all_media = SPINDEX.all()

        if filtering_medium_ids:
            all_media = [m for m in all_media if m.id in filtering_medium_ids]

        all_media = [
            m
            for m in all_media
            if len(self.tag_names & m.tag_names.searchable) > 0
        ]

        return [i.id for i in all_media]


class HasAnyTagsLike(HasAnyTags):
    def __init__(self, *regexes):
        HasAnyTags.__init__(self)
        if not regexes:
            raise Exception("You must configure at least one LIKE expression")

        self.regexes = regexes

    def _load_tag_names(self):
        tag_names = set()

        all_tag_names = set()
        for m in SPINDEX.all():
            all_tag_names |= m.tag_names.searchable

        for regex in self.regexes:
            compiled_regex = re.compile(f"^{regex}$")
            for tag_name in all_tag_names:
                if compiled_regex.match(tag_name):
                    tag_names.add(tag_name)

        self.tag_names = frozenset(tag_names)

    @property
    def _tags_as_str(self):
        return ", ".join(self.regexes)

    def pprint_if(self):
        return f"Any medium with a tag like '{self._tags_as_str}'"

    def pprint_then(self):
        return f"should have a tag like '{self._tags_as_str}'."


class HasAnyTagsIn(HasAnyTags):
    def __init__(self, *tag_names):
        HasAnyTags.__init__(self)
        if not tag_names:
            raise Exception("You must configure at least one name")
        self.tag_names = set(tag_names)

    @property
    def _tags_as_str(self):
        return ", ".join(self.tag_names)

    def pprint_if(self):
        return f"Any medium with a tag in '{self._tags_as_str}'"

    def pprint_then(self):
        return f"should have a tag in '{self._tags_as_str}'."


class HasRating(object):
    def __init__(self, rating=None):
        self.rating = rating

    def get_medium_ids(self, filtering_medium_ids=[]):
        all_media = SPINDEX.all()

        if filtering_medium_ids:
            all_media = [m for m in all_media if m.id in filtering_medium_ids]

        if self.rating:
            all_media = [m for m in all_media if m.rating == self.rating]
        else:
            all_media = [m for m in all_media if m.rating != "u"]

        return [m.id for m in all_media]

    def applies_to(self, medium_id):
        m = SPINDEX.get_medium(medium_id)
        if self.rating:
            return m.rating == self.rating
        return m.rating != "u"

    @property
    def _rating_str(self):
        if self.rating:
            return f"a rating of '{self.rating}'"
        else:
            return f"a known rating"

    def pprint_then(self):
        return f"should have {self._rating_str}."

    def pprint_if(self):
        return f"Any medium with {self._rating_str}"
