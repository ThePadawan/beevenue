
from marshmallow import fields, Schema


class PaginationQueryParamsSchema(Schema):
    pageNumber = fields.Int(required=True)
    pageSize = fields.Int(required=True)


pagination_query_params_schema = PaginationQueryParamsSchema()


class SearchQueryParamsSchema(PaginationQueryParamsSchema):
    q = fields.String(required=True)


search_query_params_schema = SearchQueryParamsSchema()
