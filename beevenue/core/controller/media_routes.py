from flask import request, send_file, render_template, make_response

from ... import notifications, permissions, schemas

from ..model.search import run
from ..model.file_upload import upload_file
from ..model.medium_update import update_medium
from ..model import thumbnails, media

from .schemas.viewmodels import medium_schema, search_results_schema
from . import bp


@bp.route("/media")
@schemas.paginated
def list_media():
    media = run([])
    return search_results_schema.dump(media)


@bp.route("/medium/<int:medium_id>", methods=["DELETE"])
@permissions.is_owner
def delete_medium(medium_id):
    success = media.delete(request.beevenue_context, medium_id)
    if success:
        return "", 200

    return notifications.no_such_medium(medium_id), 404


@bp.route("/medium/<int:medium_id>", methods=["GET", "OPTION"])
@permissions.get_medium
def get_medium(medium_id):
    status_code, maybe_medium = media.get(request.beevenue_context, medium_id)

    if status_code == 404:
        return notifications.no_such_medium(medium_id), 404

    if status_code == 400:
        return notifications.not_sfw(), 400

    return medium_schema.dump(maybe_medium)


@bp.route("/medium/<int:medium_id>", methods=["PATCH"])
@permissions.is_owner
def update_medium_post(medium_id):
    body = request.json

    success = update_medium(
        request.beevenue_context,
        medium_id,
        body.get("rating", None),
        body.get("tags", None),
    )

    if success:
        return "", 200
    else:
        return notifications.could_not_update_medium(), 400


@bp.route("/medium", methods=["POST"])
@permissions.is_owner
def form_upload_medium():
    if not request.files:
        return notifications.simple_error("You must supply a file"), 400

    stream = next(request.files.values())
    session = request.beevenue_context.session()
    success, result = upload_file(session, stream)

    if not success:
        return notifications.medium_already_exists(result), 400

    status = thumbnails.create(result.id)
    if status == 400:
        return "", 400

    return notifications.medium_uploaded(result.id), 200


@bp.route("/media/backup.sh")
@permissions.is_owner
def get_backup_sh():
    all_media_ids = media.get_all_ids()

    base_path = request.url_root
    session_cookie = request.cookies["session"]

    response = make_response(
        render_template(
            "backup.sh",
            medium_ids=all_media_ids,
            base_url=base_path,
            session_cookie=session_cookie,
        )
    )
    response.mimetype = "application/x-sh"
    return response


@bp.route("/medium/<int:medium_id>/backup")
@permissions.is_owner
def get_medium_zip(medium_id):
    status, b = media.get_zip(medium_id)

    if status == 404:
        return "", 404

    return send_file(
        b,
        mimetype="application/zip",
        as_attachment=True,
        attachment_filename=f"{medium_id}.zip",
    )
