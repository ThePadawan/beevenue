from typing import List

from ..types import MediumDocument


class MediumDetail(  # pylint: disable=too-many-instance-attributes
    MediumDocument
):
    """Viewmodel extending MediumDocument.

    Holds info about "similar" media as well."""

    __slots__ = ["similar"]

    similar: List[MediumDocument]

    def __init__(self, medium: MediumDocument, similar: List[MediumDocument]):
        self.medium_id = medium.medium_id
        self.aspect_ratio = medium.aspect_ratio
        self.medium_hash = medium.medium_hash
        self.mime_type = medium.mime_type
        self.rating = medium.rating
        self.tiny_thumbnail = medium.tiny_thumbnail
        self.tag_names = medium.tag_names

        self.similar = similar
