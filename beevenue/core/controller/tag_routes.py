from flask import request
from ... import notifications, permissions
from ..model import tags
from ..model.tags import implications, aliases, statistics
from .schemas.query import update_tag_schema, add_tags_batch_schema
from . import bp


@bp.route("/tag/<string:tag_name>", methods=["PATCH"])
@permissions.is_owner
@update_tag_schema
def patch_tag(tag_name):
    body = request.json
    success, error_or_tag = tags.update(tag_name, body)
    if not success:
        return error_or_tag, 400

    return error_or_tag


IMPLICATION_ROUTE_PATH = (
    "/tag/<string:tag_name>/implications/<string:implied_by_this>"
)


@bp.route(IMPLICATION_ROUTE_PATH, methods=["PATCH"])
@permissions.is_owner
def tag_add_implication(tag_name, implied_by_this):
    message, success = implications.add_implication(
        implying=tag_name, implied=implied_by_this
    )

    if success:
        return "", 200
    else:
        return notifications.simple_error(message), 400


@bp.route(IMPLICATION_ROUTE_PATH, methods=["DELETE"])
@permissions.is_owner
def tag_remove_implication(tag_name, implied_by_this):
    message, success = implications.remove_implication(
        implying=tag_name, implied=implied_by_this
    )

    if success:
        return "", 200
    else:
        return notifications.simple_error(message), 400


@bp.route("/tag/implications/backup")
@permissions.is_owner
def backup_implications():
    all_implications = implications.get_all()
    return all_implications


@bp.route("/tags", methods=["GET"])
def get_tags_stats():
    return statistics.get_statistics(request.beevenue_context)


@bp.route("/tags/batch", methods=["POST"])
@permissions.is_owner
@add_tags_batch_schema
def add_tags_batch():
    result = tags.add_batch(request.json["tags"], request.json["mediumIds"],)

    if not result:
        return notifications.simple_warning("No tags added")

    tag_count, added_count = result
    return notifications.tag_batch_added(tag_count, added_count), 200


@bp.route("/tags/similarity")
def get_tag_similarity():
    matrix = tags.get_similarity_matrix()
    return matrix, 200


@bp.route("/tags/implications")
def get_tag_implications():
    implications = tags.get_all_implications()
    return implications, 200


@bp.route("/tag/<string:name>", methods=["GET", "OPTION"])
@permissions.is_owner
def get_tag(name):
    maybe_tag = tags.get(name)

    if not maybe_tag:
        return notifications.no_such_tag(name), 404

    return maybe_tag


@bp.route(
    "/tag/<string:current_name>/aliases/<string:new_alias>", methods=["POST"]
)
@permissions.is_owner
def add_alias(current_name, new_alias):
    message, success = aliases.add_alias(current_name, new_alias)

    if success:
        return "", 200
    else:
        return notifications.simple_error(message), 400


@bp.route("/tag/<string:name>/aliases/<string:alias>", methods=["DELETE"])
@permissions.is_owner
def delete_alias(name, alias):
    aliases.remove_alias(name, alias)

    return "", 200
