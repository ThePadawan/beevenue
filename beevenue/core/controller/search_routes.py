from flask import request
import json

from ..model.search import run, suggestions, terms
from .schemas.query import search_query_params_schema

from . import bp


@bp.route("/search")
@search_query_params_schema
def search_endpoint():
    search_term_list = request.args.get("q").split(" ")
    return run(search_term_list)


@bp.route("/search/validators")
def get_search_validators():
    return (
        json.dumps(
            [
                # Turns out python's syntax is incompatible with Javascript's.
                # This is a hacky way to make it so.
                s.pattern.replace("?P<", "?<")
                for s in terms.VALID_SEARCH_TERM_REGEXES
            ]
        ),
        200,
    )


@bp.route("/search/suggestions/<string:query>", methods=["GET"])
def get_search_suggestions(query):
    return json.dumps(suggestions.get(query)), 200
