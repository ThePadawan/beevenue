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
    """Disposable handle on a list of temporary thumbnails.

    Allows iteration over the contained files as Paths.
    On exiting this context, the contained temporary directory is disposed."""

    def __init__(self, inner: TemporaryDirectory):
        self.inner = inner

    def __iter__(self) -> Generator[Path, None, None]:
        for thumb_file_name in os.listdir(self.inner.name):
            yield Path(self.inner.name, thumb_file_name)

    def __exit__(self, exc: Any, value: Any, tb: Any) -> None:
        self.inner.__exit__(exc, value, tb)


def _get_length_in_seconds(in_path: str) -> int:
    """Determine the length in seconds (rounded up) of the specified file."""

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
        cmd, encoding="utf-8", stderr=subprocess.PIPE, check=False
    )

    delta = _get_timedelta(completed_process.stderr)
    seconds = ceil(delta.total_seconds())
    return seconds


def _get_timedelta(ffmpeg_stderr: str) -> timedelta:
    """Try to parse ffmpeg output of video length into a timedelta.

    Raises on error."""

    line_regex = re.compile(
        r".* time=(?P<hours>..):(?P<minutes>..)"
        r":(?P<seconds>..).(?P<centiseconds>..) "
    )

    for line in ffmpeg_stderr.splitlines():
        match = line_regex.match(line)
        if not match:
            continue

        delta = timedelta(
            hours=int(match.group("hours")),
            minutes=int(match.group("minutes")),
            seconds=int(match.group("seconds")),
            milliseconds=10 * int(match.group("centiseconds")),
        )
        return delta

    raise Exception("Could not determine length of video")


def temporary_thumbnails(
    thumbnail_count: int, in_path: str, scale: int
) -> _PickableThumbsContextManager:
    """Generate some thumbnails and return a disposable handle to them."""

    length_in_seconds = _get_length_in_seconds(in_path)

    temp_dir = TemporaryDirectory()
    out_pattern = Path(temp_dir.name, "out_%03d.jpg")

    cmd = [
        "ffmpeg",
        "-i",
        f"{in_path}",
        "-vf",
        f"fps={(thumbnail_count-1)}/{length_in_seconds},scale={scale}:-1",
        f"{out_pattern}",
    ]

    subprocess.run(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False
    )

    return _PickableThumbsContextManager(temp_dir)
