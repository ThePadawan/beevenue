from flask import request, send_from_directory, jsonify
import flask_login

from ...models import Medium

from ..model.file_upload import upload_file
from ..model.medium_update import update_medium
from ..model.search import run_search
from ..model.similar import similar_media
from .. import blueprint
from ..model import (notifications, thumbnails, media, tags)

from . import permissions
from .decorators import (
    paginated, requires_query_params, requires_json_body, requires_permission
)

# TODO Split tags of into its own routes.py
from .schemas.query import (
    search_query_params_schema,
    update_tag_schema
)

from .schemas.viewmodels import (
    medium_schema, search_results_schema,
    tag_statistics_schema, tag_show_schema,
    missing_thumbnails_schema
)


def _paginate(query):
    return query.paginate(
        int(request.args.get("pageNumber")),
        int(request.args.get("pageSize")))


@blueprint.route('/search')
@flask_login.login_required
@requires_query_params(search_query_params_schema)
def search():
    search_terms = request.args.get('q').split(' ')
    medium_ids = run_search(request.beevenue_context, search_terms)

    if not medium_ids:
        return jsonify(search_results_schema.dump([]).data)

    media = Medium.query.\
        filter(Medium.id.in_(medium_ids)).\
        order_by(Medium.id.desc())

    media = _paginate(media)
    return jsonify(search_results_schema.dump(media).data)


@blueprint.route('/media/')
@flask_login.login_required
@paginated()
def list_media():
    query = Medium.query.order_by(Medium.id.desc())

    ctx = request.beevenue_context
    filters = []
    if ctx.is_sfw:
        filters.append(Medium.rating == 's')
    if ctx.user_role != 'admin':
        filters.append(Medium.rating != 'e')

    if filters:
        query = query.filter(*filters)

    media = _paginate(query)
    schema = search_results_schema.dump(media).data
    return jsonify(schema)


@blueprint.route('/thumbnails/missing', methods=["GET"])
@flask_login.login_required
@requires_permission(permissions.is_owner)
def get_missing_thumbnails():
    session = request.beevenue_context.session()
    missing = thumbnails.get_missing(session)

    return jsonify(missing_thumbnails_schema.dump(missing).data)


@blueprint.route('/thumbnail/<int:medium_id>', methods=["PATCH"])
@flask_login.login_required
@requires_permission(permissions.is_owner)
def create_thumbnail(medium_id):
    session = request.beevenue_context.session()
    maybe_medium = session.query(Medium).filter_by(id=medium_id).first()

    if not maybe_medium:
        return notifications.no_such_medium(medium_id), 404

    aspect_ratio = thumbnails.create(maybe_medium.mime_type, maybe_medium.hash)
    maybe_medium.aspect_ratio = aspect_ratio
    session.commit()

    return '', 200


@blueprint.route('/thumbnails/after/<int:medium_id>', methods=["PATCH"])
@flask_login.login_required
@requires_permission(permissions.is_owner)
def create_thumbnails(medium_id):
    session = request.beevenue_context.session()
    all_media = session.query(Medium).filter(Medium.id > medium_id).all()

    for maybe_medium in all_media:
        aspect_ratio = thumbnails.create(
            maybe_medium.mime_type,
            maybe_medium.hash)
        maybe_medium.aspect_ratio = aspect_ratio
        session.commit()

    return '', 200


@blueprint.route('/medium/<int:medium_id>', methods=["DELETE"])
@flask_login.login_required
@requires_permission(permissions.is_owner)
def delete_medium(medium_id):
    maybe_medium = Medium.query.filter_by(id=medium_id).first()

    if not maybe_medium:
        return notifications.no_such_medium(medium_id), 404

    # Delete "Medium" DB row. Note: SQLAlchemy
    # automatically removes MediaTags rows!
    session = request.beevenue_context.session()
    try:
        media.delete(session, maybe_medium)
    except FileNotFoundError:
        pass

    return '', 200


@blueprint.route('/medium/<int:medium_id>', methods=["GET", "OPTION"])
@flask_login.login_required
@requires_permission(permissions.get_medium)
def get_medium(medium_id):
    maybe_medium = Medium.query.filter_by(id=medium_id).first()

    if not maybe_medium:
        return notifications.no_such_medium(medium_id), 404

    ctx = request.beevenue_context

    if ctx.is_sfw and maybe_medium.rating != 's':
        return notifications.not_sfw(), 400

    similar = similar_media(ctx, maybe_medium)

    maybe_medium.similar = similar

    return medium_schema.jsonify(maybe_medium)


@blueprint.route('/tag/<string:name>', methods=["GET", "OPTION"])
@flask_login.login_required
@requires_permission(permissions.is_owner)
def get_tag(name):
    maybe_tag = tags.get(request.beevenue_context, name)

    if not maybe_tag:
        return notifications.no_such_tag(name), 404

    return jsonify(tag_show_schema.dump(maybe_tag).data)


@blueprint.route(
    '/tag/<string:current_name>/aliases/<string:new_alias>',
    methods=["POST"])
@flask_login.login_required
@requires_permission(permissions.is_owner)
def add_alias(current_name, new_alias):
    message, success = tags.add_alias(
        request.beevenue_context,
        current_name,
        new_alias)

    if success:
        return '', 200
    else:
        return notifications.simple_error(message), 400


@blueprint.route(
    '/tag/<string:name>/aliases/<string:alias>',
    methods=["DELETE"])
@flask_login.login_required
@requires_permission(permissions.is_owner)
def delete_alias(name, alias):
    message, success = tags.remove_alias(
        request.beevenue_context,
        name,
        alias)

    if success:
        return '', 200
    else:
        return notifications.simple_error(message), 400


@blueprint.route('/medium/<int:medium_id>', methods=["PATCH"])
@flask_login.login_required
@requires_permission(permissions.is_owner)
def update_medium_post(medium_id):
    body = request.json

    # TODO Think about default values vs. schema validation
    success = update_medium(
        request.beevenue_context,
        medium_id,
        body.get("rating", None),
        body.get("tags", None))

    if (success):
        return '', 200
    else:
        return notifications.could_not_update_medium(), 400


@blueprint.route('/medium', methods=["POST"])
@flask_login.login_required
@requires_permission(permissions.is_owner)
def form_upload_medium():
    if not request.files:
        return notifications.simple_error("You must supply a file"), 400

    stream = next(request.files.values())
    session = request.beevenue_context.session()
    success, result = upload_file(session, stream)

    if not success:
        return notifications.medium_already_exists(result), 400

    aspect_ratio = thumbnails.create(result.mime_type, result.hash)
    result.aspect_ratio = aspect_ratio
    session.commit()

    return notifications.medium_uploaded(result.id), 200


@blueprint.route('/tag/<string:tag_name>', methods=["PATCH"])
@flask_login.login_required
@requires_permission(permissions.is_owner)
@requires_json_body(update_tag_schema)
def update_tag(tag_name):
    body = request.json
    new_name = body.get("newName", None)

    session = request.beevenue_context
    message, success = tags.rename(
        session,
        old_name=tag_name,
        new_name=new_name)

    if success:
        return notifications.tag_renamed(), 200
    else:
        return notifications.simple_error(message), 404


@blueprint.route(
    '/tag/<string:tag_name>/implications/<string:implied_by_this>',
    methods=["PATCH"])
@flask_login.login_required
@requires_permission(permissions.is_owner)
def tag_add_implication(tag_name, implied_by_this):
    message, success = tags.add_implication(
        request.beevenue_context,
        implying=tag_name,
        implied=implied_by_this)

    if success:
        return '', 200
    else:
        return notifications.simple_error(message), 400


@blueprint.route(
    '/tag/<string:tag_name>/implications/<string:implied_by_this>',
    methods=["DELETE"])
@flask_login.login_required
@requires_permission(permissions.is_owner)
def tag_remove_implication(tag_name, implied_by_this):
    message, success = tags.remove_implication(
        request.beevenue_context,
        implying=tag_name,
        implied=implied_by_this)

    if success:
        return '', 200
    else:
        return notifications.simple_error(message), 400


@blueprint.route('/tags', methods=["GET"])
@flask_login.login_required
@requires_permission(permissions.is_owner)
def get_tags_stats():
    stats = tags.get_statistics(request.beevenue_context)
    return tag_statistics_schema.jsonify(stats)


@blueprint.route('/tags/orphans', methods=["DELETE"])
@flask_login.login_required
@requires_permission(permissions.is_owner)
def delete_orphan_tags():
    tags.delete_orphans(request.beevenue_context)
    return '', 200


@blueprint.route('/thumbs/<path:full_path>')
@flask_login.login_required
@requires_permission(permissions.get_thumb)
def get_thumb(full_path):
    return send_from_directory('thumbs', full_path)


@blueprint.route('/files/<path:full_path>')
@flask_login.login_required
@requires_permission(permissions.get_medium_file)
def get_file(full_path):
    return send_from_directory('media', full_path)
