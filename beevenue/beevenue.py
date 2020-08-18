import os

from flask_compress import Compress
from flask_migrate import Migrate
from flask_cors import CORS


from .cli import init_cli
from .flask import BeevenueFlask


def get_application(extra_config=None, fill_db=None):
    application = BeevenueFlask("strawberry", "0.0.0.0", 7000)

    application.config.from_envvar("BEEVENUE_CONFIG_FILE")

    if extra_config:
        extra_config(application)

    CORS(
        application,
        supports_credentials=True,
        origins=application.config["BEEVENUE_ALLOWED_CORS_ORIGINS"],
    )

    Compress(application)

    from .db import db

    db.init_app(application)
    Migrate(application, db)

    if application.config.get("SENTRY_DSN"):
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration

        sentry_sdk.init(
            dsn=application.config["SENTRY_DSN"],
            integrations=[FlaskIntegration()],
        )

    from .marshmallow import ma

    ma.init_app(application)

    with application.app_context():
        from .login_manager import login_manager

        login_manager.init_app(application)

        from .principal import principal

        principal.init_app(application)

        from .core.controller.context import init_app as context_init_app

        context_init_app(application)

        from .auth import blueprint as auth_bp
        from .core.controller.routes import bp as routes_bp
        from .strawberry.routes import bp as strawberry_bp
        from .sushi.routes import bp as sushi_bp
        from .spindex.routes import bp as spindex_bp

        application.register_blueprint(auth_bp)
        application.register_blueprint(routes_bp)
        application.register_blueprint(strawberry_bp)
        application.register_blueprint(sushi_bp)
        application.register_blueprint(spindex_bp)

        from .strawberry.rules.json import RuleEncoder

        application.json_encoder = RuleEncoder

        # Only used for testing - needs to happen after DB is setup,
        # but before filling Spindex from DB.
        if fill_db:
            # Tests also don't use migrations, they just create the schema
            # from scratch.
            db.create_all()
            fill_db()

        from .cache import init_app as cache_init_app

        cache_init_app(application)

        from .spindex import init_app as spindex_init_app

        if "BEEVENUE_SKIP_SPINDEX" in os.environ:
            print("Skipping Spindex initialization")
        else:
            spindex_init_app(application)

    init_cli(application)

    import beevenue.auth.auth

    return application
