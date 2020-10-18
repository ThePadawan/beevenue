from io import BytesIO
import os
import re
from typing import List, Optional, Tuple
from pathlib import Path

from PIL import Image
from flask import current_app
from sqlalchemy.orm.scoping import scoped_session

from beevenue import EXTENSIONS, paths
from . import ffmpeg
from ... import db
from ...models import Medium
from ...spindex.signals import medium_updated
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
    origin_path = paths.medium_path(f"{medium.hash}.{extension}")
    return 200, (origin_path, medium)


def generate_picks(
    medium_id: int, thumbnail_count: int
) -> Tuple[int, Optional[List[bytes]]]:
    status_code, details = _thumbnailable_video(medium_id)

    if status_code != 200 or (details is None):
        return status_code, None

    origin_path, _ = details
    return 200, ffmpeg.generate_picks(thumbnail_count, origin_path)


def pick(medium_id: int, thumb_index: int, thumbnail_count: int) -> int:
    status_code, details = _thumbnailable_video(medium_id)

    if status_code != 200 or (details is None):
        return status_code

    origin_path, medium = details
    ffmpeg.pick(thumbnail_count, origin_path, thumb_index, medium.hash)
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


def _create(mime_type: str, medium_hash: str) -> ThumbnailingResult:
    extensionless_thumb_path = Path(
        os.path.join(paths.thumbnail_directory(), medium_hash)
    )

    extension = EXTENSIONS[mime_type]

    origin_path = paths.medium_path((f"{medium_hash}.{extension}"))
    return ffmpeg.thumbnails(origin_path, extensionless_thumb_path, mime_type)


def _generate_tiny(medium_id: int, session: scoped_session) -> None:
    size, _ = list(current_app.config["BEEVENUE_THUMBNAIL_SIZES"].items())[0]
    tiny_thumb_res = current_app.config["BEEVENUE_TINY_THUMBNAIL_SIZE"]

    medium = Medium.query.get(medium_id)
    out_path = paths.thumbnail_path(medium_hash=medium.hash, size=size)

    with Image.open(out_path, "r") as img:
        thumbnail = img.copy()
        thumbnail.thumbnail((tiny_thumb_res, tiny_thumb_res))

        with BytesIO() as out_bytes_io:
            thumbnail.save(
                out_bytes_io, format="JPEG", optimize=True, quality=75
            )
            out_bytes = out_bytes_io.getvalue()

    medium.tiny_thumbnail = out_bytes
    medium_updated.send(medium.id)
    session.commit()
