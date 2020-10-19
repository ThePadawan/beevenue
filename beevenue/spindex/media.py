from typing import Dict, Iterable, Optional

from ..types import MediumDocument


class SpindexMedia:
    """Fancy dictionary containing all MediumDocument objects."""

    def __init__(self) -> None:
        self.data: Dict[int, MediumDocument] = {}

    def get_medium(self, medium_id: int) -> Optional[MediumDocument]:
        return self.data.get(medium_id, None)

    def get_all(self) -> Iterable[MediumDocument]:
        return self.data.values()

    def add(self, item: MediumDocument) -> None:
        self.data[item.medium_id] = item

    def remove_id(self, medium_id: int) -> Optional[MediumDocument]:
        if medium_id in self.data:
            item = self.data[medium_id]
            del self.data[medium_id]
            return item
        return None
