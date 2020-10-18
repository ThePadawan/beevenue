import os

from flask import current_app


def _base_dir() -> str:
    return current_app.config.get("BEEVENUE_STORAGE", "./")


def thumbnail_directory() -> str:
    return os.path.join(_base_dir(), "thumbs")


def thumbnail_path(medium_hash: str, size: str) -> str:
    return os.path.join(_base_dir(), "thumbs", f"{medium_hash}.{size}.jpg")


def medium_directory() -> str:
    return os.path.join(_base_dir(), "media")


def medium_path(filename: str) -> str:
    return os.path.join(_base_dir(), "media", filename)
