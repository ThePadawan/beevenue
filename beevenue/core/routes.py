from base64 import b64encode
from pathlib import Path

from flask import Blueprint, g, send_from_directory

from beevenue import paths
from beevenue.flask import request, BeevenueResponse

from .. import notifications, permissions
from . import thumbnails
from .search import search
from .schemas import search_query_params_schema

bp = Blueprint("routes", __name__)


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


@bp.route(
    "/medium/<int:medium_id>/thumbnail/picks/<int:thumbnail_count>",
    methods=["GET"],
)
@permissions.is_owner
def show_thumbnail_picks(medium_id: int, thumbnail_count: int):  # type: ignore
    status_code, list_of_bytes = thumbnails.generate_picks(
        medium_id, thumbnail_count
    )

    if status_code != 200 or (list_of_bytes is None):
        return "", status_code

    # Idea: We could also use a zip file.
    base64_strings = []

    for byte in list_of_bytes:
        base64_strings.append(b64encode(byte).decode("utf-8"))

    return {"thumbs": base64_strings}


@bp.route(
    "/medium/<int:medium_id>/thumbnail/pick/"
    "<int:thumb_index>/<int:thumbnail_count>",
    methods=["PATCH"],
)
@permissions.is_owner
def pick_thumbnail(  # type: ignore
    medium_id: int, thumb_index: int, thumbnail_count: int
):
    status_code = thumbnails.pick(medium_id, thumb_index, thumbnail_count)

    return notifications.new_thumbnail(), status_code


@bp.route("/thumbs/<int:medium_id>")
@permissions.get_medium
def get_magic_thumb(medium_id: int):  # type: ignore
    medium = g.spindex.get_medium(medium_id)
    if not medium:
        return "", 404

    size = "s"

    if (
        "Viewport-Width" in request.headers
        and int(request.headers["Viewport-Width"]) > 1200
    ):
        size = "l"

    thumb_path = Path(f"{medium.medium_hash}.{size}.jpg")

    res: BeevenueResponse = send_from_directory(  # type: ignore
        paths.thumbnail_directory(), thumb_path
    )
    # Note this must be distinct from the public route ("/thumbs"),
    # or Nginx will freak.
    res.set_sendfile_header(Path("/", "beevenue_thumbs", thumb_path))

    return res


@bp.route("/files/<path:full_path>")
@permissions.get_medium_file
def get_file(full_path: str):  # type: ignore
    res: BeevenueResponse = send_from_directory(  # type: ignore
        paths.medium_directory(), full_path
    )
    # Note this must be distinct from the public route ("/files"),
    # or Nginx will freak.
    res.set_sendfile_header(Path("/", "media", full_path))
    return res
