
from marshmallow import fields, Schema

from ....schemas import (
    PaginationQueryParamsSchema,
    requires_json_body,
    requires_query_params
)


class SearchQueryParamsSchema(PaginationQueryParamsSchema):
    q = fields.String(required=True)


search_query_params_schema = requires_query_params(SearchQueryParamsSchema())


class UpdateTagSchema(Schema):
    newName = fields.String(required=True)


update_tag_schema = requires_json_body(UpdateTagSchema())


class AddTagsBatchSchema(Schema):
    tags = fields.List(fields.String, required=True)
    mediumIds = fields.List(fields.Int, required=True)


add_tags_batch_schema = requires_json_body(AddTagsBatchSchema())
