from flask import g
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def session():
    if "session" not in g:
        g.session = db.session
    return g.session
