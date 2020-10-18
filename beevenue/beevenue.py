"""Application factory. Lots of initial setup is performed here."""

import os
from typing import Callable, Optional

from flask_compress import Compress
from flask_cors import CORS
from flask_migrate import Migrate
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from . import BeevenueFlask
from .auth.auth import init as auth_init_app
from .auth.routes import blueprint as auth_bp
from .cache import init_app as cache_init_app
from .cli import init_cli
from .core.controller import graphql_routes, media_routes, routes, tag_routes
from .db import db
from .init import init_app as context_init_app
from .login_manager import login_manager
from .principal import principal
from .spindex.init import init_app as spindex_init_app
from .spindex.routes import bp as spindex_bp
from .strawberry.routes import bp as strawberry_bp
from .strawberry.rules.json import RuleEncoder


def get_application(
    extra_config: Optional[Callable[[BeevenueFlask], None]] = None,
    fill_db: Optional[Callable[[], None]] = None,
) -> BeevenueFlask:
    """Construct and return uWSGI application object."""

    application = BeevenueFlask("beevenue-main", "0.0.0.0", 7000)

    application.config.from_envvar("BEEVENUE_CONFIG_FILE")

    if extra_config:
        extra_config(application)

    CORS(
        application,
        supports_credentials=True,
        origins=application.config["BEEVENUE_ALLOWED_CORS_ORIGINS"],
    )

    Compress(application)

    db.init_app(application)
    Migrate(application, db)

    if application.config.get("SENTRY_DSN"):
        sentry_sdk.init(
            dsn=application.config["SENTRY_DSN"],
            integrations=[FlaskIntegration(), SqlalchemyIntegration()],
        )

    with application.app_context():
        login_manager.init_app(application)
        principal.init_app(application)
        context_init_app(application)

        application.register_blueprint(auth_bp)
        application.register_blueprint(routes.bp)
        application.register_blueprint(tag_routes.bp)
        application.register_blueprint(media_routes.bp)
        application.register_blueprint(graphql_routes.bp)
        application.register_blueprint(strawberry_bp)
        application.register_blueprint(spindex_bp)

        application.json_encoder = RuleEncoder

        # Only used for testing - needs to happen after DB is setup,
        # but before filling Spindex from DB.
        if fill_db:
            # Tests also don't use migrations, they just create the schema
            # from scratch.
            db.create_all()
            fill_db()

        cache_init_app(application)

        if "BEEVENUE_SKIP_SPINDEX" in os.environ:
            print("Skipping Spindex initialization")
        else:
            spindex_init_app(application)

    init_cli(application)
    auth_init_app()

    return application
