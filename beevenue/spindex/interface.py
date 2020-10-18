from abc import ABC, abstractmethod

from .media import SpindexMedia


class SpindexCallable(ABC):
    """Abstract base class for all SpindexMedia holders.

    __call__ is used to lazily access SpindexMedia.
    exit is called on request end to persist changes.
    """

    @abstractmethod
    def __call__(self, do_write: bool) -> SpindexMedia:
        """Get the current Spindex implementation."""

    @abstractmethod
    def exit(self) -> None:
        """Persist potential changes made to Spindex to the backing storage."""
