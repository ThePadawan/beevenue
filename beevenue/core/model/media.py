from io import BytesIO
import json
import os
from typing import List, Optional, Tuple
import zipfile

from flask import current_app
from sqlalchemy.orm import load_only
from sqlalchemy.orm.scoping import scoped_session

from beevenue import BeevenueContext, EXTENSIONS, paths

from ... import db
from ...models import Medium
from ...spindex.signals import medium_deleted
from ...spindex.spindex import SPINDEX
from .detail import MediumDetail
from .similar import similar_media


def _try_and_remove(file: str) -> None:
    try:
        os.remove(file)
    except Exception:
        pass


def _get_metadata_bytes(medium: Medium) -> bytes:
    metadata = {"rating": medium.rating, "tags:": [t.tag for t in medium.tags]}
    metadata_text = json.dumps(metadata)
    return metadata_text.encode("utf-8")


def get(
    context: BeevenueContext, medium_id: int
) -> Tuple[int, Optional[MediumDetail]]:
    maybe_medium = SPINDEX.get_medium(medium_id)

    if not maybe_medium:
        return 404, None

    if context.is_sfw and maybe_medium.rating != "s":
        return 400, None

    detail = MediumDetail(maybe_medium, similar_media(context, maybe_medium))
    return 200, detail


def get_all_ids() -> List[int]:
    """Get ids of *all* media."""

    return [
        m.id
        for m in Medium.query.options(load_only(Medium.id))
        .order_by(Medium.id)
        .all()
    ]


def delete(medium_id: int) -> bool:
    """Delete medium. Return True on success, False otherwise."""

    maybe_medium = Medium.query.filter_by(id=medium_id).first()

    if not maybe_medium:
        return False

    # Delete "Medium" DB row. Note: SQLAlchemy
    # automatically removes MediaTags rows!
    session = db.session()
    try:
        _delete(session, maybe_medium)
    except FileNotFoundError:
        pass

    return True


def _delete(session: scoped_session, medium: Medium) -> None:
    current_hash = medium.hash
    extension = EXTENSIONS[medium.mime_type]
    session.delete(medium)
    session.commit()

    medium_deleted.send(medium.id)
    delete_medium_files(current_hash, extension)


def delete_medium_files(medium_hash: str, extension: str) -> None:
    """Ensure medium files and thumbnails are deleted, ignoring failure."""

    _try_and_remove(paths.medium_path(f"{medium_hash}.{extension}"))

    for thumbnail_size in current_app.config["BEEVENUE_THUMBNAIL_SIZES"].keys():
        path = paths.thumbnail_path(medium_hash, thumbnail_size)
        _try_and_remove(path)


def get_zip(medium_id: int) -> Tuple[int, Optional[BytesIO]]:
    """Get zip file containing file and metadata for specific medium."""

    medium = Medium.query.filter_by(id=medium_id).first()

    if not medium:
        return 404, None

    result_bytes = BytesIO()
    with zipfile.ZipFile(result_bytes, mode="w") as zip_file:
        # Add metadata
        metadata_bytes = _get_metadata_bytes(medium)
        zip_file.writestr(f"{medium.id}.metadata.json", metadata_bytes)

        # Add data
        extension = EXTENSIONS[medium.mime_type]
        with current_app.open_resource(
            paths.medium_path(f"{medium.hash}.{extension}"), "rb"
        ) as res:
            zip_file.writestr(f"{medium.id}.{extension}", res.read())

    result_bytes.seek(0)
    return 200, result_bytes
