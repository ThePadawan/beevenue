from flask import request
from ... import notifications, permissions
from ..model import tags
from ..model.tags import implications, aliases

from .schemas.query import update_tag_schema, add_tags_batch_schema

from .schemas.viewmodels import (
    tag_statistics_schema,
    tag_show_schema,
)

from . import bp


# TODO: Obsolete this
#         return notifications.tag_renamed(), 200


@bp.route("/tag/<string:tag_name>", methods=["PATCH"])
@permissions.is_owner
@update_tag_schema
def patch_tag(tag_name):
    body = request.json
    success, error_or_tag = tags.update(tag_name, body)
    if not success:
        return error_or_tag, 400

    return tag_show_schema.dump(error_or_tag), 200


@bp.route(
    "/tag/<string:tag_name>/implications/<string:implied_by_this>",
    methods=["PATCH"],
)
@permissions.is_owner
def tag_add_implication(tag_name, implied_by_this):
    message, success = implications.add_implication(
        request.beevenue_context, implying=tag_name, implied=implied_by_this
    )

    if success:
        return "", 200
    else:
        return notifications.simple_error(message), 400


@bp.route(
    "/tag/<string:tag_name>/implications/<string:implied_by_this>",
    methods=["DELETE"],
)
@permissions.is_owner
def tag_remove_implication(tag_name, implied_by_this):
    message, success = implications.remove_implication(
        request.beevenue_context, implying=tag_name, implied=implied_by_this
    )

    if success:
        return "", 200
    else:
        return notifications.simple_error(message), 400


@bp.route("/tag/implications/backup")
@permissions.is_owner
def backup_implications():
    all_implications = implications.get_all(request.beevenue_context)
    return all_implications


@bp.route("/tags", methods=["GET"])
@permissions.is_owner
def get_tags_stats():
    stats = tags.get_statistics(request.beevenue_context)
    return tag_statistics_schema.jsonify(stats)


@bp.route("/tags/batch", methods=["POST"])
@permissions.is_owner
@add_tags_batch_schema
def add_tags_batch():
    result = tags.add_batch(
        request.beevenue_context,
        request.json["tags"],
        request.json["mediumIds"],
    )

    if not result:
        return notifications.simple_warning("No tags added")

    tag_count, added_count = result
    return notifications.tag_batch_added(tag_count, added_count), 200


@bp.route("/tags/orphans", methods=["DELETE"])
@permissions.is_owner
def delete_orphan_tags():
    tags.delete_orphans(request.beevenue_context)
    return "", 200


@bp.route("/tags/similarity")
@permissions.is_owner
def get_tag_similarity():
    matrix = tags.get_similarity_matrix(request.beevenue_context)
    return matrix, 200


@bp.route("/tags/implications")
@permissions.is_owner
def get_tag_implications():
    implications = tags.get_all_implications(request.beevenue_context)
    return implications, 200


@bp.route("/tag/<string:name>", methods=["GET", "OPTION"])
@permissions.is_owner
def get_tag(name):
    maybe_tag = tags.get(request.beevenue_context, name)

    if not maybe_tag:
        return notifications.no_such_tag(name), 404

    return tag_show_schema.dump(maybe_tag)


@bp.route(
    "/tag/<string:current_name>/aliases/<string:new_alias>", methods=["POST"]
)
@permissions.is_owner
def add_alias(current_name, new_alias):
    message, success = aliases.add_alias(
        request.beevenue_context, current_name, new_alias
    )

    if success:
        return "", 200
    else:
        return notifications.simple_error(message), 400


@bp.route("/tag/<string:name>/aliases/<string:alias>", methods=["DELETE"])
@permissions.is_owner
def delete_alias(name, alias):
    aliases.remove_alias(request.beevenue_context, name, alias)

    return "", 200
