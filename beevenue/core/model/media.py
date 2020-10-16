from io import BytesIO
import json
import os
from typing import List, Optional, Tuple
import zipfile

from flask import current_app
from sqlalchemy.orm import load_only
from sqlalchemy.orm.scoping import scoped_session

from beevenue.context import BeevenueContext

from ... import db
from ...models import Medium
from ...spindex.signals import medium_deleted
from ...spindex.spindex import SPINDEX
from .detail import MediumDetail
from .extensions import EXTENSIONS
from .similar import similar_media


def _try_and_remove(f: str) -> None:
    try:
        os.remove(f)
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
    return [
        m.id
        for m in Medium.query.options(load_only(Medium.id))
        .order_by(Medium.id)
        .all()
    ]


def delete(medium_id: int) -> bool:
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
    hash = medium.hash
    extension = EXTENSIONS[medium.mime_type]
    session.delete(medium)
    session.commit()

    medium_deleted.send(medium.id)
    delete_medium_files(hash, extension)


def delete_medium_files(hash: str, extension: str) -> None:
    _try_and_remove(f"media/{hash}.{extension}")

    for thumbnail_size, _ in current_app.config[
        "BEEVENUE_THUMBNAIL_SIZES"
    ].items():
        _try_and_remove(f"thumbs/{hash}.{thumbnail_size}.jpg")


def get_zip(medium_id: int) -> Tuple[int, Optional[BytesIO]]:
    medium = Medium.query.filter_by(id=medium_id).first()

    if not medium:
        return 404, None

    result_bytes = BytesIO()
    with zipfile.ZipFile(result_bytes, mode="w") as z:
        # Add metadata
        metadata_bytes = _get_metadata_bytes(medium)
        z.writestr(f"{medium.id}.metadata.json", metadata_bytes)

        # Add data
        extension = EXTENSIONS[medium.mime_type]
        with current_app.open_resource(
            f"media/{medium.hash}.{extension}", "rb"
        ) as res:
            z.writestr(f"{medium.id}.{extension}", res.read())

    result_bytes.seek(0)
    return 200, result_bytes
