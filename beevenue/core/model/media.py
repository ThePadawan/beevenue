from flask import current_app
import os

EXTENSIONS = {
    'video/mp4': 'mp4',
    'video/webm': 'webm',
    'image/png': 'png',
    'image/gif': 'gif',
    'image/jpeg': 'jpg',
    'image/jpg': 'jpg',
    'application/x-shockwave-flash': "swf"
}


def delete(session, medium):
    hash = medium.hash
    extension = EXTENSIONS[medium.mime_type]
    session.delete(medium)
    session.commit()

    os.remove(f'media/{hash}.{extension}')

    for thumbnail_size, _ in current_app.config['BEEVENUE_THUMBNAIL_SIZES'].items():
        os.remove(f'thumbs/{hash}.{thumbnail_size}.jpg')
