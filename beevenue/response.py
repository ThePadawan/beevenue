from pathlib import Path
from typing import List
from flask import Response, current_app
from .core.model import media
from .spindex.load import SpindexedMedium


def _thumb_path(m: SpindexedMedium):
    p = Path(
        "/", current_app.config.get("BEEVENUE_ROOT", "/"), "thumbs", str(m.id)
    )
    return str(p)


def _file_path(m: SpindexedMedium):
    p = Path(
        "/",
        current_app.config.get("BEEVENUE_ROOT", "/"),
        "files",
        f"{m.hash}.{media.EXTENSIONS[m.mime_type]}",
    )
    return str(p)


class BeevenueResponse(Response):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.push_links = []
        self.sendfile_header = None

    def push_file(self, m: SpindexedMedium):
        self.push_links.append(
            f"<{_file_path(m)}>; rel=prefetch; crossorigin=use-credentials; as=image"
        )

    def push_thumbs(self, media: List[SpindexedMedium]):
        for m in media:
            self.push_links.append(
                f"<{_thumb_path(m)}>; rel=prefetch; crossorigin=use-credentials; as=image"
            )

    def set_sendfile_header(self, path):
        self.sendfile_header = str(path)
