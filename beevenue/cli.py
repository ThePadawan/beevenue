import click
import os
from io import BytesIO

from flask import g

from .core.model.file_upload import create_medium_from_upload, UploadResult
from .core.model import thumbnails


class HelperBytesIO(BytesIO):
    def save(self, p):
        """
        Helper to enable BytesIO to save itself to a path.
        """
        with open(p, "wb") as out_file:
            out_file.write(self.read())


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

            print("Uploading...")
            success, result = create_medium_from_upload(stream)
            if success != UploadResult.SUCCESS:
                print(f"Could not upload file {p}: {result}")
                continue

            print("Creating thumbnails...")
            thumbnails.create(result.id)
            print(f"Successfulyl imported {p}")
