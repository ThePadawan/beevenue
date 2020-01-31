from flask import Blueprint, request, send_from_directory, jsonify

from ...models import Medium

from ..model.search import run_search
from ..model import thumbnails

from ... import permissions, notifications
from ...decorators import (
    requires_query_params, requires_permission
)

from .schemas.query import (
    search_query_params_schema,
)

from .schemas.viewmodels import (
    search_results_schema,
    missing_thumbnails_schema
)

bp = Blueprint('core', __name__)

from . import tag_routes, media_routes


@bp.route('/search')
@requires_query_params(search_query_params_schema)
def search():
    search_terms = request.args.get('q').split(' ')
    medium_ids = run_search(request.beevenue_context, search_terms)

    if not medium_ids:
        return search_results_schema.dumps([])

    media = Medium.query.\
        filter(Medium.id.in_(medium_ids)).\
        order_by(Medium.id.desc())

    media = request.beevenue_context.paginate(media)
    return search_results_schema.dump(media)


@bp.route('/thumbnails/missing', methods=["GET"])
@requires_permission(permissions.is_owner)
def get_missing_thumbnails():
    session = request.beevenue_context.session()
    missing = thumbnails.get_missing(session)

    return jsonify(missing_thumbnails_schema.dump(missing))


@bp.route('/thumbnail/<int:medium_id>', methods=["PATCH"])
@requires_permission(permissions.is_owner)
def create_thumbnail(medium_id):
    session = request.beevenue_context.session()
    maybe_medium = session.query(Medium).filter_by(id=medium_id).first()

    if not maybe_medium:
        return notifications.no_such_medium(medium_id), 404

    maybe_aspect_ratio = thumbnails.create(
        maybe_medium.mime_type, maybe_medium.hash)

    if not maybe_aspect_ratio:
        return '', 400

    maybe_medium.aspect_ratio = maybe_aspect_ratio
    session.commit()

    return '', 200


@bp.route('/thumbnails/after/<int:medium_id>', methods=["PATCH"])
@requires_permission(permissions.is_owner)
def create_thumbnails(medium_id):
    session = request.beevenue_context.session()
    all_media = session.query(Medium).filter(Medium.id > medium_id).all()

    for maybe_medium in all_media:
        maybe_aspect_ratio = thumbnails.create(
            maybe_medium.mime_type,
            maybe_medium.hash)

        if not maybe_aspect_ratio:
            continue

        maybe_medium.aspect_ratio = maybe_aspect_ratio

    session.commit()

    return '', 200


@bp.route('/thumbs/<path:full_path>')
@requires_permission(permissions.get_thumb)
def get_thumb(full_path):
    return send_from_directory('thumbs', full_path)


@bp.route('/files/<path:full_path>')
@requires_permission(permissions.get_medium_file)
def get_file(full_path):
    return send_from_directory('media', full_path)
