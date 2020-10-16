from flask import Request
from flask import request as flask_request

from .context import BeevenueContext
from .spindex.interface import SpindexCallable


class BeevenueRequest(Request):
    beevenue_context: BeevenueContext
    spindex: SpindexCallable


request: BeevenueRequest = flask_request  # type: ignore
