import bcrypt

from flask import current_app, jsonify, session, request
from flask_login import current_user, login_user, logout_user
from flask_principal import identity_changed, Identity, AnonymousIdentity

from ..decorators import does_not_require_login

from . import blueprint
from .logged_in_user import LoggedInUser
from .models import User
from .schemas import login_params_schema, sfw_mode_schema


# "Am I logged in"? This simply reads the session cookie and replies true/false
@blueprint.route("/login", methods=["GET"])
@does_not_require_login
def get_login_state():
    if current_user.is_anonymous:
        return jsonify(False)

    result = {
        "id": current_user.id,
        "role": current_user.role,
        "version": current_app.config["COMMIT_ID"],
        "sfwSession": session.get("sfwSession", True),
    }
    return result


@blueprint.route("/logout", methods=["POST"])
def logout():
    logout_user()

    for key in ("identity.id", "identity.auth_type", "identity.role"):
        session.pop(key, None)

    identity_changed.send(
        current_app._get_current_object(), identity=AnonymousIdentity()
    )

    return "", 200


@blueprint.route("/login", methods=["POST"])
@login_params_schema
@does_not_require_login
def login():
    username = request.json["username"]
    password = request.json["password"]

    maybe_user = User.query.filter(User.username == username).first()
    if not maybe_user:
        return "", 401

    is_authed = bcrypt.checkpw(
        password.encode("utf-8"), maybe_user.hash.encode("utf-8")
    )
    if not is_authed:
        return "", 401

    if "sfwSession" not in session:
        session["sfwSession"] = True

    user = LoggedInUser(id=username, role=maybe_user.role)
    login_user(user)

    identity_changed.send(
        current_app._get_current_object(), identity=Identity(user.id)
    )

    return (
        {
            "id": username,
            "role": maybe_user.role,
            "version": current_app.config["COMMIT_ID"],
            "sfwSession": session["sfwSession"],
        },
        200,
    )


@blueprint.route("/sfw", methods=["PATCH"])
@sfw_mode_schema
def set_sfw_mode():
    session["sfwSession"] = bool(request.json["sfwSession"])
    session.modified = True
    return "", 200
