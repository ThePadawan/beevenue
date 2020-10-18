from contextlib import AbstractContextManager, contextmanager
from typing import Any, ContextManager, Generator, Iterable, List, Optional

from flask import g

from beevenue import request

from ..cache import cache
from .interface import SpindexCallable
from .load.single import single_load
from .media import SpindexMedia
from .models import SpindexedMedium


class CachedSpindexCallable(SpindexCallable):
    """Holder class for the Spindex currently in memory.

    Is lazily initialized from cache, and only persists back into cache
    at the end of each request, and if a write is necessary.

    This means that multiple reads in a row are performed very fast and
    in-memory."""

    def __init__(self) -> None:
        self.spindex: Optional[SpindexMedia] = None
        self.do_write = False

    def __call__(self, do_write: bool) -> SpindexMedia:
        self.do_write |= do_write
        if self.spindex is None:
            self.spindex = cache.get("MEDIA")
        return self.spindex

    def exit(self) -> None:
        if self.do_write:
            cache.set("MEDIA", self.spindex)


class _InitializationContext(AbstractContextManager):
    """Context manager used to fill spindex at application startup.

    Always writes on __exit__."""

    def __init__(self) -> None:
        self._to_write: Optional[SpindexMedia] = None

    def __enter__(self) -> SpindexMedia:
        self._to_write = SpindexMedia()
        return self._to_write

    def __exit__(self, exc: Any, value: Any, tb: Any) -> None:
        cache.set("MEDIA", self._to_write)


@contextmanager
def _cache_context(write_on_exit: bool) -> Generator[SpindexMedia, None, None]:
    if "spindex" in g:
        yield g.spindex(write_on_exit)
    else:
        yield request.spindex(write_on_exit)


class Spindex:
    """Collection of queries on the in-memory document database of media."""

    @property
    def _read_context(self) -> ContextManager[SpindexMedia]:
        return _cache_context(False)

    @property
    def _write_context(self) -> ContextManager[SpindexMedia]:
        # Note: This *always* writes, even if no actual modification
        # took place. This makes it less laborious for the caller to explicitly
        # decide when to write or not (using a "dirty" flag or similar).
        return _cache_context(True)

    def all(self) -> Iterable[SpindexedMedium]:
        with self._read_context as context:
            return context.get_all()

    def get_medium(self, medium_id: int) -> Optional[SpindexedMedium]:
        with self._read_context as context:
            return context.get_medium(medium_id)

    def get_media(self, ids: Iterable[int]) -> List[SpindexedMedium]:
        with self._read_context as context:
            result = []
            for medium_id in ids:
                maybe_medium = context.get_medium(medium_id)
                if maybe_medium:
                    result.append(maybe_medium)
            return result

    def add_alias(self, tag_name: str, new_alias: str) -> bool:
        with self._write_context as ctx:
            for medium in ctx.get_all():
                if tag_name in medium.tag_names.searchable:
                    medium.tag_names.searchable.add(new_alias)

            return True

    def remove_alias(self, former_alias: str) -> bool:
        with self._write_context as ctx:
            for medium in ctx.get_all():
                if former_alias in medium.tag_names.searchable:
                    medium.tag_names.searchable.remove(former_alias)

            return True

    def reindex_medium(self, medium_id: int) -> bool:
        with self._write_context as ctx:
            ctx.remove_id(medium_id)

            new_spindexed_medium = single_load(medium_id)

            if not new_spindexed_medium:
                return False

            ctx.add(new_spindexed_medium)
            return True

    def rename_tag(self, old_name: str, new_name: str) -> bool:
        with self._write_context as ctx:
            for medium in ctx.get_all():
                if old_name in medium.tag_names.innate:
                    medium.tag_names.innate.remove(old_name)
                    medium.tag_names.innate.add(new_name)
                if old_name in medium.tag_names.searchable:
                    medium.tag_names.searchable.remove(old_name)
                    medium.tag_names.searchable.add(new_name)

            return True

    def add_implication(self, implying: str, implied: str) -> bool:
        with self._write_context as ctx:
            for medium in ctx.get_all():
                if implying in medium.tag_names.searchable:
                    medium.tag_names.searchable.add(implied)

            return True

    def remove_implication(self, implying: str, implied: str) -> bool:
        with self._write_context as ctx:
            for medium in ctx.get_all():
                if set([implying, implied]) <= medium.tag_names.searchable:
                    medium.tag_names.searchable.remove(implied)

            return True

    def remove_medium(self, medium_id: int) -> Optional[SpindexedMedium]:
        with self._write_context as ctx:
            return ctx.remove_id(medium_id)

    def add_media(self, media: Iterable[SpindexedMedium]) -> None:
        with _InitializationContext() as ctx:
            for medium in media:
                ctx.add(medium)


SPINDEX = Spindex()
