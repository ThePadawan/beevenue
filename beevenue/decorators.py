from functools import wraps


# Note: validator functions must return falsey on success
# or anything truthy on failure
def requires(validator):
    def outer(f):
        @wraps(f)
        def inner(*args, **kwargs):
            return validator(*args, **kwargs) or f(*args, **kwargs)

        return inner

    return outer


def does_not_require_login(f):
    f.is_public = True
    return f
