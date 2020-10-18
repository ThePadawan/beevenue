from enum import Enum
import re
from typing import Literal, Optional, Tuple, TypedDict, Union

import magic
from werkzeug.datastructures import FileStorage

from beevenue import EXTENSIONS, paths
from beevenue.io import HelperBytesIO

from ... import db
from ...models import Medium
from ...spindex.signals import medium_added
from .md5sum import md5sum
from .medium_update import update_rating, update_tags

Uploadable = Union[HelperBytesIO, FileStorage]

TAGGY_FILENAME_REGEX = re.compile(r"^\d+ - (?P<tags>.*)\.([a-zA-Z0-9]+)$")

RATING_TAG_REGEX = re.compile(r"rating:(?P<rating>u|q|s|e)")


def _maybe_add_tags(medium: Medium, file: Uploadable) -> None:
    filename = file.filename
    if not filename:
        print("Filename not useful")
        return

    match = TAGGY_FILENAME_REGEX.match(filename)
    if not match:
        print("Filename not taggy:", filename)
        return

    joined_tags = match.group("tags").replace("_", ":")
    tags = joined_tags.split(" ")
    ratings = []
    for chunk in tags:
        match = RATING_TAG_REGEX.match(chunk)
        if match:
            ratings.append(
                (
                    chunk,
                    match,
                )
            )

    rating = None
    if ratings:
        rating = ratings[0][1].group("rating")
        for (chunk, match) in ratings:
            tags.remove(chunk)

    update_tags(medium, tags)
    if rating:
        update_rating(medium, rating)


class UploadFailureType(Enum):
    """Reason enum why the upload could not be performed.

    When extending this, keep its values non-overlapping with
    ReplacementFailureType!"""

    SUCCESS = 0
    CONFLICTING_MEDIUM = 1
    UNKNOWN_MIME_TYPE = 2


class _ConflictingMediumResult(TypedDict):
    type: Literal[UploadFailureType.CONFLICTING_MEDIUM]
    medium_id: int


class _UnknownMimeTypeResult(TypedDict):
    type: Literal[UploadFailureType.UNKNOWN_MIME_TYPE]
    mime_type: str


UploadFailure = Union[_UnknownMimeTypeResult, _ConflictingMediumResult]

UploadDetails = Tuple[str, str, str]


def upload_precheck(
    file: Uploadable,
) -> Tuple[Optional[UploadDetails], Optional[UploadFailure]]:
    basename = md5sum(file)

    conflicting_medium = Medium.query.filter(Medium.hash == basename).first()
    if conflicting_medium:
        return (
            None,
            {
                "type": UploadFailureType.CONFLICTING_MEDIUM,
                "medium_id": conflicting_medium.id,
            },
        )

    file.seek(0)

    mime_type: str = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)
    extension = EXTENSIONS.get(mime_type)

    if not extension:
        return (
            None,
            {
                "type": UploadFailureType.UNKNOWN_MIME_TYPE,
                "mime_type": mime_type,
            },
        )

    return (mime_type, basename, extension), None


def upload_file(file: Uploadable, basename: str, extension: str) -> None:
    path = paths.medium_path(f"{basename}.{extension}")
    file.save(path)


def create_medium_from_upload(
    file: Uploadable,
) -> Tuple[Optional[int], Optional[UploadFailure]]:
    details, failure = upload_precheck(file)

    if (not details) or failure:
        return None, failure

    mime_type, basename, extension = details

    session = db.session()
    medium = Medium(mime_type=mime_type, medium_hash=basename)
    session.add(medium)

    upload_file(file, basename, extension)

    _maybe_add_tags(medium, file)

    session.commit()
    medium_added.send(medium.id)
    return medium.id, None
