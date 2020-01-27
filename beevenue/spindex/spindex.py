from contextlib import AbstractContextManager
from ..models import Medium, Tag, TagAlias, TagImplication


def _spindexed_medium(session, id):
    matching_media = session.query(Medium).filter_by(id=id).all()
    if not matching_media:
        return None

    matching_medium = matching_media[0]

    tag_ids = [t.id for t in matching_medium.tags]

    tag_aliases = session.query(TagAlias)\
        .filter(TagAlias.tag_id.in_(tag_ids))\
        .with_entities(TagAlias.alias)\
        .all()

    implied_tag_ids = session.query(TagImplication)\
        .filter(TagImplication.c.implying_tag_id.in_(tag_ids))\
        .with_entities(TagImplication.c.implied_tag_id)\
        .all()

    implied_tag_names = session.query(Tag)\
        .filter(Tag.id.in_(implied_tag_ids))\
        .with_entities(Tag.tag)\
        .all()

    tag_names = set([t.tag for t in matching_medium.tags]) \
        | set(tag_aliases) \
        | set(implied_tag_names)

    return SpindexedMedium(
        id=matching_medium.id,
        rating=matching_medium.rating,
        hash=matching_medium.hash,
        tag_names=tag_names
    )


class SpindexedMedium(object):
    def __init__(self, id, hash, rating, tag_names):
        self.id = id
        self.hash = hash
        self.rating = rating
        self.tag_names = set(tag_names)

    def __str__(self):
        return f"Medium {self.id} ({self.hash}) ({self.tag_names})"

    def __repr__(self):
        return self.__str__()


class _SpindexCache(AbstractContextManager):
    def __init__(self, cache):
        self._cache = cache
        self._to_set = None

    def __enter__(self):
        return self

    def get(self):
        return self._cache.get("MEDIA") or set()

    def set(self, new):
        self._to_set = set(new)

    def __exit__(self, *details):
        if self._to_set:
            self._cache.set("MEDIA", self._to_set)


class Spindex(object):
    def set_cache(self, cache):
        self._cache = cache
        self._cache.clear()

    def all(self):
        with self._cache_context as c:
            return c.get()

    @property
    def _cache_context(self):
        return _SpindexCache(self._cache)

    def add_alias(self, tag_name, new_alias):
        with self._cache_context as c:
            old = c.get()

            for m in old:
                if tag_name in m.tag_names:
                    m.tag_names.add(new_alias)

            c.set(old)
            return True

    def remove_alias(self, tag_name, former_alias):
        with self._cache_context as c:
            old = c.get()

            for m in old:
                if former_alias in m.tag_names:
                    m.tag_names.remove(former_alias)

            c.set(old)
            return True

    def reindex_medium(self, session, id):
        with self._cache_context as c:
            old = c.get()
            found_media = [m for m in old if m.id == id]

            new_spindexed_medium = _spindexed_medium(session, id)

            if not new_spindexed_medium:
                return False

            if found_media:
                found_medium = found_media[0]
                old.remove(found_medium)

            old.add(new_spindexed_medium)

            c.set(old)
            return True

    def rename_tag(self, old_name, new_name):
        with self._cache_context as c:
            old = c.get()
            for m in old:
                if old_name in m.tag_names:
                    m.tag_names.remove(old_name)
                    m.tag_names.add(new_name)

            c.set(old)
            return True

    def add_implication(self, implying, implied):
        with self._cache_context as c:
            old = c.get()

            for m in old:
                if implying in m.tag_names:
                    m.tag_names.add(implied)

            c.set(old)
            return True

    def remove_implication(self, implying, implied):
        with self._cache_context as c:
            old = c.get()

            for m in old:
                if implying in m.tag_names:
                    m.tag_names.remove(implied)

            c.set(old)
            return True

    def remove_medium(self, id):
        with self._cache_context as c:
            old = c.get()
            new = [m for m in old if m.id != id]

            c.set(new)
            return (len(old), len(new))

    def add_media(self, media):
        with self._cache_context as c:
            old = c.get()
            for m in media:
                old.add(m)

            c.set(old)


SPINDEX = Spindex()
