import io
import json
import os
import zipfile

from flask import current_app
from sqlalchemy.orm import load_only

from ...models import Medium
from ...spindex.spindex import SPINDEX
from ...spindex.signals import medium_deleted

from .similar import similar_media

EXTENSIONS = {
    'video/mp4': 'mp4',
    'video/webm': 'webm',
    'image/png': 'png',
    'image/gif': 'gif',
    'image/jpeg': 'jpg',
    'image/jpg': 'jpg',
    'application/x-shockwave-flash': "swf"
}


def _try_and_remove(f):
    try:
        os.remove(f)
    except Exception:
        pass


def _get_metadata_bytes(medium):
    metadata = {
        'rating': medium.rating,
        'tags:': [t.tag for t in medium.tags]
    }
    metadata_text = json.dumps(metadata)
    return metadata_text.encode('utf-8')


def get(context, medium_id):
    maybe_medium = SPINDEX.get_medium(medium_id)

    if not maybe_medium:
        return 404, None

    if context.is_sfw and maybe_medium.rating != 's':
        return 400, None

    maybe_medium.similar = similar_media(context, medium_id)
    return 200, maybe_medium


def get_all_ids():
    return [
        m.id for m in
        Medium.query.options(load_only(Medium.id)).order_by(Medium.id).all()
    ]


def delete(context, medium_id):
    maybe_medium = Medium.query.filter_by(id=medium_id).first()

    if not maybe_medium:
        return False

    # Delete "Medium" DB row. Note: SQLAlchemy
    # automatically removes MediaTags rows!
    session = context.session()
    try:
        _delete(session, maybe_medium)
    except FileNotFoundError:
        pass

    return True


def _delete(session, medium):
    hash = medium.hash
    extension = EXTENSIONS[medium.mime_type]
    session.delete(medium)
    session.commit()

    medium_deleted.send(medium.id)

    _try_and_remove(f'media/{hash}.{extension}')

    for thumbnail_size, _ in current_app.config['BEEVENUE_THUMBNAIL_SIZES'].items():
        _try_and_remove(f'thumbs/{hash}.{thumbnail_size}.jpg')


def get_zip(medium_id):
    medium = Medium.query.filter_by(id=medium_id).first()

    if not medium:
        return 404, None

    result_bytes = io.BytesIO()
    with zipfile.ZipFile(result_bytes, mode='w') as z:
        # Add metadata
        metadata_bytes = _get_metadata_bytes(medium)
        z.writestr(f'{medium.id}.metadata.json', metadata_bytes)

        # Add data
        extension = EXTENSIONS[medium.mime_type]
        with current_app.open_resource(
            f'media/{medium.hash}.{extension}',
                'rb') as res:
            z.writestr(f'{medium.id}.{extension}', res.read())

    result_bytes.seek(0)
    return 200, result_bytes
