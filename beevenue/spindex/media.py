from typing import Dict, Iterable, Optional

from .models import SpindexedMedium


class SpindexMedia:
    """Fancy dictionary containing all SpindexedMedium objects."""

    def __init__(self) -> None:
        self.data: Dict[int, SpindexedMedium] = {}

    def get_medium(self, medium_id: int) -> Optional[SpindexedMedium]:
        return self.data.get(medium_id, None)

    def get_all(self) -> Iterable[SpindexedMedium]:
        return self.data.values()

    def add(self, item: SpindexedMedium) -> None:
        self.data[item.id] = item

    def remove_id(self, medium_id: int) -> Optional[SpindexedMedium]:
        if medium_id in self.data:
            item = self.data[medium_id]
            del self.data[medium_id]
            return item
        return None
