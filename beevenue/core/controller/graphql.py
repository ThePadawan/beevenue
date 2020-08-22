from collections import defaultdict

import graphene

from ...spindex.spindex import SPINDEX


ratings = ["u", "s", "q", "e"]


def generate_statistics_type():
    """
    Generates a Graphene type with an Int field and resolver per rating.
    i.e.
        q = graphene.Int()
        resolve_q = ...
    """

    def ctor(self):
        stats = defaultdict(int)
        for m in SPINDEX.all():
            stats[m.rating] += 1
        self.stats = stats

    type_dict = {"__init__": ctor}

    for rating in ratings:
        type_dict[rating] = graphene.Int()

        def generate_resolver(rating_query):
            def resolver(root, info):
                return root.stats[rating_query]

            return resolver

        type_dict[f"resolve_{rating}"] = generate_resolver(rating)

    return type("RatingStatistics", (graphene.ObjectType,), type_dict)


RatingStatistics = generate_statistics_type()


class Statistics(graphene.ObjectType):
    ratings = graphene.Field(RatingStatistics)

    def resolve_ratings(root, info):
        return RatingStatistics()


class Query(graphene.ObjectType):
    statistics = graphene.Field(Statistics)

    def resolve_statistics(root, info):
        return Statistics()


schema = graphene.Schema(query=Query)
