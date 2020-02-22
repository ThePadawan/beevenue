import collections
from io import BytesIO
import os
import re
from pathlib import Path

from PIL import Image
from flask import current_app, request

from ...models import Medium
from .media import EXTENSIONS

from ...spindex.signals import medium_updated

from . import ffmpeg


def _thumbnailable_video(medium_id):
    session = request.beevenue_context.session()
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
        return status_code, None

    origin_path, medium = t
    ffmpeg.pick(n, origin_path, thumb_index, medium.hash)
    generate_tiny(medium_id)
    return 200


def create(medium_id):
    session = request.beevenue_context.session()
    maybe_medium = session.query(Medium).filter_by(id=medium_id).first()

    if not maybe_medium:
        return 404

    maybe_aspect_ratio = _create(maybe_medium.mime_type, maybe_medium.hash)

    if not maybe_aspect_ratio:
        return 400

    maybe_medium.aspect_ratio = maybe_aspect_ratio
    generate_tiny(medium_id)
    session.commit()
    return 200


def create_all(medium_id_threshold):
    session = request.beevenue_context.session()
    all_media = (
        session.query(Medium).filter(Medium.id > medium_id_threshold).all()
    )

    for maybe_medium in all_media:
        maybe_aspect_ratio = _create(maybe_medium.mime_type, maybe_medium.hash)

        if not maybe_aspect_ratio:
            continue

        maybe_medium.aspect_ratio = maybe_aspect_ratio

    session.commit()


def _create(mime_type, hash):
    thumb_path = os.path.abspath(f"thumbs/{hash}.jpg")
    if os.path.exists(thumb_path):
        os.remove(thumb_path)

    extension = EXTENSIONS[mime_type]

    origin_path = os.path.abspath(f"media/{hash}.{extension}")

    if not os.path.exists(origin_path):
        return False

    return ffmpeg.thumbnails(origin_path, thumb_path, mime_type)


def _add_media_with_missing_media_files(all_media, result):
    found_hashes = set()

    if not os.path.exists("media"):
        os.mkdir("media")

    with os.scandir("media") as it:
        for entry in it:
            found_hash = Path(os.path.basename(entry)).with_suffix("")
            found_hashes.add(str(found_hash))

    missing_media = [m for m in all_media if m.hash not in found_hashes]

    for m in missing_media:
        result[m.id].append("Missing medium")


def _add_medium_with_missing_thumbnail(medium, thumbnail_size, result):
    out_path_base = os.path.abspath(f"thumbs/{medium.hash}.jpg")
    out_path = Path(out_path_base).with_suffix(f".{thumbnail_size}.jpg")
    if not os.path.exists(out_path):
        result[medium.id].append(f"Missing thumbnail {thumbnail_size}")


def _add_media_with_missing_thumbnails(all_media, result):
    for medium in all_media:
        for thumbnail_size, _ in current_app.config[
            "BEEVENUE_THUMBNAIL_SIZES"
        ].items():
            _add_medium_with_missing_thumbnail(medium, thumbnail_size, result)


def get_missing(session):
    all_media = session.query(Medium).all()
    missing = collections.defaultdict(list)

    _add_media_with_missing_media_files(all_media, missing)
    _add_media_with_missing_thumbnails(all_media, missing)

    result = []

    for medium_id, reasons in missing.items():
        result.append({"mediumId": medium_id, "reasons": reasons})

    return result


def generate_tiny(medium_id):
    _generate_tiny(lambda: [Medium.query.get(medium_id)])


def generate_all_tiny():
    _generate_tiny(lambda: Medium.query.all())


def _generate_tiny(get_media):
    size, _ = list(current_app.config["BEEVENUE_THUMBNAIL_SIZES"].items())[0]
    tiny_thumb_res = current_app.config["BEEVENUE_TINY_THUMBNAIL_SIZE"]

    for m in get_media():
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

    request.beevenue_context.session().commit()
