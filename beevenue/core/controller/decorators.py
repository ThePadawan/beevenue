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


# View decorator that validates query params against the specified schema.
# By default, validates for the presence of pagination parameters.
def paginated(schema=pagination_query_params_schema):
    def outer(f):

        @wraps(f)
        def inner(*args, **kwargs):
            validation_errors = schema.validate(request.args)
            if validation_errors:
                return jsonify(validation_errors), 400

            return f(*args, **kwargs)
        return inner
    return outer
