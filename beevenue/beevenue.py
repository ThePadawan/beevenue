from flask import (
    Flask
)

from flask_migrate import Migrate
from flask_cors import CORS


class BeevenueFlask(Flask):
    """Custom implementation of Flask application """

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


def get_application(extra_config=None):
    application = BeevenueFlask(
        "strawberry",
        '0.0.0.0',
        7000)

    application.config.from_envvar('BEEVENUE_CONFIG_FILE')

    if extra_config:
        extra_config(application)

    CORS(
        application,
        supports_credentials=True,
        origins=application.config['BEEVENUE_ALLOWED_CORS_ORIGINS'])

    # if application.config['DEBUG']:
    #     application.config['SQLALCHEMY_ECHO'] = True

    from .db import db
    db.init_app(application)
    migrate = Migrate(application, db)

    if application.config.get('SENTRY_DSN'):
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration

        sentry_sdk.init(
            dsn=application.config['SENTRY_DSN'],
            integrations=[FlaskIntegration()]
        )

    from .marshmallow import ma
    ma.init_app(application)

    with application.app_context():
        from .login_manager import login_manager
        login_manager.init_app(application)

        from .principal import principal
        principal.init_app(application)

        from .auth import blueprint as auth_bp
        from .core import blueprint as routes_bp
        from .strawberry.routes import bp as strawberry_bp
        application.register_blueprint(auth_bp)
        application.register_blueprint(routes_bp)
        application.register_blueprint(strawberry_bp)

        db.create_all()

    import beevenue.auth.auth

    return application
