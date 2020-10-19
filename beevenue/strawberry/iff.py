from typing import Optional, List

from flask import g

from .common import Iff


class All(Iff):
    """Select all media."""

    def get_medium_ids(
        self, filtering_medium_ids: Optional[List[int]] = None
    ) -> List[int]:
        return [m.medium_id for m in g.spindex.all()]

    def applies_to(self, medium_id: int) -> bool:
        return True

    def pprint_if(self) -> str:
        return "Any medium"
