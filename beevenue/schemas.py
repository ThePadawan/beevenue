from typing import Any, Callable, Dict, List, Optional, Tuple

from flask import jsonify, Request
from marshmallow import fields, Schema

from beevenue import request

from .decorators import RequirementDecorator, requires


def requires_query_params(schema: Schema) -> RequirementDecorator:
    """Validate requests' query params against the specified schema."""

    return _requires_schema(lambda r: schema.validate(r.args))


def requires_json_body(schema: Schema) -> RequirementDecorator:
    """Validate requests' json body against the specified schema."""
    return _requires_schema(lambda r: schema.validate(r.json))


def _requires_schema(
    validate: Callable[[Request], Dict[str, List[str]]]
) -> RequirementDecorator:
    """Call specified validator against the current request."""

    def validator(*_: Any, **__: Any) -> Optional[Tuple[Any, int]]:
        validation_errors = validate(request)
        if validation_errors:
            return jsonify(validation_errors), 400
        return None

    return requires(validator)


class PaginationQueryParamsSchema(Schema):
    """Query parameters required for all paginated queries."""

    pageNumber = fields.Int(required=True)
    pageSize = fields.Int(required=True)


paginated = requires_query_params(PaginationQueryParamsSchema())
