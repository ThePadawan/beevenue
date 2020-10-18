from typing import List

from ...spindex.models import SpindexedMedium


class MediumDetail:
    """Viewmodel extending SpindexedMedium. Holds more details about medium."""

    def __init__(self, medium: SpindexedMedium, similar: List[SpindexedMedium]):
        self.__dict__.update(medium.__dict__)
        self.similar = similar
