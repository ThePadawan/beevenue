from collections import defaultdict

from flask_caching import Cache

from ..models import Medium, TagImplication, TagAlias, Tag

from .spindex import SPINDEX
from .reindex import setup_signals


class SpindexedMedium(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __str__(self):
        return f"Medium {self.id} ({self.hash}) ({self.tag_names})"

    def __repr__(self):
        return self.__str__()


def init_app(app, session):
    cache = Cache(config={"CACHE_TYPE": "filesystem"})
    cache.init_app(app, config={"CACHE_TYPE": "filesystem"})

    SPINDEX.set_cache(cache)
    _full_load(session)
    setup_signals()


def _full_load(session):
    all_media = Medium.query.all()

    all_implications = session.query(TagImplication).all()

    all_tags = session.query(Tag).all()
    tag_name_by_id = {t.id: t.tag for t in all_tags}

    # if Id=3 implies Id=5, implied_by_this[3] == set([5])
    implied_by_this = defaultdict(set)

    # if Id=3 implies Id=5, implying_this[5] == set([3])
    implying_this = defaultdict(set)

    for implication in all_implications:
        implied_by_this[implication.implying_tag_id].add(implication.implied_tag_id)
        implying_this[implication.implied_tag_id].add(implication.implying_tag_id)

    all_aliases = session.query(TagAlias).all()

    aliases_by_id = defaultdict(set)
    for alias in all_aliases:
        aliases_by_id[alias.tag_id].add(alias.alias)

    media_to_cache = []

    for medium in all_media:
        tag_names = [t.tag for t in medium.tags]

        implied_ids = set()
        implying_ids = set()

        for tag in medium.tags:
            implied_ids |= implied_by_this[tag.id]
            implying_ids |= implying_this[tag.id]

        implied_tags = [tag_name_by_id[i] for i in implied_ids]

        alias_tags = set()

        for tag in medium.tags:
            alias_tags |= aliases_by_id[tag.id]

        tag_names = set(tag_names) | set(implied_tags) | set(alias_tags)

        medium_to_cache = SpindexedMedium(
            id=medium.id,
            hash=medium.hash,
            rating=medium.rating,
            tag_names=tag_names
        )

        media_to_cache.append(medium_to_cache)

    global SPINDEX
    SPINDEX.add_media(media_to_cache)
