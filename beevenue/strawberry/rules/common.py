from abc import abstractmethod, abstractproperty, ABCMeta

from sqlalchemy.sql.expression import column

from ...models import Medium, Tag, MediaTags


class HasAnyTags(metaclass=ABCMeta):
    def __init__(self):
        self.tag_ids = None

    @abstractmethod
    def _load_tag_ids(self):
        pass

    @abstractproperty
    def _tags_as_str(self):
        pass

    def _ensure_tag_ids_loaded(self):
        if self.tag_ids is not None:
            return

        self._load_tag_ids()

    def get_medium_ids(self, session, filtering_medium_ids=[]):
        self._ensure_tag_ids_loaded()
        if not self.tag_ids:
            return []

        filters = [column("tag_id").in_(self.tag_ids)]
        if filtering_medium_ids:
            filters.append(column("medium_id").in_(filtering_medium_ids))

        medium_tags = session.query(MediaTags).filter(*filters).all()

        return [i.medium_id for i in medium_tags]


class HasAnyTagsLike(HasAnyTags):
    def __init__(self, *like_exprs):
        HasAnyTags.__init__(self)
        if not like_exprs:
            raise Exception("You must configure at least one LIKE expression")
        self.like_exprs = like_exprs

    def _load_tag_ids(self):
        tag_ids = []
        for like_expr in self.like_exprs:
            tags = Tag.query.filter(Tag.tag.ilike(like_expr)).all()
            tag_ids += [t.id for t in tags]

        self.tag_ids = frozenset(tag_ids)

    @property
    def _tags_as_str(self):
        return ', '.join(self.like_exprs)

    def pprint_if(self):
        return f"Any medium with a tag like '{self._tags_as_str}'"

    def pprint_then(self):
        return f"should have a tag like '{self._tags_as_str}'."


class HasAnyTagsIn(HasAnyTags):
    def __init__(self, *names):
        HasAnyTags.__init__(self)
        if not names:
            raise Exception("You must configure at least one name")
        self.names = names

    def _load_tag_ids(self):
        tags = Tag.query.filter(Tag.tag.in_(self.names)).all()
        tag_ids = [t.id for t in tags]
        self.tag_ids = frozenset(tag_ids)

    @property
    def _tags_as_str(self):
        return ', '.join(self.names)

    def pprint_if(self):
        return f"Any medium with a tag in '{self._tags_as_str}'"

    def pprint_then(self):
        return f"should have a tag in '{self._tags_as_str}'."


class HasRating(object):
    def __init__(self, rating=None):
        self.rating = rating

    def get_medium_ids(self, session, filtering_medium_ids=[]):
        filters = []
        if self.rating:
            filters.append(Medium.rating == self.rating)
        else:
            filters.append(Medium.rating != 'u')

        if filtering_medium_ids:
            filters.append(Medium.id.in_(filtering_medium_ids))

        media = session.query(Medium).filter(*filters).all()

        return [m.id for m in media]

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
