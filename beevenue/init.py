from typing import Any, Optional

from flask import current_app, session
from flask_login import current_user

from .flask import BeevenueContext, BeevenueFlask, BeevenueResponse, request
from .spindex.spindex import CachingSessionFactory


def _context_setter() -> None:
    """Set request.beevenue_context from request context."""

    try:
        is_sfw = session["sfwSession"]
    except Exception:
        is_sfw = True

    role = None
    if hasattr(current_user, "role"):
        role = current_user.role

    request.beevenue_context = BeevenueContext(is_sfw=is_sfw, user_role=role)


def _login_required_by_default() -> Optional[Any]:
    """Make login required by default on all endpoints.

    Can be overridden through ``does_not_require_login``.
    """

    # * endpoint is None: Can happen when /foo/ is registered,
    #   but /foo is accessed.
    # * OPTIONS queries are sent-preflight to e.g. PATCH,
    #   and do not carry session info (so we can't auth them)
    if not request.endpoint or request.method == "OPTIONS":
        return None

    view_func = current_app.view_functions[request.endpoint]

    if hasattr(view_func, "is_public"):
        return None

    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()
    return None


def _set_client_hint_headers(res: BeevenueResponse) -> BeevenueResponse:
    """Set client hint headers for better performance."""

    client_hint_fields = ["Viewport-Width"]

    res.headers.setdefault("Accept-CH", ", ".join(client_hint_fields))
    res.headers.setdefault("Accept-CH-Lifetime", 86400)

    for hint in client_hint_fields:
        # res.vary is actually a werkzeug.datastructures.HeaderSet,
        # but mypy does not infer that correctly.
        res.vary.add(hint)  # type: ignore

    return res


def _set_server_push_link_header(res: BeevenueResponse) -> BeevenueResponse:
    """Set Link headers for better performance."""

    if not hasattr(res, "push_links") or not res.push_links:
        return res

    res.headers["Link"] = ", ".join(res.push_links)
    return res


def _set_sendfile_header(res: BeevenueResponse) -> BeevenueResponse:
    """Set X-Accel-Redirect headers for better performance."""

    if (
        not hasattr(res, "sendfile_header")
        or not res.sendfile_header
        or not current_app.use_x_sendfile
    ):
        return res

    res.headers["X-Accel-Redirect"] = res.sendfile_header
    return res


def _spindex_initialize() -> None:
    """Set request.spindex_session to caching implementation."""
    request.spindex_session = CachingSessionFactory()


def _spindex_teardown(res: BeevenueResponse) -> BeevenueResponse:
    """Flush cached spindex implementation if necessary."""
    if hasattr(request, "spindex_session"):
        request.spindex_session.exit()
    return res


def init_app(app: BeevenueFlask) -> None:
    """Register request/response lifecycle methods."""

    app.before_request(_context_setter)
    app.before_request(_login_required_by_default)
    app.before_request(_spindex_initialize)

    app.after_request(_set_client_hint_headers)  # type: ignore
    app.after_request(_set_server_push_link_header)  # type: ignore
    app.after_request(_set_sendfile_header)  # type: ignore
    app.after_request(_spindex_teardown)  # type: ignore
