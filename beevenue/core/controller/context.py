from flask import session, request
from flask_login import current_user

from ...db import db


class BeevenueContext(object):
    def __init__(self, is_sfw, user_role):
        self.is_sfw = is_sfw
        self.user_role = user_role

    def session(self):
        return db.session

    def paginate(self, query):
        return query.paginate(
            int(request.args.get("pageNumber")),
            int(request.args.get("pageSize")))


def init_app(app):

    @app.before_request
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
