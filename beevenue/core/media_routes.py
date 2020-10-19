from flask import make_response, render_template, send_file, Blueprint

from beevenue.flask import request

from .. import notifications, permissions, schemas
from . import media, thumbnails
from .file_upload import create_medium_from_upload, UploadFailureType
from .medium_replace import replace_medium
from .medium_update import update_medium
from .search.search import find_all

bp = Blueprint("media", __name__)


@bp.route("/media")
@schemas.paginated
def list_media():  # type: ignore
    return find_all()


@bp.route("/medium/<int:medium_id>", methods=["DELETE"])
@permissions.is_owner
def delete_medium(medium_id: int):  # type: ignore
    success = media.delete(medium_id)
    if success:
        return "", 200

    return notifications.no_such_medium(medium_id), 404


@bp.route("/medium/<int:medium_id>", methods=["GET", "OPTION"])
@permissions.get_medium
def get_medium(medium_id: int):  # type: ignore
    status_code, medium = media.get(request.beevenue_context, medium_id)

    if status_code == 404:
        return notifications.no_such_medium(medium_id), 404

    if status_code == 400:
        return notifications.not_sfw(), 400

    return medium


@bp.route("/medium/<int:medium_id>/metadata", methods=["PATCH"])
@permissions.is_owner
def update_medium_metadata(medium_id: int):  # type: ignore
    """Update some or all of the medium's metadata (e.g. rating).

    Note: This is *not* used to update the medium itself.
    See the /file endpoint for that.
    """
    body = request.json

    success = update_medium(
        medium_id,
        body.get("rating", None),
        body.get("tags", None),
    )

    if success:
        return success
    return notifications.could_not_update_medium(), 400


@bp.route("/medium", methods=["POST"])
@permissions.is_owner
def form_upload_medium():  # type: ignore
    if not request.files:
        return notifications.simple_error("You must supply a file"), 400

    stream = next(request.files.values())
    medium_id, failure = create_medium_from_upload(stream)

    if failure and failure["type"] == UploadFailureType.UNKNOWN_MIME_TYPE:
        return (
            notifications.unknown_mime_type(
                stream.filename, failure["mime_type"]
            ),
            400,
        )
    if failure and failure["type"] == UploadFailureType.CONFLICTING_MEDIUM:
        return (
            notifications.medium_already_exists(
                stream.filename, failure["medium_id"]
            ),
            400,
        )

    status, error = thumbnails.create(medium_id)
    if status == 400:
        return notifications.simple_error(error), 400

    return notifications.medium_uploaded(medium_id), 200


@bp.route("/medium/<int:medium_id>/file", methods=["PATCH"])
@permissions.is_owner
def replace_medium_file(medium_id: int):  # type: ignore
    """Replace medium's file. Use the /metadata route to replace e.g. rating."""

    if not request.files:
        return notifications.simple_error("You must supply a file"), 400

    stream = next(request.files.values())
    error = replace_medium(medium_id, stream)

    if not error:
        return get_medium(medium_id)

    if error["type"] == UploadFailureType.UNKNOWN_MIME_TYPE:
        return (
            notifications.unknown_mime_type(
                stream.filename, error["mime_type"]
            ),
            400,
        )
    if error["type"] == UploadFailureType.CONFLICTING_MEDIUM:
        return (
            notifications.medium_already_exists(
                stream.filename, error["medium_id"]
            ),
            400,
        )

    # error["type"] must now be "ReplacementFailureType.UNKNOWN_MEDIUM"
    return notifications.no_such_medium(medium_id), 400


@bp.route("/media/backup.sh")
@permissions.is_owner
def get_backup_sh():  # type: ignore
    all_media_ids = media.get_all_ids()

    base_path = request.url_root
    session_cookie = request.cookies["session"]

    response = make_response(
        render_template(
            "backup.sh.template",
            medium_ids=all_media_ids,
            base_url=base_path,
            session_cookie=session_cookie,
        )
    )
    response.mimetype = "application/x-sh"
    return response


@bp.route("/medium/<int:medium_id>/backup")
@permissions.is_owner
def get_medium_zip(medium_id: int):  # type: ignore
    status, zip_bytes = media.get_zip(medium_id)

    if status == 404:
        return "", 404

    return send_file(
        zip_bytes,
        mimetype="application/zip",
        as_attachment=True,
        attachment_filename=f"{medium_id}.zip",
    )
