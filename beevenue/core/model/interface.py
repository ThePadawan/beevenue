from typing import Optional


class ThumbnailingResult(object):
    def __init__(
        self, success: bool, aspect_ratio: Optional[float], error: Optional[str]
    ):
        self.success = success
        self.aspect_ratio = aspect_ratio
        self.error = error

    @staticmethod
    def from_success(aspect_ratio: float) -> "ThumbnailingResult":
        return ThumbnailingResult(True, aspect_ratio, error=None)

    @staticmethod
    def from_failure(error: str) -> "ThumbnailingResult":
        return ThumbnailingResult(False, aspect_ratio=None, error=error)
