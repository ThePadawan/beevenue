from contextlib import AbstractContextManager
from .load import single_load, SpindexedMedium


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
            
    def get_media(self, ids):
        with self._read_context as c:
            return [c.get_medium(id) for id in ids]

    def add_alias(self, tag_name, new_alias):
        with self._write_context as old:
            for m in old.get_all():
                if tag_name in m.tag_names.searchable:
                    m.tag_names.searchable.add(new_alias)

            return True

    def remove_alias(self, tag_name, former_alias):
        with self._write_context as old:
            for m in old.get_all():
                if former_alias in m.tag_names.searchable:
                    m.tag_names.searchable.remove(former_alias)

            return True

    def reindex_medium(self, session, id):
        with self._write_context as old:
            old.remove_id(id)

            new_spindexed_medium = single_load(session, id)

            if not new_spindexed_medium:
                return False

            old.add(new_spindexed_medium)
            return True

    def rename_tag(self, old_name, new_name):
        with self._write_context as old:
            for m in old.get_all():
                if old_name in m.tag_names.innate:
                    m.tag_names.innate.remove(old_name)
                    m.tag_names.innate.add(new_name)
                if old_name in m.tag_names.searchable:
                    m.tag_names.searchable.remove(old_name)
                    m.tag_names.searchable.add(new_name)

            return True

    def add_implication(self, implying, implied):
        with self._write_context as old:
            for m in old.get_all():
                if implying in m.tag_names.searchable:
                    m.tag_names.searchable.add(implied)

            return True

    def remove_implication(self, implying, implied):
        with self._write_context as old:
            for m in old.get_all():
                if implying in m.tag_names.searchable:
                    m.tag_names.searchable.remove(implied)

            return True

    def remove_medium(self, id):
        with self._write_context as old:
            old.remove_id(id)

    def add_media(self, media):
        with self._write_context as old:
            for m in media:
                old.add(m)


SPINDEX = Spindex()
