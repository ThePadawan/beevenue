from ....marshmallow import ma
from ....models import Tag

from flask import current_app
from marshmallow import fields, Schema


class TagSchema(ma.ModelSchema):
    class Meta:
        model = Tag


class SpindexMediumSchema(Schema):
    id = fields.Int()
    tags = fields.Method("extract_innate_tags")
    similar = fields.Nested(
        "SimilarMediumSchema",
        many=True,
        only=["id", "mime_type", "rating", "thumbs", "tags"],
    )
    aspect_ratio = fields.Decimal(dump_to="aspectRatio", as_string=True)
    hash = fields.String()
    rating = fields.String()
    mime_type = fields.String()

    def extract_innate_tags(self, obj):
        return [t for t in obj.tag_names.innate]


class MediumWithThumbsSchema(SpindexMediumSchema):
    thumbs = fields.Method("get_thumbnail_urls")

    def get_thumbnail_urls(self, obj):
        return {
            size: f"/thumbs/{obj.id}"
            for name, size in current_app.config[
                "BEEVENUE_THUMBNAIL_SIZES"
            ].items()
        }


class SimilarMediumSchema(MediumWithThumbsSchema):
    pass


class SearchResultMediumSchema(MediumWithThumbsSchema):
    tiny_thumbnail = fields.Method("get_thumb", data_key="tinyThumbnail")

    def get_thumb(self, obj):
        import base64

        if obj.tiny_thumbnail:
            return base64.b64encode(obj.tiny_thumbnail).decode("utf-8")
        return None


class SearchResultsSchema(Schema):
    items = fields.Nested(
        SearchResultMediumSchema,
        many=True,
        only=["id", "aspect_ratio", "hash", "thumbs", "tiny_thumbnail"],
    )
    pageCount = fields.Int()
    pageNumber = fields.Int()
    pageSize = fields.Int()


medium_schema = SpindexMediumSchema()


search_results_schema = SearchResultsSchema()


class TagShowSchema(Schema):
    aliases = fields.Method("get_aliases")
    count = fields.Method("get_media_count")

    rating = fields.String()
    tag = fields.String()

    implied_by_this = fields.Method("get_implied_by_this")
    implying_this = fields.Method("get_implying_this")

    def get_aliases(self, obj):
        return [t.alias for t in obj.aliases]

    def get_media_count(self, obj):
        return len(obj.media)

    def get_implied_by_this(self, obj):
        return [t.tag for t in obj.implied_by_this]

    def get_implying_this(self, obj):
        return [t.tag for t in obj.implying_this]


tag_show_schema = TagShowSchema()


class TagStatisticsSchema(TagSchema):
    media_count = fields.Int(data_key="mediaCount")
    implying_this_count = fields.Int(data_key="implyingThisCount")
    implied_by_this_count = fields.Int(data_key="impliedByThisCount")

    class Meta:
        fields = (
            "id",
            "tag",
            "media_count",
            "rating",
            "implied_by_this_count",
            "implying_this_count",
        )


tag_statistics_schema = TagStatisticsSchema(many=True)


class MissingThumbnailSchema(Schema):
    mediumId = fields.Int()
    reasons = fields.List(fields.String)


missing_thumbnails_schema = MissingThumbnailSchema(many=True)
