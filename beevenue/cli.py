"""CLI operations for the application. Mainly used for testing."""

import os
from typing import Iterable

import click
from flask import g

from .core import thumbnails
from .core.file_upload import create_medium_from_upload
from .flask import BeevenueFlask
from .io import HelperBytesIO


class _Nop:
    """Spindex that does nothing.

    We can use this during CLI usage since we never care about reading
    from the Spindex, so we might as well not even write it."""

    def reindex_medium(self, medium_id: int) -> None:
        """Do nothing, intentionally."""

    def remove_id(self, medium_id: int) -> None:
        """Do nothing, intentionally."""

    def add(self, _: object) -> None:
        """Do nothing, intentionally."""


def init_cli(app: BeevenueFlask) -> None:
    """Initialize CLI component of the application."""

    @app.cli.command("import")
    @click.argument("file_paths", nargs=-1, type=click.Path(exists=True))
    def _import(file_paths: Iterable[str]) -> None:
        """Import all the specified files. Skip invalid files."""

        g.spindex = _Nop()

        for path in file_paths:
            print(f"Importing {path}...")
            with open(path, "rb") as current_file:
                file_bytes = current_file.read()
            stream = HelperBytesIO(file_bytes)
            stream.filename = os.path.basename(path)

            print("Uploading...")
            medium_id, failure = create_medium_from_upload(stream)
            if failure or not medium_id:
                print(f"Could not upload file {path}: {failure}")
                continue

            print("Creating thumbnails...")
            thumbnails.create(medium_id)
            print(f"Successfully imported {path} (Medium {medium_id})")
