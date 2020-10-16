from math import ceil
from pathlib import Path

from PIL import Image
from flask import current_app

from ..interface import ThumbnailingResult


def _constrain_aspect_ratio(img: Image) -> Image:
    min_aspect_ratio = current_app.config["BEEVENUE_MINIMUM_ASPECT_RATIO"]
    aspect_ratio = img.width / img.height

    if aspect_ratio < min_aspect_ratio:
        maximum_height = round((1 / min_aspect_ratio) * img.width)
        img = img.crop((0, 0, img.width, maximum_height))

    return img


def image_thumbnails(in_path: str, out_path_base: Path) -> ThumbnailingResult:
    with Image.open(in_path) as img:
        width, height = img.size
        aspect_ratio = float(width) / height

        for thumbnail_size, thumbnail_size_pixels in current_app.config[
            "BEEVENUE_THUMBNAIL_SIZES"
        ].items():
            min_axis = thumbnail_size_pixels
            out_path = out_path_base.with_suffix(f".{thumbnail_size}.jpg")

            if width > height:
                min_height = min_axis
                min_width = int(ceil(aspect_ratio * min_height))
            else:
                min_width = min_axis
                min_height = int(ceil(min_width / aspect_ratio))

            thumbnail = img.copy()
            thumbnail.thumbnail((min_width, min_height))

            thumbnail = _constrain_aspect_ratio(thumbnail)

            if thumbnail.mode != "RGB":
                thumbnail = thumbnail.convert("RGB")
            try:
                thumbnail.save(
                    out_path, quality=80, progressive=True, optimize=True
                )
            except Exception:
                background = Image.new("RGB", thumbnail.size, (255, 255, 255))
                # 3 is the alpha channel
                background.paste(thumbnail, mask=thumbnail.split()[3])
                background.save(
                    out_path, quality=80, progressive=True, optimize=True
                )

        thumb_width, thumb_height = thumbnail.size
        aspect_ratio = float(thumb_width) / thumb_height
        return ThumbnailingResult.from_success(aspect_ratio)
