from typing import Dict, Iterable, Optional

from .models import SpindexedMedium


class SpindexMedia(object):
    def __init__(self) -> None:
        self.data: Dict[int, SpindexedMedium] = {}

    def get_medium(self, id: int) -> Optional[SpindexedMedium]:
        return self.data.get(id, None)

    def get_all(self) -> Iterable[SpindexedMedium]:
        return self.data.values()

    def add(self, item: SpindexedMedium) -> None:
        self.data[item.id] = item

    def remove(self, item: SpindexedMedium) -> Optional[SpindexedMedium]:
        return self.remove_id(item.id)

    def remove_id(self, id: int) -> Optional[SpindexedMedium]:
        if id in self.data:
            item = self.data[id]
            del self.data[id]
            return item
        return None
