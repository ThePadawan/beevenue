from contextlib import AbstractContextManager
import os
from math import ceil
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory
from datetime import timedelta

from flask import current_app

from PIL import Image


class _PickableThumbsContextManager(AbstractContextManager):
    def __init__(self, inner):
        self.inner = inner

    def __iter__(self):
        for thumb_file_name in os.listdir(self.inner.name):
            yield Path(self.inner.name, thumb_file_name)

    def __exit__(self, *args, **kwargs):
        self.inner.__exit__(*args, **kwargs)


def _get_length_in_seconds(in_path):
    cmd = [
        "ffmpeg",
        "-i",
        f"{in_path}",
        "-map",
        "0:v:0",
        "-c",
        "copy",
        "-f",
        "null",
        "-",
    ]

    completed_process = subprocess.run(cmd, text=True, stderr=subprocess.PIPE)

    td = _get_timedelta(completed_process.stderr)
    seconds = ceil(td.total_seconds())
    return seconds


def _get_timedelta(ffmpeg_stderr):
    # line_regex = re.compile(r".* time=(.*?) ")
    line_regex = re.compile(
        r".* time=(?P<hours>..):(?P<minutes>..):(?P<seconds>..).(?P<centiseconds>..) "
    )

    for line in ffmpeg_stderr.splitlines():
        m = line_regex.match(line)
        if not m:
            continue

        td = timedelta(
            hours=int(m.group("hours")),
            minutes=int(m.group("minutes")),
            seconds=int(m.group("seconds")),
            milliseconds=10 * int(m.group("centiseconds")),
        )
        return td


def _image_thumbnails(in_path, out_path_base):
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
        return float(thumb_width) / thumb_height


def _video_thumbnails(in_path, out_path_base):
    for thumbnail_size, thumbnail_size_pixels in current_app.config[
        "BEEVENUE_THUMBNAIL_SIZES"
    ].items():
        min_axis = thumbnail_size_pixels
        out_path = out_path_base.with_suffix(f".{thumbnail_size}.jpg")

        cmd = [
            "ffmpeg",
            "-y",
            f"-i",
            f"{in_path}",
            "-vf",
            f"thumbnail,scale={min_axis}:-1",
            "-frames:v",
            "1",
            f"{out_path}",
        ]

        subprocess.run(cmd, stdout=subprocess.PIPE)

    with Image.open(out_path) as img:
        width, height = img.size
        aspect_ratio = float(width) / height
        return aspect_ratio


def thumbnails(in_path, out_path, mime_type):
    still_out_path = Path(out_path).with_suffix("")

    if re.match("image/", mime_type):
        return _image_thumbnails(in_path, still_out_path)
    elif re.match("video/", mime_type):
        return _video_thumbnails(in_path, still_out_path)


def _temporary_thumbs(n, in_path, scale):
    length_in_seconds = _get_length_in_seconds(in_path)

    temp_dir = TemporaryDirectory()
    out_pattern = Path(temp_dir.name, "out_%03d.jpg")

    cmd = [
        "ffmpeg",
        "-i",
        f"{in_path}",
        "-vf",
        f"fps={(n-1)}/{length_in_seconds},scale={scale}:-1",
        f"{out_pattern}",
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return _PickableThumbsContextManager(temp_dir)


def _set_thumbnail(hash, thumbnail_size, filename):
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


def generate_picks(n, in_path):
    all_thumbs_bytes = []

    with _temporary_thumbs(n, in_path, 120) as temporary_thumbs:
        for thumb_file_name in temporary_thumbs:
            with open(thumb_file_name, "rb") as thumb_file:
                these_bytes = thumb_file.read()
                all_thumbs_bytes.append(these_bytes)

    return all_thumbs_bytes


def pick(n, in_path, index, medium_hash):
    for thumbnail_size, thumbnail_size_pixels in current_app.config[
        "BEEVENUE_THUMBNAIL_SIZES"
    ].items():
        with _temporary_thumbs(
            n, in_path, thumbnail_size_pixels
        ) as temporary_thumbs:
            picked_thumb = list(temporary_thumbs)[index]
            _set_thumbnail(medium_hash, thumbnail_size, picked_thumb)
