from typing import List

from ...spindex.spindex import SPINDEX
from .common import Iff


class All(Iff):
    def get_medium_ids(self, filtering_medium_ids: List[int] = []) -> List[int]:
        return [m.id for m in SPINDEX.all()]

    def applies_to(self, medium_id: int) -> bool:
        return True

    def pprint_if(self) -> str:
        return "Any medium"
