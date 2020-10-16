from abc import ABC, abstractmethod

from .media import SpindexMedia


class SpindexCallable(ABC):
    @abstractmethod
    def __call__(self, do_write: bool) -> SpindexMedia:
        """Get the current Spindex implementation."""

    @abstractmethod
    def exit(self) -> None:
        """If necessary, persist changes made on the Spindex on the backing storage."""
