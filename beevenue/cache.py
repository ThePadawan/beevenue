"""Top-level access to the Flask cache."""

from flask_caching import Cache

from .flask import BeevenueFlask

cache = Cache(config={"CACHE_TYPE": "filesystem", "CACHE_DEFAULT_TIMEOUT": 0})


def init_app(app: BeevenueFlask) -> None:
    """Initialize cache component of the application."""
    cache.init_app(app)
