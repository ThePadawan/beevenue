import base64
from typing import List, Optional

from marshmallow import fields, Schema

from .models import Tag
from .spindex.models import SpindexedMedium


class SpindexMediumSchema(Schema):
    id = fields.Int()
    tags = fields.Method("extract_innate_tags")
    aspect_ratio = fields.String(data_key="aspectRatio")
    hash = fields.String()
    rating = fields.String()
    mime_type = fields.String()

    def extract_innate_tags(self, obj: SpindexedMedium) -> List[str]:
        return [t for t in obj.tag_names.innate]


class SpindexMediumDetailSchema(SpindexMediumSchema):
    similar = fields.Nested("SpindexMediumDetailSchema", many=True, only=["id"])


class PaginationMediumSchema(SpindexMediumSchema):
    tiny_thumbnail = fields.Method("get_thumb", data_key="tinyThumbnail")

    def get_thumb(self, obj: SpindexedMedium) -> Optional[str]:
        if obj.tiny_thumbnail:
            return base64.b64encode(obj.tiny_thumbnail).decode("utf-8")
        return None


class PaginationSchema(Schema):
    items = fields.Nested(
        PaginationMediumSchema,
        many=True,
        only=["id", "aspect_ratio", "hash", "tiny_thumbnail"],
    )
    pageCount = fields.Int()
    pageNumber = fields.Int()
    pageSize = fields.Int()


class TagShowSchema(Schema):
    aliases = fields.Method("get_aliases")
    count = fields.Method("get_media_count")

    rating = fields.String()
    tag = fields.String()

    implied_by_this = fields.Method("get_implied_by_this")
    implying_this = fields.Method("get_implying_this")

    def get_aliases(self, obj: Tag) -> List[str]:
        return [t.alias for t in obj.aliases]

    def get_media_count(self, obj: Tag) -> int:
        return len(obj.media)

    def get_implied_by_this(self, obj: Tag) -> List[str]:
        return [t.tag for t in obj.implied_by_this]

    def get_implying_this(self, obj: Tag) -> List[str]:
        return [t.tag for t in obj.implying_this]


class TagSummaryItemSchema(Schema):
    media_count = fields.Int(data_key="mediaCount")
    implied_by_something = fields.Bool(data_key="impliedBySomething")

    class Meta:
        fields = (
            "id",
            "tag",
            "media_count",
            "rating",
            "implied_by_something",
        )


class TagSummarySchema(Schema):
    tags = fields.Nested(TagSummaryItemSchema, many=True)


medium_detail_schema = SpindexMediumDetailSchema()
pagination_schema = PaginationSchema()
tag_summary_schema = TagSummarySchema()
tag_show_schema = TagShowSchema()
