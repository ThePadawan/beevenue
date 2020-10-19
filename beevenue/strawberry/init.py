from ..flask import BeevenueFlask

from .routes import bp
from .json import RuleEncoder


def init_app(app: BeevenueFlask) -> None:
    app.register_blueprint(bp)
    app.json_encoder = RuleEncoder
