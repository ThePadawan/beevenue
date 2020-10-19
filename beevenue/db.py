from typing import Any

from flask import appcontext_pushed, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.scoping import scoped_session
from werkzeug.local import LocalProxy

db = SQLAlchemy()


def init_app(app: Any) -> None:
    # Set g.db on the current (initialization) context because we (might)
    # need it for initializing the rest of the app...
    _set_db()

    # ...and set g.db for every future application context.
    # Note: This works for CLI usage and web requests (so it's better than
    # using before_request).
    appcontext_pushed.connect(_set_db)
    app.teardown_appcontext(_close_db_session)


def _set_db(*_: Any, **__: Any) -> None:
    g.db = LocalProxy(_session)


def _session() -> scoped_session:
    """Open a new session to the SQL database."""

    if "session" not in g:
        g.session = db.session
    return g.session


def _close_db_session(_: Any) -> None:
    """Discards last db session on appcontext destruction."""
    g.pop("session", None)
