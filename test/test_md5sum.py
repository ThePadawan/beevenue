import io

from beevenue.core.file_upload import _md5sum


def test_md5sum():
    buf = io.BytesIO("Some Checksum Example".encode("utf-8"))
    actual = _md5sum(buf)
    print(actual)
    assert actual == "c35ef28ab559500a8c3361080c1a3806"
