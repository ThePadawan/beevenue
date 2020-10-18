from typing import Optional, List

from ...spindex.spindex import SPINDEX
from .common import Iff


class All(Iff):
    """Select all media."""

    def get_medium_ids(
        self, filtering_medium_ids: Optional[List[int]] = None
    ) -> List[int]:
        return [m.id for m in SPINDEX.all()]

    def applies_to(self, medium_id: int) -> bool:
        return True

    def pprint_if(self) -> str:
        return "Any medium"
