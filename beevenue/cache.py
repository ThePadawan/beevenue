from flask_caching import Cache

cache = Cache(config={"CACHE_TYPE": "filesystem", "CACHE_DEFAULT_TIMEOUT": 0})


def init_app(app):
    cache.init_app(app)
