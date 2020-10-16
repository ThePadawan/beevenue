import os
from typing import Iterable

import click
from flask import g

from .core.model import thumbnails
from .core.model.file_upload import create_medium_from_upload, UploadFailure
from .flask import BeevenueFlask
from .io import HelperBytesIO


class Nop(object):
    def remove_id(self, id: int) -> None:
        """Do nothing, intentionally."""

    def add(self, x: object) -> None:
        """Do nothing, intentionally."""


class NopSpindex(object):
    def __call__(self, do_write: bool) -> Nop:
        return Nop()


def init_cli(app: BeevenueFlask) -> None:
    @app.cli.command("import")
    @click.argument("file_paths", nargs=-1, type=click.Path(exists=True))
    def _import(file_paths: Iterable[str]) -> None:
        g.spindex = NopSpindex()

        for p in file_paths:
            print(f"Importing {p}...")
            with open(p, "rb") as f:
                file_bytes = f.read()
            stream = HelperBytesIO(file_bytes)
            stream.filename = os.path.basename(p)

            print("Uploading...")
            medium_id, failure = create_medium_from_upload(stream)
            if failure or not medium_id:
                print(f"Could not upload file {p}: {failure}")
                continue

            print("Creating thumbnails...")
            thumbnails.create(medium_id)
            print(f"Successfully imported {p}")
