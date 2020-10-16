from flask import Blueprint

bp = Blueprint("core", __name__)

from . import graphql_routes, media_routes, routes, tag_routes
