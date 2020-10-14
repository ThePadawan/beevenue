from flask import Blueprint

bp = Blueprint("core", __name__)

from . import routes, tag_routes, media_routes, graphql_routes, search_routes
