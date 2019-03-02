from hashlib import md5


def md5sum(stream):
    m = md5()
    while True:
        buf = stream.read(1024 * 1024 * 16)
        if not buf:
            break
        m.update(buf)

    return m.hexdigest()