from ...spindex.signals import medium_updated
from ...models import Medium
from ... import db

from .file_upload import can_upload, upload_file
from . import thumbnails
from .media import delete_medium_files, EXTENSIONS


def replace_medium(medium_id, file):
    maybe_medium = Medium.query.get(medium_id)
    if not maybe_medium:
        return False, (f"Could not find medium with id {medium_id}.", None)

    success, details = can_upload(file)

    if not success:
        return success, details

    old_hash = maybe_medium.hash

    old_extension = EXTENSIONS[maybe_medium.mime_type]

    mime_type, basename, extension = details

    # Upload new file
    upload_file(file, basename, extension)

    session = db.session()

    # Update Medium entity with new values
    maybe_medium.mime_type = mime_type
    maybe_medium.hash = basename

    session.commit()

    # Update thumbs, tiny thumb, aspect_ratio
    thumbnails.create(medium_id)

    # Delete old file, thumbs
    delete_medium_files(old_hash, old_extension)

    medium_updated.send(medium_id)
    return True, None
