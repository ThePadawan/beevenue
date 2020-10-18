from functools import wraps
from typing import Any, Callable, Optional, Tuple

Validator = Callable[..., Optional[Tuple[Any, int]]]

RequirementDecorator = Callable[..., Callable[..., Any]]


def requires(validator: Validator) -> RequirementDecorator:
    """Return decorator that calls validator before the decorated function.

    Note: validator functions must return falsey on success or anything
    truthy on failure.
    """

    def outer(route: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(route)
        def inner(*args: Any, **kwargs: Any) -> Any:
            return validator(*args, **kwargs) or route(*args, **kwargs)

        return inner

    return outer


def does_not_require_login(route: Any) -> Any:
    """Decorate an endpoint as completely public.

    This is in contrast to the default visibility, which is "public to users".
    You probably only want to use this decorator on /login.
    """
    route.is_public = True
    return route
