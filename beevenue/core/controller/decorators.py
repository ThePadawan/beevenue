from functools import wraps
from flask import request, jsonify

from ..model import notifications
from .schemas.query import pagination_query_params_schema


def requires_permission(permission):
    def outer(f):
        @wraps(f)
        def inner(*args, **kwargs):
            p = permission
            if callable(p):
                p = p(*args, **kwargs)

            if not p.can():
                return notifications.no_permission(), 403
            return f(*args, **kwargs)
        return inner
    return outer


def _requires_schema(schema, validate):
    def outer(f):
        @wraps(f)
        def inner(*args, **kwargs):
            validation_errors = validate(request)
            if validation_errors:
                return jsonify(validation_errors), 400

            return f(*args, **kwargs)
        return inner
    return outer


# View decorator that validates requests' query params
# against the specified schema.
def requires_query_params(schema):
    return _requires_schema(schema, lambda r: schema.validate(r.args))


# View decorator that validates request's json body 
# against the specified schema.
def requires_json_body(schema):
    return _requires_schema(schema, lambda r: schema.validate(r.json))


def paginated():
    return requires_query_params(schema=pagination_query_params_schema)
