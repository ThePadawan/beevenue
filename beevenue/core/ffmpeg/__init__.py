import os
from pathlib import Path
import re
from typing import List

from flask import current_app

from beevenue import paths
from ..interface import ThumbnailingResult
from .image import image_thumbnails
from .temporary_thumbnails import temporary_thumbnails
from .video import video_thumbnails


def thumbnails(
    in_path: str, extensionless_out_path: Path, mime_type: str
) -> ThumbnailingResult:
    """Generate and persist thumbnails of the file at ``in_path``."""

    if re.match("image/", mime_type):
        return image_thumbnails(in_path, extensionless_out_path)
    if re.match("video/", mime_type):
        return video_thumbnails(in_path, extensionless_out_path)

    raise Exception(f"Cannot create thumbnails for mime_type {mime_type}")


def _set_thumbnail(
    medium_hash: str, thumbnail_size: str, filename: str
) -> None:
    out_path = Path(paths.thumbnail_path(medium_hash, thumbnail_size))

    with open(filename, "rb") as in_file:
        with open(out_path, "wb") as out_file:
            out_file.write(in_file.read())


def generate_picks(thumbnail_count: int, in_path: str) -> List[bytes]:
    """Generate some preview-sized thumbnails in-memory.

    The files are returned as bytes in-memory and not permanently persisted.
    This is a bit wasteful, but involves less server-side state management."""

    all_thumbs_bytes = []

    with temporary_thumbnails(
        thumbnail_count, in_path, 120
    ) as temporary_thumbs:
        for thumb_file_name in temporary_thumbs:
            with open(thumb_file_name, "rb") as thumb_file:
                these_bytes = thumb_file.read()
                all_thumbs_bytes.append(these_bytes)

    return all_thumbs_bytes


def pick(
    thumbnail_count: int, in_path: str, index: int, medium_hash: str
) -> None:
    """Pick ``index`` out of ``thumbnail_count`` as the new thumbnail."""

    for thumbnail_size, thumbnail_size_pixels in current_app.config[
        "BEEVENUE_THUMBNAIL_SIZES"
    ].items():
        with temporary_thumbnails(
            thumbnail_count, in_path, thumbnail_size_pixels
        ) as temporary_thumbs:
            picked_thumb = list(temporary_thumbs)[index]
            _set_thumbnail(medium_hash, thumbnail_size, picked_thumb)
