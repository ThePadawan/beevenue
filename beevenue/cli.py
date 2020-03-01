import click
import os

from flask import g

from .db import db
from .sushi.routes import HelperBytesIO
from .core.model.file_upload import upload_file
from .core.model import thumbnails


class Nop(object):
    def remove_id(self, id):
        pass

    def add(self, x):
        pass


class NopSpindex(object):
    def __call__(self, do_write):
        return Nop()


def init_cli(app):
    @app.cli.command("import")
    @click.argument("file_paths", nargs=-1, type=click.Path(exists=True))
    def _import(file_paths):
        g.spindex = NopSpindex()

        for p in file_paths:
            print(f"Importing {p}...")
            with open(p, "rb") as f:
                file_bytes = f.read()
            stream = HelperBytesIO(file_bytes)
            stream.filename = os.path.basename(p)

            print(f"Uploading...")
            success, result = upload_file(stream)
            if not success:
                print(f"Could not upload file {p}: {result}")
                continue

            print(f"Creating thumbnails...")
            thumbnails.create(result.id)
            print(f"Successfulyl imported {p}")
