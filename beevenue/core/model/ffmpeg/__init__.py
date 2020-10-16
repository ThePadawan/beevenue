import os
from pathlib import Path
import re
from typing import List

from flask import current_app

from ..interface import ThumbnailingResult
from .image import image_thumbnails
from .temporary_thumbnails import temporary_thumbnails
from .video import video_thumbnails


def thumbnails(
    in_path: str, out_path: str, mime_type: str
) -> ThumbnailingResult:
    still_out_path = Path(out_path).with_suffix("")

    if re.match("image/", mime_type):
        return image_thumbnails(in_path, still_out_path)
    elif re.match("video/", mime_type):
        return video_thumbnails(in_path, still_out_path)

    raise Exception(f"Cannot create thumbnails for mime_type {mime_type}")


def _set_thumbnail(hash: str, thumbnail_size: str, filename: str) -> None:
    # thumbnail_size: "s" or "l" or ...
    thumb_path = os.path.abspath(f"thumbs/{hash}.jpg")
    if os.path.exists(thumb_path):
        os.remove(thumb_path)

    out_path = Path(thumb_path).with_suffix("")
    out_path = out_path.with_suffix(f".{thumbnail_size}.jpg")

    if os.path.exists(out_path):
        os.remove(out_path)

    with open(filename, "rb") as in_file:
        with open(out_path, "wb") as out_file:
            out_file.write(in_file.read())


def generate_picks(n: int, in_path: str) -> List[bytes]:
    all_thumbs_bytes = []

    with temporary_thumbnails(n, in_path, 120) as temporary_thumbs:
        for thumb_file_name in temporary_thumbs:
            with open(thumb_file_name, "rb") as thumb_file:
                these_bytes = thumb_file.read()
                all_thumbs_bytes.append(these_bytes)

    return all_thumbs_bytes


def pick(n: int, in_path: str, index: int, medium_hash: str) -> None:
    for thumbnail_size, thumbnail_size_pixels in current_app.config[
        "BEEVENUE_THUMBNAIL_SIZES"
    ].items():
        with temporary_thumbnails(
            n, in_path, thumbnail_size_pixels
        ) as temporary_thumbs:
            picked_thumb = list(temporary_thumbs)[index]
            _set_thumbnail(medium_hash, thumbnail_size, picked_thumb)
