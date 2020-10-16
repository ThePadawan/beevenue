from flask_caching import Cache

from beevenue.flask import BeevenueFlask

cache = Cache(config={"CACHE_TYPE": "filesystem", "CACHE_DEFAULT_TIMEOUT": 0})


def init_app(app: BeevenueFlask) -> None:
    cache.init_app(app)
