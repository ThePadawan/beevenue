from flask import Blueprint
from flask_graphql import GraphQLView

from ... import permissions
from .graphql import schema

bp = Blueprint("graphql", __name__)

graphql_func = permissions.is_owner(
    GraphQLView.as_view(
        "graphql",
        schema=schema,
        graphiql=True,
    )
)

bp.add_url_rule("/graphql", view_func=graphql_func)
