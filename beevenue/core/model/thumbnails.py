import collections
import os
from pathlib import Path
import re
import subprocess
from math import ceil

from flask import current_app, request

import magic
from PIL import Image

from .media import EXTENSIONS
from ...models import Medium


class Ffmpeg(object):
    def _image_thumbnails(self, in_path, out_path_base):
        with Image.open(in_path) as img:
            width, height = img.size
            aspect_ratio = float(width) / height

            for thumbnail_size, thumbnail_size_pixels in current_app.config['BEEVENUE_THUMBNAIL_SIZES'].items():
                min_axis = thumbnail_size_pixels
                out_path = out_path_base.with_suffix(f'.{thumbnail_size}.jpg')
                print(f"Creating thumb with size {min_axis}, out_path = {out_path}")

                if width > height:
                    min_height = min_axis
                    min_width = int(ceil(aspect_ratio * min_height))
                else:
                    min_width = min_axis
                    min_height = int(ceil(min_width / aspect_ratio))

                thumbnail = img.copy()
                thumbnail.thumbnail((min_width, min_height))
                if thumbnail.mode != "RGB":
                    thumbnail = thumbnail.convert("RGB")
                try:
                    thumbnail.save(
                        out_path,
                        quality=80,
                        progressive=True,
                        optimize=True)
                except Exception:
                    background = Image.new("RGB", thumbnail.size, (255, 255, 255))
                    # 3 is the alpha channel
                    background.paste(thumbnail, mask=thumbnail.split()[3])
                    background.save(
                        out_path,
                        quality=80,
                        progressive=True,
                        optimize=True)

            thumb_width, thumb_height = thumbnail.size
            return float(thumb_width) / thumb_height

    def _video_thumbnails(self, in_path, out_path_base):
        for thumbnail_size, thumbnail_size_pixels in current_app.config['BEEVENUE_THUMBNAIL_SIZES'].items():
            min_axis = thumbnail_size_pixels
            out_path = out_path_base.with_suffix(f'.{thumbnail_size}.jpg')

            cmd = ["ffmpeg", "-y", f"-i", f"{in_path}", "-vf",
                f"thumbnail,scale={min_axis}:-1", "-frames:v", "1", f"{out_path}"]

            completed_process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE)
            print(completed_process.stdout)

        with Image.open(out_path) as img:
            width, height = img.size
            aspect_ratio = float(width) / height
            return aspect_ratio

    def thumbnails(self, in_path, out_path, mime_type):
        still_out_path = Path(out_path).with_suffix('')

        if re.match("image/", mime_type):
            return self._image_thumbnails(in_path, still_out_path)
        elif re.match("video/", mime_type):
            return self._video_thumbnails(in_path, still_out_path)


def create(medium_id):
    session = request.beevenue_context.session()
    maybe_medium = session.query(Medium).filter_by(id=medium_id).first()

    if not maybe_medium:
        return 404

    maybe_aspect_ratio = _create(maybe_medium.mime_type, maybe_medium.hash)

    if not maybe_aspect_ratio:
        return 400

    maybe_medium.aspect_ratio = maybe_aspect_ratio
    session.commit()
    return 200


def create_all(medium_id_threshold):
    session = request.beevenue_context.session()
    all_media = session.query(Medium)\
        .filter(Medium.id > medium_id_threshold).all()

    for maybe_medium in all_media:
        maybe_aspect_ratio = _create(
            maybe_medium.mime_type,
            maybe_medium.hash)

        if not maybe_aspect_ratio:
            continue

        maybe_medium.aspect_ratio = maybe_aspect_ratio

    session.commit()


def _create(mime_type, hash):
    thumb_path = os.path.abspath(f'thumbs/{hash}.jpg')
    if os.path.exists(thumb_path):
        os.remove(thumb_path)

    extension = EXTENSIONS[mime_type]

    origin_path = os.path.abspath(f'media/{hash}.{extension}')

    if not os.path.exists(origin_path):
        return False

    return Ffmpeg().thumbnails(origin_path, thumb_path, mime_type)


def _add_media_with_missing_media_files(all_media, result):
    found_hashes = set()

    if not os.path.exists('media'):
        os.mkdir('media')

    with os.scandir('media') as it:
        for entry in it:
            found_hash = Path(os.path.basename(entry)).with_suffix('')
            found_hashes.add(str(found_hash))

    missing_media = [m for m in all_media if m.hash not in found_hashes]

    for m in missing_media:
        result[m.id].append("Missing medium")


def _add_medium_with_missing_thumbnail(medium, thumbnail_size, result):
    out_path_base = os.path.abspath(f'thumbs/{medium.hash}.jpg')
    out_path = Path(out_path_base).with_suffix(f'.{thumbnail_size}.jpg')
    if not os.path.exists(out_path):
        result[medium.id].append(f"Missing thumbnail {thumbnail_size}")


def _add_media_with_missing_thumbnails(all_media, result):
    for medium in all_media:
        for thumbnail_size, _ in current_app.config['BEEVENUE_THUMBNAIL_SIZES'].items():
            _add_medium_with_missing_thumbnail(medium, thumbnail_size, result)


def get_missing(session):
    all_media = session.query(Medium).all()
    missing = collections.defaultdict(list)

    _add_media_with_missing_media_files(all_media, missing)
    _add_media_with_missing_thumbnails(all_media, missing)

    result = []

    for medium_id, reasons in missing.items():
        result.append({
            "mediumId": medium_id,
            "reasons": reasons
        })

    return result
