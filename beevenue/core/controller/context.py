from flask import session, request, current_app, g
from flask_login import current_user

from ...cache import cache


class BeevenueContext(object):
    def __init__(self, is_sfw, user_role):
        self.is_sfw = is_sfw
        self.user_role = user_role


def context_setter():
    try:
        is_sfw = session["sfwSession"]
    except Exception:
        is_sfw = True

    role = None
    if hasattr(current_user, "role"):
        role = current_user.role

    request.beevenue_context = BeevenueContext(is_sfw=is_sfw, user_role=role)


def login_required_by_default():
    # * endpoint is None: Can happen when /foo/ is registered,
    #   but /foo is accessed.
    # * OPTIONS queries are sent-preflight to e.g. PATCH,
    #   and do not carry session info (so we can't auth them)
    if not request.endpoint or request.method == "OPTIONS":
        return

    view_func = current_app.view_functions[request.endpoint]

    if hasattr(view_func, "is_public"):
        return

    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()


def set_client_hint_headers(res):
    client_hint_fields = ["Viewport-Width"]

    res.headers.setdefault("Accept-CH", ", ".join(client_hint_fields))
    res.headers.setdefault("Accept-CH-Lifetime", 86400)

    for x in client_hint_fields:
        res.vary.add(x)

    return res


def set_server_push_link_header(res):
    if not hasattr(res, "push_links") or not res.push_links:
        return res

    res.headers["Link"] = ", ".join(res.push_links)
    return res


def set_sendfile_header(res):
    if (
        not hasattr(res, "sendfile_header")
        or not res.sendfile_header
        or not current_app.use_x_sendfile
    ):
        return res

    res.headers["X-Accel-Redirect"] = res.sendfile_header
    return res


class MemoizedSpindex(object):
    def __init__(self):
        self.spindex = None
        self.do_write = False

    def __call__(self, do_write):
        self.do_write |= do_write
        if self.spindex is None:
            self.spindex = cache.get("MEDIA")
        return self.spindex

    def exit(self):
        if self.do_write:
            cache.set("MEDIA", self.spindex)


def spindex_memoize():
    request.spindex = MemoizedSpindex()


def spindex_unmemoize(res):
    if hasattr(request, "spindex"):
        request.spindex.exit()
    return res


def init_app(app):
    app.before_request(context_setter)
    app.before_request(login_required_by_default)
    app.before_request(spindex_memoize)

    app.after_request(set_client_hint_headers)
    app.after_request(set_server_push_link_header)
    app.after_request(set_sendfile_header)
    app.after_request(spindex_unmemoize)

    @app.teardown_appcontext
    def teardown_session(x):
        g.pop("session", None)
