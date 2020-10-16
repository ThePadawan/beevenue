from enum import Enum
import os
import re
from time import sleep
from typing import Literal, Optional, Tuple, TypedDict, Union

import magic
from werkzeug.datastructures import FileStorage

from beevenue.io import HelperBytesIO

from ... import db
from ...models import Medium
from ...spindex.signals import medium_added
from .extensions import EXTENSIONS
from .md5sum import md5sum
from .medium_update import update_rating, update_tags

Uploadable = Union[HelperBytesIO, FileStorage]

TAGGY_FILENAME_REGEX = re.compile(r"^\d+ - (?P<tags>.*)\.([a-zA-Z0-9]+)$")

RATING_TAG_REGEX = re.compile(r"rating:(?P<rating>u|q|s|e)")


def _maybe_add_tags(m: Medium, file: Uploadable) -> None:
    filename = file.filename
    if not filename:
        print("Filename not useful")
        return

    match = TAGGY_FILENAME_REGEX.match(filename)
    if not match:
        print("Filename not taggy:", filename)
        return

    joined_tags = match.group("tags").replace("_", ":")
    print(joined_tags)
    tags = joined_tags.split(" ")
    ratings = []
    for r in tags:
        match = RATING_TAG_REGEX.match(r)
        if match:
            ratings.append(
                (
                    r,
                    match,
                )
            )

    rating = None
    if ratings:
        rating = ratings[0][1].group("rating")
        for (r, match) in ratings:
            tags.remove(r)

    update_tags(m, tags)
    if rating:
        update_rating(m, rating)


class UploadFailureType(Enum):
    SUCCESS = 0
    CONFLICTING_MEDIUM = 1
    UNKNOWN_MIME_TYPE = 2


class ConflictingMediumResult(TypedDict):
    type: Literal[UploadFailureType.CONFLICTING_MEDIUM]
    medium_id: int


class UnknownMimeTypeResult(TypedDict):
    type: Literal[UploadFailureType.UNKNOWN_MIME_TYPE]
    mime_type: str


UploadFailure = Union[UnknownMimeTypeResult, ConflictingMediumResult]

UploadDetails = Tuple[str, str, str]


def can_upload(
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
    p = os.path.join("media", f"{basename}.{extension}")

    file.save(p)

    # TODO Try and replace me with os.fsync
    while not os.path.exists(p):
        sleep(1)


def create_medium_from_upload(
    file: Uploadable,
) -> Tuple[Optional[int], Optional[UploadFailure]]:
    details, failure = can_upload(file)

    if (not details) or failure:
        return None, failure

    mime_type, basename, extension = details

    session = db.session()
    m = Medium(mime_type=mime_type, hash=basename)
    session.add(m)

    upload_file(file, basename, extension)

    _maybe_add_tags(m, file)

    session.commit()
    medium_added.send(m.id)
    return m.id, None
