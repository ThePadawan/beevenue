from .reindex import setup_signals
from .load import full_load
from .spindex import SPINDEX

from ..cache import cache


def init_app(app):
    cache.init_app(app)
    SPINDEX.add_media(full_load())
    setup_signals()
