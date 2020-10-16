from functools import wraps
from typing import Any, Callable, Optional, Tuple

Validator = Callable[..., Optional[Tuple[Any, int]]]

RequirementDecorator = Callable[..., Callable[..., Any]]


# Note: validator functions must return falsey on success
# or anything truthy on failure
def requires(validator: Validator) -> RequirementDecorator:
    def outer(f: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(f)
        def inner(*args: Any, **kwargs: Any) -> Any:
            return validator(*args, **kwargs) or f(*args, **kwargs)

        return inner

    return outer


def does_not_require_login(f: Any) -> Any:
    f.is_public = True
    return f
