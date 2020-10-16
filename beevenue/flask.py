from typing import Any

from flask import Flask

from .convert import decorate_response, try_convert_model
from .request import BeevenueRequest
from .response import BeevenueResponse


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
        input = try_convert_model(rv)
        res: BeevenueResponse = super().make_response(input)
        decorate_response(res, rv)
        return res

    def start(self) -> None:
        if self.config["DEBUG"]:
            self.run(self.hostname, self.port, threaded=True)
        else:
            self.run(
                self.hostname, self.port, threaded=True, use_x_sendfile=True
            )
