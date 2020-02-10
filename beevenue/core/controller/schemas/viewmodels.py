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
        "SimilarMediumSchema", many=True, exclude=["similar"]
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
            size: f"/thumbs/{obj.id}/{name}.jpg"
            for name, size in current_app.config[
                "BEEVENUE_THUMBNAIL_SIZES"
            ].items()
        }


class SimilarMediumSchema(MediumWithThumbsSchema):
    pass


class SearchResultMediumSchema(MediumWithThumbsSchema):
    pass


class SearchResultsSchema(Schema):
    items = fields.Nested(SearchResultMediumSchema, many=True)
    pageCount = fields.Int()
    pageNumber = fields.Int()
    pageSize = fields.Int()


medium_schema = SpindexMediumSchema()


search_results_schema = SearchResultsSchema()


class TagShowSchema(Schema):
    aliases = fields.List(fields.String(attribute="alias"))
    count = fields.Method("get_media_count")

    implied_by_this = fields.Method("get_implied_by_this")
    implying_this = fields.Method("get_implying_this")

    def get_media_count(self, obj):
        return len(obj.media)

    def get_implied_by_this(self, obj):
        return [t.tag for t in obj.implied_by_this]

    def get_implying_this(self, obj):
        return [t.tag for t in obj.implying_this]


tag_show_schema = TagShowSchema()


class TagStatisticsSchema(TagSchema):
    count = fields.Method("get_media_count")

    def get_media_count(self, obj):
        return len(obj.media)

    class Meta:
        fields = ("id", "tag", "count")


tag_statistics_schema = TagStatisticsSchema(many=True)


class MissingThumbnailSchema(Schema):
    mediumId = fields.Int()
    reasons = fields.List(fields.String)


missing_thumbnails_schema = MissingThumbnailSchema(many=True)
