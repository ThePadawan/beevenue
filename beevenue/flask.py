from flask import Flask
from .response import BeevenueResponse
from .convert import try_convert_model, decorate_response


class BeevenueFlask(Flask):
    """Custom implementation of Flask application """

    response_class = BeevenueResponse

    def __init__(self, name, hostname, port, *args, **kwargs):
        Flask.__init__(self, name, *args, **kwargs)
        self.hostname = hostname
        self.port = port

    def make_response(self, rv):
        input = try_convert_model(rv)
        res = super().make_response(input)
        decorate_response(res, rv)
        return res

    def start(self):
        if self.config["DEBUG"]:
            self.run(self.hostname, self.port, threaded=True)
        else:
            self.run(
                self.hostname, self.port, threaded=True, use_x_sendfile=True
            )
