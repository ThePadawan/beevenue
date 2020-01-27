from flask import current_app

import io
import json
import os
import zipfile

from ...spindex.signals import medium_deleted

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


def _get_metadata_bytes(session, medium):
    metadata = {
        'rating': medium.rating,
        'tags:': [t.tag for t in medium.tags]
    }
    metadata_text = json.dumps(metadata)
    return metadata_text.encode('utf-8')


def delete(session, medium):
    hash = medium.hash
    extension = EXTENSIONS[medium.mime_type]
    session.delete(medium)
    session.commit()

    medium_deleted.send(medium.id)

    _try_and_remove(f'media/{hash}.{extension}')

    for thumbnail_size, _ in current_app.config['BEEVENUE_THUMBNAIL_SIZES'].items():
        _try_and_remove(f'thumbs/{hash}.{thumbnail_size}.jpg')


def get_zip(session, medium):
    result_bytes = io.BytesIO()
    with zipfile.ZipFile(result_bytes, mode='w') as z:
        # Add metadata
        metadata_bytes = _get_metadata_bytes(session, medium)
        z.writestr(f'{medium.id}.metadata.json', metadata_bytes)

        # Add data
        extension = EXTENSIONS[medium.mime_type]
        with current_app.open_resource(
            f'media/{medium.hash}.{extension}',
                'rb') as res:
            z.writestr(f'{medium.id}.{extension}', res.read())

    result_bytes.seek(0)
    return result_bytes
