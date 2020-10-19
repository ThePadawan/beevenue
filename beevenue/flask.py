from pathlib import Path
from typing import Any, List, Optional

from flask import Response
from flask import current_app, Flask, Request
from flask import request as flask_request

from .convert import decorate_response, try_convert_model
from .spindex.interface import SpindexSessionFactory
from .types import MediumDocument

EXTENSIONS = {
    "video/mp4": "mp4",
    "video/webm": "webm",
    "video/x-matroska": "mkv",
    "image/png": "png",
    "image/gif": "gif",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
}


class BeevenueContext:
    """Customized request context."""

    def __init__(self, is_sfw: bool, user_role: Optional[str]):
        self.is_sfw = is_sfw
        self.user_role = user_role


class BeevenueRequest(Request):
    """Customized request class."""

    beevenue_context: BeevenueContext
    spindex_session: SpindexSessionFactory


request: BeevenueRequest = flask_request  # type: ignore


class BeevenueResponse(Response):
    """Customized response object."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.push_links: List[str] = []
        self.sendfile_header: Optional[str] = None

    def push_medium(self, medium: MediumDocument) -> None:
        """Note that file of specified medium is relevant to this response.

        This allows us to set prefetch headers for optimization."""

        self.push_links.append(
            f"<{_file_url(medium)}>; rel=prefetch;"
            " crossorigin=use-credentials; as=image"
        )

    def push_thumbs(self, media: List[MediumDocument]) -> None:
        """Note that thumbs of specified media are relevant to this response.

        This allows us to set prefetch headers for optimization."""

        for medium in media:
            self.push_links.append(
                f"<{_thumb_url(medium)}>; rel=prefetch;"
                " crossorigin=use-credentials; as=image"
            )

    def set_sendfile_header(self, path: Path) -> None:
        """Set the Sendfile header to the specified path."""
        self.sendfile_header = str(path)


class BeevenueFlask(Flask):
    """Custom implementation of Flask application """

    request_class = BeevenueRequest
    response_class = BeevenueResponse

    def __init__(
        self, name: str, hostname: str, port: int, *args: Any, **kwargs: Any
    ) -> None:
        Flask.__init__(self, name, *args, **kwargs)
        self.hostname = hostname
        self.port = port

    def make_response(self, rv: Any) -> BeevenueResponse:
        model = try_convert_model(rv)
        res: BeevenueResponse = super().make_response(model)
        decorate_response(res, rv)
        return res

    def start(self) -> None:
        """Run this application (main uWSGI entrypoint)."""
        if self.config["DEBUG"]:
            self.run(self.hostname, self.port, threaded=True)
        else:
            self.run(
                self.hostname, self.port, threaded=True, use_x_sendfile=True
            )


def _thumb_url(medium: MediumDocument) -> str:
    """Get URL for this medium's thumbnail."""

    path = Path(
        "/",
        current_app.config.get("BEEVENUE_ROOT", "/"),
        "thumbs",
        str(medium.medium_id),
    )
    return str(path)


def _file_url(medium: MediumDocument) -> str:
    """Get URL for this medium's file."""
    path = Path(
        "/",
        current_app.config.get("BEEVENUE_ROOT", "/"),
        "files",
        f"{medium.medium_hash}.{EXTENSIONS[medium.mime_type]}",
    )
    return str(path)
