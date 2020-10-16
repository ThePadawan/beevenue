from contextlib import AbstractContextManager
from datetime import timedelta
from math import ceil
import os
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory
from typing import Any, Generator


class _PickableThumbsContextManager(AbstractContextManager):
    def __init__(self, inner: TemporaryDirectory):
        self.inner = inner

    def __iter__(self) -> Generator[Path, None, None]:
        for thumb_file_name in os.listdir(self.inner.name):
            yield Path(self.inner.name, thumb_file_name)

    def __exit__(self, exc: Any, value: Any, tb: Any) -> None:
        self.inner.__exit__(exc, value, tb)


def _get_length_in_seconds(in_path: str) -> int:
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

    completed_process = subprocess.run(
        cmd, encoding="utf-8", stderr=subprocess.PIPE
    )

    td = _get_timedelta(completed_process.stderr)
    seconds = ceil(td.total_seconds())
    return seconds


def _get_timedelta(ffmpeg_stderr: str) -> timedelta:
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

    raise Exception("Could not determine length of video")


def temporary_thumbnails(
    n: int, in_path: str, scale: int
) -> _PickableThumbsContextManager:
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
