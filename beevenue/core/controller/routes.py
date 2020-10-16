from base64 import b64encode
from pathlib import Path

from flask import send_from_directory

from beevenue.request import request
from beevenue.response import BeevenueResponse

from . import bp
from ... import notifications, permissions
from ...spindex.spindex import SPINDEX
from ..model import thumbnails
from ..model.search import search
from .schemas.query import search_query_params_schema


@bp.route("/search")
@search_query_params_schema
def search_endpoint():  # type: ignore
    search_term_list = request.args.get("q").split(" ")
    return search.run(search_term_list)


@bp.route("/thumbnail/<int:medium_id>", methods=["PATCH"])
@permissions.is_owner
def create_thumbnail(medium_id: int):  # type: ignore
    status_code, message = thumbnails.create(medium_id)

    if status_code == 404:
        return notifications.no_such_medium(medium_id), 404

    return message, status_code


@bp.route("/medium/<int:medium_id>/thumbnail/picks/<int:n>", methods=["GET"])
@permissions.is_owner
def show_thumbnail_picks(medium_id: int, n: int):  # type: ignore
    status_code, list_of_bytes = thumbnails.generate_picks(medium_id, n)

    if status_code != 200 or (list_of_bytes is None):
        return "", status_code

    # Idea: We could also use a zip file.
    base64_strings = []

    for b in list_of_bytes:
        base64_strings.append(b64encode(b).decode("utf-8"))

    return {"thumbs": base64_strings}


@bp.route(
    "/medium/<int:medium_id>/thumbnail/pick/<int:thumb_index>/<int:n>",
    methods=["PATCH"],
)
@permissions.is_owner
def pick_thumbnail(medium_id: int, thumb_index: int, n: int):  # type: ignore
    status_code = thumbnails.pick(medium_id, thumb_index, n)

    return notifications.new_thumbnail(), status_code


@bp.route("/thumbs/<int:medium_id>")
@permissions.get_medium
def get_magic_thumb(medium_id: int):  # type: ignore
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

    res: BeevenueResponse = send_from_directory("thumbs", thumb_path)  # type: ignore
    # Note this must be distinct from the public route ("/thumbs"),
    # or Nginx will freak.
    res.set_sendfile_header(Path("/", "beevenue_thumbs", thumb_path))

    return res


@bp.route("/files/<path:full_path>")
@permissions.get_medium_file
def get_file(full_path: str):  # type: ignore
    res: BeevenueResponse = send_from_directory("media", full_path)  # type: ignore
    # Note this must be distinct from the public route ("/files"),
    # or Nginx will freak.
    res.set_sendfile_header(Path("/", "media", full_path))
    return res
