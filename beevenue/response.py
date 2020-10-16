from pathlib import Path
from typing import Any, List, Optional

from flask import current_app, Response

from .core.model.extensions import EXTENSIONS
from .spindex.load import SpindexedMedium


def _thumb_path(m: SpindexedMedium) -> str:
    p = Path(
        "/", current_app.config.get("BEEVENUE_ROOT", "/"), "thumbs", str(m.id)
    )
    return str(p)


def _file_path(m: SpindexedMedium) -> str:
    p = Path(
        "/",
        current_app.config.get("BEEVENUE_ROOT", "/"),
        "files",
        f"{m.hash}.{EXTENSIONS[m.mime_type]}",
    )
    return str(p)


class BeevenueResponse(Response):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.push_links: List[str] = []
        self.sendfile_header: Optional[str] = None

    def push_file(self, m: SpindexedMedium) -> None:
        self.push_links.append(
            f"<{_file_path(m)}>; rel=prefetch; crossorigin=use-credentials; as=image"
        )

    def push_thumbs(self, media: List[SpindexedMedium]) -> None:
        for m in media:
            self.push_links.append(
                f"<{_thumb_path(m)}>; rel=prefetch; crossorigin=use-credentials; as=image"
            )

    def set_sendfile_header(self, path: Path) -> None:
        self.sendfile_header = str(path)
