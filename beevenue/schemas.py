from typing import Any, Callable, Dict, List, Optional, Tuple

from flask import jsonify, Request
from marshmallow import fields, Schema

from beevenue.request import request

from .decorators import RequirementDecorator, requires


# View decorator that validates requests' query params
# against the specified schema.
def requires_query_params(schema: Schema) -> RequirementDecorator:
    return _requires_schema(lambda r: schema.validate(r.args))


# View decorator that validates request's json body
# against the specified schema.
def requires_json_body(schema: Schema) -> RequirementDecorator:
    return _requires_schema(lambda r: schema.validate(r.json))


def _requires_schema(
    validate: Callable[[Request], Dict[str, List[str]]]
) -> RequirementDecorator:
    def validator(*args: Any, **kwargs: Any) -> Optional[Tuple[Any, int]]:
        validation_errors = validate(request)
        if validation_errors:
            return jsonify(validation_errors), 400
        return None

    return requires(validator)


class PaginationQueryParamsSchema(Schema):
    pageNumber = fields.Int(required=True)
    pageSize = fields.Int(required=True)


paginated = requires_query_params(PaginationQueryParamsSchema())
