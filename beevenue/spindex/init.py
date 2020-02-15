from flask_caching import Cache
from .reindex import setup_signals
from .load import full_load
from .spindex import SPINDEX

from ..cache import cache


def init_app(app, session):
    cache.init_app(app)
    SPINDEX.add_media(full_load(session))
    setup_signals()
