from flask import session, request
from flask_login import current_user

from ...db import db

from .. import blueprint
from ...strawberry.routes import bp as strawberry_blueprint


class BeevenueContext(object):
    def __init__(self, is_sfw, user_role):
        self.is_sfw = is_sfw
        self.user_role = user_role

    def session(self):
        return db.session


@strawberry_blueprint.before_request
@blueprint.before_request
def context_setter():
    try:
        is_sfw = session["sfwSession"]
    except Exception:
        is_sfw = True

    role = None
    if hasattr(current_user, 'role'):
        role = current_user.role

    request.beevenue_context = BeevenueContext(
        is_sfw=is_sfw,
        user_role=role)
