from typing import List

from .common import Then


class Fail(Then):
    def get_medium_ids(self, filtering_medium_ids: List[int] = []) -> List[int]:
        return []

    def applies_to(self, medium_id: int) -> bool:
        return False

    def pprint_then(self) -> str:
        return "should not exist."
