from flask_graphql import GraphQLView

from . import bp
from ... import permissions
from .graphql import schema

graphql_func = permissions.is_owner(
    GraphQLView.as_view(
        "graphql",
        schema=schema,
        graphiql=True,
    )
)

bp.add_url_rule("/graphql", view_func=graphql_func)
