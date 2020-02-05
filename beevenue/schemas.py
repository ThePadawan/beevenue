from flask import request, jsonify
from marshmallow import fields, Schema

from .decorators import requires


# View decorator that validates requests' query params
# against the specified schema.
def requires_query_params(schema):
    return _requires_schema(lambda r: schema.validate(r.args))


# View decorator that validates request's json body
# against the specified schema.
def requires_json_body(schema):
    return _requires_schema(lambda r: schema.validate(r.json))


def _requires_schema(validate):
    def validator(*args, **kwargs):
        validation_errors = validate(request)
        if validation_errors:
            return jsonify(validation_errors), 400
    return requires(validator)


class PaginationQueryParamsSchema(Schema):
    pageNumber = fields.Int(required=True)
    pageSize = fields.Int(required=True)


paginated = requires_query_params(PaginationQueryParamsSchema())
