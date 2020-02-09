from flask import request, send_from_directory, jsonify

from ... import permissions, notifications
from ..model import thumbnails, search

from .schemas.query import search_query_params_schema

from .schemas.viewmodels import (
    search_results_schema,
    missing_thumbnails_schema
)

from . import bp


@bp.route('/search')
@search_query_params_schema
def search_endpoint():
    search_term_list = request.args.get('q').split(' ')
    media = search.run(search_term_list)
    return search_results_schema.dump(media)


@bp.route('/thumbnails/missing', methods=["GET"])
@permissions.is_owner
def get_missing_thumbnails():
    session = request.beevenue_context.session()
    missing = thumbnails.get_missing(session)

    return jsonify(missing_thumbnails_schema.dump(missing))


@bp.route('/thumbnail/<int:medium_id>', methods=["PATCH"])
@permissions.is_owner
def create_thumbnail(medium_id):
    status_code = thumbnails.create(medium_id)

    if status_code == 404:
        return notifications.no_such_medium(medium_id), 404

    return '', status_code


@bp.route('/thumbnails/after/<int:medium_id>', methods=["PATCH"])
@permissions.is_owner
def create_thumbnails(medium_id):
    thumbnails.create_all(medium_id)
    return '', 200


@bp.route('/thumbs/<path:full_path>')
@permissions.get_thumb
def get_thumb(full_path):
    res = send_from_directory('thumbs', full_path)
    res.headers["X-Accel-Redirect"] = f"/thumbs/{full_path}"
    return res


@bp.route('/files/<path:full_path>')
@permissions.get_medium_file
def get_file(full_path):
    res = send_from_directory('media', full_path)
    res.headers["X-Accel-Redirect"] = f"/media/{full_path}"
    return res
