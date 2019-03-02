import os
from pathlib import Path
import re
import subprocess
from math import ceil

from flask import current_app

import magic
from PIL import Image

from .media import EXTENSIONS

KNOWN_MIME_TYPES = [
    'image/gif',
    'image/jpeg',
    'image/png',
    'video/mp4',
    'video/webm'
]


def _is_file_thumbnailable(path):
    mime_type = magic.from_file(path, mime=True)
    print(f"MIME Type: {mime_type}")
    return mime_type in KNOWN_MIME_TYPES


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


def create(mime_type, hash):
    thumb_path = os.path.abspath(f'thumbs/{hash}.jpg')
    if os.path.exists(thumb_path):
        print("Thumb exists")
        os.remove(thumb_path)

    extension = EXTENSIONS[mime_type]

    origin_path = os.path.abspath(f'media/{hash}.{extension}')
    return Ffmpeg().thumbnails(origin_path, thumb_path, mime_type)
