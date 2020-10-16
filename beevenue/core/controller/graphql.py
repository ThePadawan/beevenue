from collections import defaultdict
from typing import Any, Callable, Dict, List, Type

import graphene

from ...spindex.spindex import SPINDEX

ratings: List[str] = ["u", "s", "q", "e"]


class StatisticsType(object):
    stats: Dict[str, int]


def generate_statistics_type() -> Type:
    """
    Generates a Graphene type with an Int field and resolver per rating.
    i.e.
        q = graphene.Int()
        resolve_q = ...
    """

    def ctor(self: Any) -> None:
        stats: Dict[str, int] = defaultdict(int)
        for m in SPINDEX.all():
            stats[m.rating] += 1
        self.stats = stats

    type_dict: Dict[str, Callable] = {"__init__": ctor}

    for rating in ratings:
        type_dict[rating] = graphene.Int()

        def generate_resolver(rating_query: str) -> Callable[[Any, Any], int]:
            def resolver(root: StatisticsType, info: Any) -> int:
                return root.stats[rating_query]

            return resolver

        type_dict[f"resolve_{rating}"] = generate_resolver(rating)

    return type("RatingStatistics", (graphene.ObjectType,), type_dict)


RatingStatistics = generate_statistics_type()


class Statistics(graphene.ObjectType):
    ratings = graphene.Field(RatingStatistics)

    def resolve_ratings(root: Any, info: Any) -> object:
        return RatingStatistics()


class Query(graphene.ObjectType):
    statistics = graphene.Field(Statistics)

    def resolve_statistics(root: Any, info: Any) -> Statistics:
        return Statistics()


schema = graphene.Schema(query=Query)
