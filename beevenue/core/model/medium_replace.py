from enum import Enum
from typing import Literal, Optional, TypedDict, Union

from werkzeug.datastructures import FileStorage

from . import thumbnails
from ... import db
from ...models import Medium
from ...spindex.signals import medium_updated
from .file_upload import can_upload, upload_file, UploadFailure
from .media import delete_medium_files, EXTENSIONS


class ReplacementFailureType(Enum):
    UNKNOWN_MEDIUM = 3


class UnknownMediumResult(TypedDict):
    type: Literal[ReplacementFailureType.UNKNOWN_MEDIUM]


ReplacementFailure = Union[UploadFailure, UnknownMediumResult]


def replace_medium(
    medium_id: int, file: FileStorage
) -> Optional[ReplacementFailure]:
    """Try to replace the medium with id ``medium_id`` with the specified file."""
    maybe_medium = Medium.query.get(medium_id)
    if not maybe_medium:
        return {"type": ReplacementFailureType.UNKNOWN_MEDIUM}

    details, failure = can_upload(file)

    if (not details) or failure:
        return failure

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
    return None
