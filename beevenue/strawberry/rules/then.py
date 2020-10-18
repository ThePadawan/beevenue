from typing import List, Optional

from .common import Then


class Fail(Then):
    """Fail every medium.

    This allows you to construct rules of the form "No media to which this Iff
    applies should exist at all."""

    def get_medium_ids(
        self, filtering_medium_ids: Optional[List[int]] = None
    ) -> List[int]:
        return []

    def applies_to(self, medium_id: int) -> bool:
        return False

    def pprint_then(self) -> str:
        return "should not exist."
