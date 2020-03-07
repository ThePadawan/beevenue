from io import BytesIO
import os
import re

from PIL import Image
from flask import current_app

from ... import db
from ...models import Medium
from .media import EXTENSIONS

from ...spindex.signals import medium_updated

from . import ffmpeg


def _thumbnailable_video(medium_id):
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


def generate_picks(medium_id, n):
    status_code, t = _thumbnailable_video(medium_id)

    if status_code != 200:
        return status_code, None

    origin_path, _ = t
    return 200, ffmpeg.generate_picks(n, origin_path)


def pick(medium_id, thumb_index, n):
    status_code, t = _thumbnailable_video(medium_id)

    if status_code != 200:
        return status_code

    origin_path, medium = t
    ffmpeg.pick(n, origin_path, thumb_index, medium.hash)
    _generate_tiny(medium_id, db.session())
    return 200


def create(medium_id):
    session = db.session()
    maybe_medium = session.query(Medium).filter_by(id=medium_id).first()

    if not maybe_medium:
        return 404

    maybe_aspect_ratio = _create(maybe_medium.mime_type, maybe_medium.hash)

    if not maybe_aspect_ratio:
        return 400

    maybe_medium.aspect_ratio = maybe_aspect_ratio
    session.commit()
    _generate_tiny(medium_id, session)
    return 200


def _create(mime_type, hash):
    thumb_path = os.path.abspath(f"thumbs/{hash}.jpg")
    if os.path.exists(thumb_path):
        os.remove(thumb_path)

    extension = EXTENSIONS[mime_type]

    origin_path = os.path.abspath(f"media/{hash}.{extension}")

    if not os.path.exists(origin_path):
        return False

    return ffmpeg.thumbnails(origin_path, thumb_path, mime_type)


def _generate_tiny(medium_id, session):
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
