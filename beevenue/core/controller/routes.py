from pathlib import Path
from flask import request, send_from_directory

from ... import permissions, notifications
from ..model import thumbnails, search
from ...spindex.spindex import SPINDEX

from .schemas.query import search_query_params_schema

from . import bp


@bp.route("/search")
@search_query_params_schema
def search_endpoint():
    search_term_list = request.args.get("q").split(" ")
    return search.run(search_term_list)


@bp.route("/thumbnail/<int:medium_id>", methods=["PATCH"])
@permissions.is_owner
def create_thumbnail(medium_id):
    status_code = thumbnails.create(medium_id)

    if status_code == 404:
        return notifications.no_such_medium(medium_id), 404

    return "", status_code


@bp.route("/medium/<int:medium_id>/thumbnail/picks/<int:n>", methods=["GET"])
@permissions.is_owner
def show_thumbnail_picks(medium_id, n):
    status_code, list_of_bytes = thumbnails.generate_picks(medium_id, n)

    if status_code != 200:
        return "", status_code

    # Idea: We could also use a zip file.
    base64_strings = []
    from base64 import b64encode

    for b in list_of_bytes:
        base64_strings.append(b64encode(b).decode("utf-8"))

    return {"thumbs": base64_strings}


@bp.route(
    "/medium/<int:medium_id>/thumbnail/pick/<int:thumb_index>/<int:n>",
    methods=["PATCH"],
)
@permissions.is_owner
def pick_thumbnail(medium_id, thumb_index, n):
    status_code = thumbnails.pick(medium_id, thumb_index, n)

    return notifications.new_thumbnail(), status_code


@bp.route("/thumbs/<int:medium_id>")
@permissions.get_medium
def get_magic_thumb(medium_id):
    medium = SPINDEX.get_medium(medium_id)
    if not medium:
        return "", 404

    size = "s"

    if (
        "Viewport-Width" in request.headers
        and int(request.headers["Viewport-Width"]) > 1200
    ):
        size = "l"

    thumb_path = Path(f"{medium.hash}.{size}.jpg")

    res = send_from_directory("thumbs", thumb_path)
    # Note this must be distinct from the public route ("/thumbs"),
    # or Nginx will freak.
    res.set_sendfile_header(Path("/", "beevenue_thumbs", thumb_path))

    return res


@bp.route("/thumbs/gentiny", methods=["POST"])
@permissions.is_owner
def gen_tiny():
    thumbnails.generate_all_tiny()
    return "", 200


@bp.route("/files/<path:full_path>")
@permissions.get_medium_file
def get_file(full_path):
    res = send_from_directory("media", full_path)
    # Note this must be distinct from the public route ("/files"),
    # or Nginx will freak.
    res.set_sendfile_header(Path("/", "media", full_path))
    return res
