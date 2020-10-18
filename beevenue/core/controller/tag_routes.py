from flask import Blueprint

from beevenue import request

from ... import notifications, permissions
from ..model.tags import (
    aliases,
    implications,
    load,
    summary,
    update,
    similarity_chart,
    new,
    implications_chart,
)
from .schemas.query import add_tags_batch_schema, update_tag_schema


bp = Blueprint("tags", __name__)


@bp.route("/tag/<string:tag_name>", methods=["PATCH"])
@permissions.is_owner
@update_tag_schema
def patch_tag(tag_name: str):  # type: ignore
    body = request.json
    success, error_or_tag = update.update(tag_name, body)
    if not success:
        return error_or_tag, 400

    return error_or_tag


IMPLICATION_ROUTE_PATH = (
    "/tag/<string:tag_name>/implications/<string:implied_by_this>"
)


@bp.route(IMPLICATION_ROUTE_PATH, methods=["PATCH"])
@permissions.is_owner
def tag_add_implication(tag_name: str, implied_by_this: str):  # type: ignore
    error = implications.add_implication(
        implying=tag_name, implied=implied_by_this
    )

    if not error:
        return "", 200
    return notifications.simple_error(error), 400


@bp.route(IMPLICATION_ROUTE_PATH, methods=["DELETE"])
@permissions.is_owner
def tag_remove_implication(tag_name: str, implied_by_this: str):  # type: ignore
    error = implications.remove_implication(
        implying=tag_name, implied=implied_by_this
    )

    if not error:
        return "", 200
    return notifications.simple_error(error), 400


@bp.route("/tag/implications/backup")
@permissions.is_owner
def backup_implications():  # type: ignore
    all_implications = implications.get_all()
    return all_implications


@bp.route("/tags", methods=["GET"])
def get_tags_stats():  # type: ignore
    return summary.get_summary(request.beevenue_context)


@bp.route("/tags/batch", methods=["POST"])
@permissions.is_owner
@add_tags_batch_schema
def add_tags_batch():  # type: ignore
    added_count = new.add_batch(
        request.json["tags"],
        request.json["mediumIds"],
    )

    if added_count is None:
        return notifications.simple_warning("No tags added")

    return notifications.tag_batch_added(added_count), 200


@bp.route("/tags/similarity")
def get_tag_similarity():  # type: ignore
    matrix = similarity_chart.get_similarity_matrix()
    return matrix, 200


@bp.route("/tags/implications")
def get_tag_implications():  # type: ignore
    chart = implications_chart.get_all_implications()
    return chart, 200


@bp.route("/tag/<string:name>", methods=["GET", "OPTION"])
@permissions.is_owner
def get_tag(name: str):  # type: ignore
    maybe_tag = load.get(name)

    if not maybe_tag:
        return notifications.no_such_tag(name), 404

    return maybe_tag


@bp.route(
    "/tag/<string:current_name>/aliases/<string:new_alias>", methods=["POST"]
)
@permissions.is_owner
def add_alias(current_name: str, new_alias: str):  # type: ignore
    error = aliases.add_alias(current_name, new_alias)

    if not error:
        return "", 200
    return notifications.simple_error(error), 400


@bp.route("/tag/<string:name>/aliases/<string:alias>", methods=["DELETE"])
@permissions.is_owner
def delete_alias(name: str, alias: str):  # type: ignore
    aliases.remove_alias(name, alias)

    return "", 200
