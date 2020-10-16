from ..cache import cache
from ..flask import BeevenueFlask
from .load.full import full_load
from .reindex import setup_signals


def init_app(app: BeevenueFlask) -> None:
    cache.init_app(app)
    full_load()
    setup_signals()
