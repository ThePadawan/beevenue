from flask import request, g

from contextlib import AbstractContextManager, contextmanager
from .load import single_load, SpindexedMedium
from ..cache import cache


class _SpindexMedia(object):
    def __init__(self):
        self.data = {}

    def get_medium(self, id):
        return self.data.get(id, None)

    def get_all(self):
        return self.data.values()

    def add(self, item: SpindexedMedium):
        self.data[item.id] = item

    def remove(self, item: SpindexedMedium):
        self.remove_id(item.id)

    def remove_id(self, id: int):
        if id in self.data:
            del self.data[id]


@contextmanager
def _cache_context(write_on_exit):
    if "spindex" in g:
        yield g.spindex(write_on_exit)
    else:
        yield request.spindex(write_on_exit)


class _InitializationContext(AbstractContextManager):
    def __init__(self):
        self._to_write = None

    def __enter__(self):
        self._to_write = _SpindexMedia()
        return self._to_write

    def __exit__(self, *details):
        cache.set("MEDIA", self._to_write)


class Spindex(object):
    @property
    def _read_context(self):
        return _cache_context(False)

    @property
    def _write_context(self):
        # Note: This *always* writes, even if no actual modification
        # took place. This makes it less laborious for the caller to explicitly
        # decide when to write or not (using a "dirty" flag or similar).
        return _cache_context(True)

    def all(self):
        with self._read_context as c:
            return c.get_all()

    def get_medium(self, id):
        with self._read_context as c:
            return c.get_medium(id)

    def get_media(self, ids):
        with self._read_context as c:
            return [c.get_medium(id) for id in ids]

    def add_alias(self, tag_name, new_alias):
        with self._write_context as ctx:
            for m in ctx.get_all():
                if tag_name in m.tag_names.searchable:
                    m.tag_names.searchable.add(new_alias)

            return True

    def remove_alias(self, tag_name, former_alias):
        with self._write_context as ctx:
            for m in ctx.get_all():
                if former_alias in m.tag_names.searchable:
                    m.tag_names.searchable.remove(former_alias)

            return True

    def reindex_medium(self, id):
        with self._write_context as ctx:
            ctx.remove_id(id)

            new_spindexed_medium = single_load(id)

            if not new_spindexed_medium:
                return False

            ctx.add(new_spindexed_medium)
            return True

    def rename_tag(self, old_name, new_name):
        with self._write_context as ctx:
            for m in ctx.get_all():
                if old_name in m.tag_names.innate:
                    m.tag_names.innate.remove(old_name)
                    m.tag_names.innate.add(new_name)
                if old_name in m.tag_names.searchable:
                    m.tag_names.searchable.remove(old_name)
                    m.tag_names.searchable.add(new_name)

            return True

    def add_implication(self, implying, implied):
        with self._write_context as ctx:
            for m in ctx.get_all():
                if implying in m.tag_names.searchable:
                    m.tag_names.searchable.add(implied)

            return True

    def remove_implication(self, implying, implied):
        with self._write_context as ctx:
            for m in ctx.get_all():
                if set([implying, implied]) <= m.tag_names.searchable:
                    m.tag_names.searchable.remove(implied)

            return True

    def remove_medium(self, id):
        with self._write_context as ctx:
            ctx.remove_id(id)

    def add_media(self, media):
        with _InitializationContext() as ctx:
            for m in media:
                ctx.add(m)


SPINDEX = Spindex()
