from functools import wraps
from flask import request, jsonify

from . import notifications
from .schemas import pagination_query_params_schema


# Note: validator functions must return falsey on success
# or anything truthy on failure
def _requires(validator):
    def outer(f):
        @wraps(f)
        def inner(*args, **kwargs):
            return validator(*args, **kwargs) or f(*args, **kwargs)
        return inner
    return outer


def requires_permission(permission):
    def validator(*args, **kwargs):
        p = permission
        if callable(p):
            p = p(*args, **kwargs)

        if not p.can():
            return notifications.no_permission(), 403
    return _requires(validator)


def _requires_schema(validate):
    def validator(*args, **kwargs):
        validation_errors = validate(request)
        if validation_errors:
            return jsonify(validation_errors), 400
    return _requires(validator)


# View decorator that validates requests' query params
# against the specified schema.
def requires_query_params(schema):
    return _requires_schema(lambda r: schema.validate(r.args))


# View decorator that validates request's json body
# against the specified schema.
def requires_json_body(schema):
    return _requires_schema(lambda r: schema.validate(r.json))


def paginated():
    return requires_query_params(schema=pagination_query_params_schema)
