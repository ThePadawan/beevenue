from pathlib import Path
import subprocess

from PIL import Image
from flask import current_app

from ..interface import ThumbnailingResult


def video_thumbnails(in_path: str, out_path_base: Path) -> ThumbnailingResult:
    for thumbnail_size, thumbnail_size_pixels in current_app.config[
        "BEEVENUE_THUMBNAIL_SIZES"
    ].items():
        min_axis = thumbnail_size_pixels
        out_path = out_path_base.with_suffix(f".{thumbnail_size}.jpg")

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            f"{in_path}",
            "-vf",
            f"thumbnail,scale={min_axis}:-1",
            "-frames:v",
            "1",
            f"{out_path}",
        ]

        ffmpeg_result = subprocess.run(cmd)

        if ffmpeg_result.returncode != 0:
            return ThumbnailingResult.from_failure(
                "Could not create thumbnail for video."
            )

    with Image.open(out_path) as img:
        width, height = img.size
        aspect_ratio = float(width) / height
        return ThumbnailingResult.from_success(aspect_ratio)
