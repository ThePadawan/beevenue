from typing import List

from ...spindex.models import SpindexedMedium


class MediumDetail(SpindexedMedium):
    def __init__(self, medium: SpindexedMedium, similar: List[SpindexedMedium]):
        self.__dict__.update(medium.__dict__)
        self.similar = similar
