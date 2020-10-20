"""Application factory. Lots of initial setup is performed here."""

import os
from typing import Any, Callable

from flask_compress import Compress
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from .auth.auth import init as auth_init_app
from .auth.routes import blueprint as auth_bp
from .cache import init_app as cache_init_app
from .cli import init_cli
from .core import graphql_routes, media_routes, routes, tag_routes
from .db import db
from .db import init_app as db_init_app
from .flask import BeevenueFlask
from .init import init_app as context_init_app
from .login_manager import login_manager
from .principal import principal
from .spindex.init import init_app as spindex_init_app
from .spindex.routes import bp as spindex_bp
from .strawberry.init import init_app as strawberry_init_app


def _nop(_: Any) -> None:
    """Do nothing, intentionally."""


def get_application(
    extra_config: Callable[[BeevenueFlask], None] = _nop,
    fill_db: Callable[[SQLAlchemy], None] = _nop,
) -> BeevenueFlask:
    """Construct and return uWSGI application object."""

    application = BeevenueFlask("beevenue-main", "0.0.0.0", 7000)
    application.config.from_envvar("BEEVENUE_CONFIG_FILE")
    extra_config(application)

    CORS(
        application,
        supports_credentials=True,
        origins=application.config["BEEVENUE_ALLOWED_CORS_ORIGINS"],
    )
    Compress(application)

    db.init_app(application)
    Migrate(application, db)

    sentry_sdk.init(
        dsn=application.config["SENTRY_DSN"],
        integrations=[FlaskIntegration(), SqlalchemyIntegration()],
    )

    with application.app_context():
        login_manager.init_app(application)
        principal.init_app(application)
        context_init_app(application)
        db_init_app(application)

        application.register_blueprint(auth_bp)
        application.register_blueprint(routes.bp)
        application.register_blueprint(tag_routes.bp)
        application.register_blueprint(media_routes.bp)
        application.register_blueprint(graphql_routes.bp)
        application.register_blueprint(spindex_bp)

        strawberry_init_app(application)

        # Only used for testing - needs to happen after DB is setup,
        # but before filling Spindex from DB.
        fill_db(db)

        cache_init_app(application)

        if "BEEVENUE_SKIP_SPINDEX" in os.environ:
            print("Skipping Spindex initialization")
        else:
            spindex_init_app(application)

    init_cli(application)
    auth_init_app()

    return application
