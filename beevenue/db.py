from flask import g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.scoping import scoped_session

db = SQLAlchemy()


def session() -> scoped_session:
    if "session" not in g:
        g.session = db.session
    return g.session
