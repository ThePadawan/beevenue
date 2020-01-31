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

    tag_aliases = [t[0] for t in tag_aliases]

    implied_tag_ids = session.query(TagImplication)\
        .filter(TagImplication.c.implying_tag_id.in_(tag_ids))\
        .with_entities(TagImplication.c.implied_tag_id)\
        .all()

    implied_tag_names = session.query(Tag)\
        .filter(Tag.id.in_(implied_tag_ids))\
        .with_entities(Tag.tag)\
        .all()

    implied_tag_names = [t[0] for t in implied_tag_names]

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
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __str__(self):
        return f"Medium {self.id} ({self.hash}) ({self.tag_names})"

    def __repr__(self):
        return self.__str__()


class _SpindexMedia(object):
    def __init__(self):
        self.data = {}

    def get_medium(self, id):
        return self.data[id]

    def get_all(self):
        return self.data.values()

    def add(self, item: SpindexedMedium):
        self.data[item.id] = item

    def remove(self, item: SpindexedMedium):
        self.remove_id(item.id)

    def remove_id(self, id: int):
        if id in self.data:
            del self.data[id]


class _CacheContextManager(AbstractContextManager):
    MEDIA = None

    def __init__(self, write_on_exit):
        self._to_write = None
        self.write_on_exit = write_on_exit

    def __enter__(self):
        if not _CacheContextManager.MEDIA:
            _CacheContextManager.MEDIA = _SpindexMedia()

        self._to_write = _CacheContextManager.MEDIA
        return self._to_write

    def __exit__(self, *details):
        if self.write_on_exit:
            _CacheContextManager.MEDIA = self._to_write


class Spindex(object):
    @property
    def _read_context(self):
        return _CacheContextManager(False)

    @property
    def _write_context(self):
        # Note: This *always* writes, even if no actual modification
        # took place. This makes it less laborious for the caller to explicitly
        # decide when to write or not (using a "dirty" flag or similar).
        return _CacheContextManager(True)

    def all(self):
        with self._read_context as c:
            return c.get_all()

    def get_medium(self, id):
        with self._read_context as c:
            return c.get_medium(id)

    def add_alias(self, tag_name, new_alias):
        with self._write_context as old:
            for m in old.get_all():
                if tag_name in m.tag_names:
                    m.tag_names.add(new_alias)

            return True

    def remove_alias(self, tag_name, former_alias):
        with self._write_context as old:
            for m in old.get_all():
                if former_alias in m.tag_names:
                    m.tag_names.remove(former_alias)

            return True

    def reindex_medium(self, session, id):
        with self._write_context as old:
            old.remove_id(id)

            new_spindexed_medium = _spindexed_medium(session, id)

            if not new_spindexed_medium:
                return False

            old.add(new_spindexed_medium)
            return True

    def rename_tag(self, old_name, new_name):
        with self._write_context as old:
            for m in old.get_all():
                if old_name in m.tag_names:
                    m.tag_names.remove(old_name)
                    m.tag_names.add(new_name)

            return True

    def add_implication(self, implying, implied):
        with self._write_context as old:
            for m in old.get_all():
                if implying in m.tag_names:
                    m.tag_names.add(implied)

            return True

    def remove_implication(self, implying, implied):
        with self._write_context as old:
            for m in old.get_all():
                if implying in m.tag_names:
                    m.tag_names.remove(implied)

            return True

    def remove_medium(self, id):
        with self._write_context as old:
            old.remove_id(id)

    def add_media(self, media):
        with self._write_context as old:
            for m in media:
                old.add(m)


SPINDEX = Spindex()
