from abc import ABC, abstractmethod
from collections import defaultdict, deque
from typing import List, Set, Tuple
from ..models import Medium, Tag, TagAlias, TagImplication


class SpindexedMediumTagNames(object):
    def __init__(self, innate, searchable):
        self.innate = set(innate)
        self.searchable = set(searchable)


class SpindexedMedium(object):
    @classmethod
    def create(cls, medium, tag_names):
        # Pluck 1:1 fields from entity to kwargs
        fields = [
            "id",
            "aspect_ratio",
            "mime_type",
            "hash",
            "rating",
            "tiny_thumbnail",
        ]
        new_kwargs = {}
        for f in fields:
            new_kwargs[f] = getattr(medium, f)

        new_kwargs.update({"tag_names": tag_names})
        return cls(**new_kwargs)

    def __init__(self, **kwargs):
        self.id = None
        self.hash = None
        self.mime_type = None
        self.__dict__.update(kwargs)

    def __str__(self):
        return f"<SpindexedMedium {self.id}>"

    def __repr__(self):
        return self.__str__()


def single_load(session, id: int):
    matching_media = session.query(Medium).filter_by(id=id).all()
    if not matching_media:
        return None

    matching_medium = matching_media[0]

    return _create_spindexed_medium(
        _SingleLoadDataSource(session), matching_medium
    )


def full_load(session):
    all_media = Medium.query.all()

    all_implications = session.query(TagImplication).all()

    all_tags = session.query(Tag).all()
    tag_name_by_id = {t.id: t.tag for t in all_tags}

    # if Id=3 implies Id=5, implied_by_this[3] == set([5])
    implied_by_this = defaultdict(set)

    for i in all_implications:
        implied_by_this[i.implying_tag_id].add(i.implied_tag_id)

    all_aliases = session.query(TagAlias).all()

    aliases_by_id = defaultdict(set)
    for alias in all_aliases:
        aliases_by_id[alias.tag_id].add(alias.alias)

    media_to_cache = []

    data_source = _FullLoadDataSource(
        implied_by_this, aliases_by_id, tag_name_by_id
    )

    for medium in all_media:
        medium_to_cache = _create_spindexed_medium(data_source, medium)
        media_to_cache.append(medium_to_cache)

    return media_to_cache


class _AbstractDataSource(ABC):
    @abstractmethod
    def alias_names(self, tag_ids: List[int]) -> Set[str]:
        pass

    def implied(self, tag_ids: List[int]) -> Tuple[Set[str], Set[str]]:
        pass


class _SingleLoadDataSource(_AbstractDataSource):
    def __init__(self, session):
        self.session = session

    def alias_names(self, tag_ids):
        tag_alias_entities = (
            self.session.query(TagAlias)
            .filter(TagAlias.tag_id.in_(tag_ids))
            .with_entities(TagAlias.alias)
            .all()
        )

        return set([t[0] for t in tag_alias_entities])

    def implied(self, tag_ids: List[int]):
        implied_tag_id_entities = (
            self.session.query(TagImplication)
            .filter(TagImplication.c.implying_tag_id.in_(tag_ids))
            .with_entities(TagImplication.c.implied_tag_id)
            .all()
        )
        implied_tag_ids = set([t[0] for t in implied_tag_id_entities])

        implied_tag_name_entities = (
            self.session.query(Tag)
            .filter(Tag.id.in_(implied_tag_ids))
            .with_entities(Tag.tag)
            .all()
        )
        implied_tag_names = set([t[0] for t in implied_tag_name_entities])

        return implied_tag_ids, implied_tag_names


class _FullLoadDataSource(_AbstractDataSource):
    def __init__(self, implied_by_this, aliases_by_id, tag_name_by_id):
        self.implied_by_this = implied_by_this
        self.aliases_by_id = aliases_by_id
        self.tag_name_by_id = tag_name_by_id

    def alias_names(self, tag_ids):
        result = set()
        for tag_id in tag_ids:
            result |= self.aliases_by_id[tag_id]
        return result

    def implied(self, tag_ids):
        implied_ids = set()
        for tag_id in tag_ids:
            implied_ids |= self.implied_by_this[tag_id]

        implied_names = set([self.tag_name_by_id[i] for i in implied_ids])

        return implied_ids, implied_names


def _create_spindexed_medium(data_source: _AbstractDataSource, medium):
    # First, get innate tags. These will never change.
    innate_tag_names = set([t.tag for t in medium.tags])

    # Follow chain of implications. Gather implied tags
    # and aliases until that queue is empty.
    extra_searchable_tags = _gather_extra(data_source, medium)

    searchable_tag_names = innate_tag_names | extra_searchable_tags

    tag_names = SpindexedMediumTagNames(innate_tag_names, searchable_tag_names)

    return SpindexedMedium.create(medium, tag_names)


def _gather_extra(data_source: _AbstractDataSource, medium):
    extra: Set[str] = set()

    q = deque()
    initial_tag_ids = set([t.id for t in medium.tags])
    q.append(initial_tag_ids)

    while q:
        tag_ids: List[int] = q.pop()
        if not tag_ids:
            continue

        extra |= data_source.alias_names(tag_ids)

        implied_tag_ids, implied_tag_names = data_source.implied(tag_ids)
        extra |= implied_tag_names

        q.append(implied_tag_ids)

    return extra
