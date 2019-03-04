from flask import (
    Flask
)

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_login import LoginManager
from flask_principal import Principal

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


class BeevenueFlask(Flask):
    """Custom implementation of Flask app """

    def __init__(self, name, hostname, port, *args, **kwargs):
        Flask.__init__(self, name, *args, **kwargs)
        self.hostname = hostname
        self.port = port

    def start(self):
        if self.config["DEBUG"]:
            self.run(self.hostname, self.port, threaded=True)
        else:
            self.run(
                self.hostname,
                self.port,
                threaded=True,
                use_x_sendfile=True)


def get_application():
    application = BeevenueFlask(
        "strawberry",
        '0.0.0.0',
        7000)

    application.config.from_envvar('BEEVENUE_CONFIG_FILE')

    CORS(
        application,
        supports_credentials=True,
        origins=application.config['BEEVENUE_ALLOWED_CORS_ORIGINS'])

    # if application.config['DEBUG']:
    #     application.config['SQLALCHEMY_ECHO'] = True

    return application

app = get_application()
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.config['RULES'] = app.config['GET_RULES']()

sentry_sdk.init(
    dsn=app.config['SENTRY_DSN'],
    integrations=[FlaskIntegration()]
)

ma = Marshmallow(app)

from .auth import blueprint as auth_bp
from .core import blueprint as routes_bp
from .strawberry.routes import bp as strawberry_bp
app.register_blueprint(auth_bp)
app.register_blueprint(routes_bp)
app.register_blueprint(strawberry_bp)

login_manager = LoginManager()
login_manager.init_app(app)

Principal(app)

db.create_all()

import beevenue.auth.auth
