from io import BytesIO
import os
import re
from typing import List, Optional, Tuple

from PIL import Image
from flask import current_app
from sqlalchemy.orm.scoping import scoped_session

from . import ffmpeg
from ... import db
from ...models import Medium
from ...spindex.signals import medium_updated
from .extensions import EXTENSIONS
from .interface import ThumbnailingResult


def _thumbnailable_video(
    medium_id: int,
) -> Tuple[int, Optional[Tuple[str, Medium]]]:
    session = db.session()
    medium = session.query(Medium).filter_by(id=medium_id).first()

    if not medium:
        return 404, None

    if not re.match("video/", medium.mime_type):
        return 400, None

    extension = EXTENSIONS[medium.mime_type]
    origin_path = os.path.abspath(f"media/{medium.hash}.{extension}")

    if not os.path.exists(origin_path):
        return 404, None

    return 200, (origin_path, medium)


def generate_picks(medium_id: int, n: int) -> Tuple[int, Optional[List[bytes]]]:
    status_code, t = _thumbnailable_video(medium_id)

    if status_code != 200 or (t is None):
        return status_code, None

    origin_path, _ = t
    return 200, ffmpeg.generate_picks(n, origin_path)


def pick(medium_id: int, thumb_index: int, n: int) -> int:
    status_code, t = _thumbnailable_video(medium_id)

    if status_code != 200 or (t is None):
        return status_code

    origin_path, medium = t
    ffmpeg.pick(n, origin_path, thumb_index, medium.hash)
    _generate_tiny(medium_id, db.session())
    return 200


def create(medium_id: int) -> Tuple[int, str]:
    session = db.session()
    maybe_medium = session.query(Medium).filter_by(id=medium_id).first()

    if not maybe_medium:
        return 404, ""

    thumbnailing_result = _create(maybe_medium.mime_type, maybe_medium.hash)

    if thumbnailing_result.error:
        return 400, thumbnailing_result.error

    maybe_medium.aspect_ratio = thumbnailing_result.aspect_ratio
    session.commit()
    _generate_tiny(medium_id, session)
    return 200, ""


def _create(mime_type: str, hash: str) -> ThumbnailingResult:
    thumb_path = os.path.abspath(f"thumbs/{hash}.jpg")
    if os.path.exists(thumb_path):
        os.remove(thumb_path)

    extension = EXTENSIONS[mime_type]

    origin_path = os.path.abspath(f"media/{hash}.{extension}")

    if not os.path.exists(origin_path):
        raise Exception(
            "Could not create thumbnail because medium file does not exist."
        )

    return ffmpeg.thumbnails(origin_path, thumb_path, mime_type)


def _generate_tiny(medium_id: int, session: scoped_session) -> None:
    size, _ = list(current_app.config["BEEVENUE_THUMBNAIL_SIZES"].items())[0]
    tiny_thumb_res = current_app.config["BEEVENUE_TINY_THUMBNAIL_SIZE"]

    m = Medium.query.get(medium_id)
    out_path = os.path.abspath(f"thumbs/{m.hash}.{size}.jpg")

    with Image.open(out_path, "r") as img:
        thumbnail = img.copy()
        thumbnail.thumbnail((tiny_thumb_res, tiny_thumb_res))

        with BytesIO() as out_bytes_io:
            thumbnail.save(
                out_bytes_io, format="JPEG", optimize=True, quality=75
            )
            out_bytes = out_bytes_io.getvalue()

    m.tiny_thumbnail = out_bytes
    medium_updated.send(m.id)
    session.commit()
