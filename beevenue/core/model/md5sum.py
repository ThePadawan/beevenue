from hashlib import md5
from typing import Union

from werkzeug.datastructures import FileStorage

from beevenue.io import HelperBytesIO

Readable = Union[HelperBytesIO, FileStorage]


def md5sum(stream: Readable) -> str:
    m = md5()
    while True:
        buf = stream.read(1024 * 1024 * 16)
        if not buf:
            break
        m.update(buf)

    return m.hexdigest()
