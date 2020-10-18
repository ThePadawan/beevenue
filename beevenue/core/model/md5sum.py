from hashlib import md5
from typing import Union

from werkzeug.datastructures import FileStorage

from beevenue.io import HelperBytesIO

Readable = Union[HelperBytesIO, FileStorage]


def md5sum(stream: Readable) -> str:
    """Return string representation of specified byte stream."""

    calc = md5()
    while True:
        buf = stream.read(1024 * 1024 * 64)
        if not buf:
            break
        calc.update(buf)

    return calc.hexdigest()
