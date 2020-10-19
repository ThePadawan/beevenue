from abc import ABC, abstractmethod

from .media import SpindexMedia


class SpindexSessionFactory(ABC):
    """Abstract base class for all session factories.

    get is used to lazily create a session.
    exit (to be called on request end) persists changes (if necessary).
    """

    @abstractmethod
    def get(self, do_write: bool) -> SpindexMedia:
        """Get the current Spindex implementation."""

    @abstractmethod
    def exit(self) -> None:
        """Persist potential changes made to Spindex to the backing storage."""
