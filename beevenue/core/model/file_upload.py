from enum import Enum
import os
import re
from time import sleep

import magic

from ... import db
from ...spindex.signals import medium_added
from ...models import Medium

from .md5sum import md5sum
from .media import EXTENSIONS
from .medium_update import update_tags, update_rating

TAGGY_FILENAME_REGEX = re.compile(r"^\d+ - (?P<tags>.*)\.([a-zA-Z0-9]+)$")

RATING_TAG_REGEX = re.compile(r"rating:(?P<rating>u|q|s|e)")


def _maybe_add_tags(m, file):
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


class UploadResult(Enum):
    SUCCESS = 0
    CONFLICTING_MEDIUM = 1
    UNKNOWN_MIME_TYPE = 2


def can_upload(file):
    basename = md5sum(file)

    conflicting_medium = Medium.query.filter(Medium.hash == basename).first()
    if conflicting_medium:
        return False, (UploadResult.CONFLICTING_MEDIUM, conflicting_medium.id)

    file.seek(0)

    mime_type = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)
    extension = EXTENSIONS.get(mime_type)

    if not extension:
        return False, (UploadResult.UNKNOWN_MIME_TYPE, mime_type)

    return True, (mime_type, basename, extension)


def upload_file(file, basename, extension):
    p = os.path.join("media", f"{basename}.{extension}")

    file.save(p)

    while not os.path.exists(p):
        sleep(1)


def create_medium_from_upload(file):
    success, details = can_upload(file)

    if not success:
        return details

    mime_type, basename, extension = details

    session = db.session()
    m = Medium(mime_type=mime_type, hash=basename)
    session.add(m)

    upload_file(file, basename, extension)

    _maybe_add_tags(m, file)

    session.commit()
    medium_added.send(m.id)
    return UploadResult.SUCCESS, m
