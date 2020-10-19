from typing import List

from ..types import MediumDocument


class MediumDetail:
    """Viewmodel extending MediumDocument.

    Holds info about "similar" media as well."""

    def __init__(self, medium: MediumDocument, similar: List[MediumDocument]):
        self.__dict__.update(medium.__dict__)
        self.similar = similar
