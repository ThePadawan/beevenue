from .reindex import setup_signals
from .load import full_load
from .spindex import SPINDEX


def init_app(app, session):
    SPINDEX.add_media(full_load(session))
    setup_signals()
