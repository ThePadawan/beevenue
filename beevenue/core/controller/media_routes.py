from flask import request, jsonify, send_file, render_template, make_response
import flask_login

from ...models import Medium

from ..model.file_upload import upload_file
from ..model.medium_update import update_medium
from ..model.similar import similar_media
from .. import blueprint
from ..model import (thumbnails, media)
from ... import notifications, permissions

from ...decorators import (
    paginated, requires_permission
)

from .schemas.viewmodels import medium_schema, search_results_schema


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

    media = ctx.paginate(query)
    schema = search_results_schema.dump(media).data
    return jsonify(schema)


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


@blueprint.route('/medium/<int:medium_id>', methods=["PATCH"])
@flask_login.login_required
@requires_permission(permissions.is_owner)
def update_medium_post(medium_id):
    body = request.json

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

    maybe_aspect_ratio = thumbnails.create(result.mime_type, result.hash)
    if not maybe_aspect_ratio:
        return '', 400

    result.aspect_ratio = maybe_aspect_ratio
    session.commit()

    return notifications.medium_uploaded(result.id), 200


@blueprint.route('/media/backup.sh')
@flask_login.login_required
@requires_permission(permissions.is_owner)
def get_backup_sh():
    all_media_ids = [m.id for m in Medium.query.order_by(Medium.id).all()]

    base_path = request.url_root
    session_cookie = request.cookies['session']

    response = make_response(render_template(
        'backup.sh',
        medium_ids=all_media_ids,
        base_url=base_path,
        session_cookie=session_cookie))
    response.mimetype = "application/x-sh"
    return response


@blueprint.route('/medium/<int:medium_id>/backup')
@flask_login.login_required
@requires_permission(permissions.is_owner)
def get_medium_zip(medium_id):
    maybe_medium = Medium.query.filter_by(id=medium_id).first()

    if not maybe_medium:
        return '', 404

    session = request.beevenue_context.session()

    b = media.get_zip(session, maybe_medium)
    return send_file(
        b,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename=f'{medium_id}.zip')
