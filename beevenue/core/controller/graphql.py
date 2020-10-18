from collections import defaultdict
from typing import Any, Callable, Dict, List, Type

import graphene

from ...spindex.spindex import SPINDEX

ratings: List[str] = ["u", "s", "q", "e"]


class _StatisticsType:
    stats: Dict[str, int]


def _generate_statistics_type() -> Type:
    """
    Generates a Graphene type with an Int field and resolver per rating.
    i.e.
        q = graphene.Int()
        resolve_q = ...
    """

    def ctor(self: Any) -> None:
        stats: Dict[str, int] = defaultdict(int)
        for medium in SPINDEX.all():
            stats[medium.rating] += 1
        self.stats = stats

    type_dict: Dict[str, Callable] = {"__init__": ctor}

    for rating in ratings:
        type_dict[rating] = graphene.Int()

        def generate_resolver(rating_query: str) -> Callable[[Any, Any], int]:
            def resolver(root: _StatisticsType, _: Any) -> int:
                return root.stats[rating_query]

            return resolver

        type_dict[f"resolve_{rating}"] = generate_resolver(rating)

    return type("RatingStatistics", (graphene.ObjectType,), type_dict)


_RatingStatistics = _generate_statistics_type()


class _Statistics(graphene.ObjectType):
    ratings = graphene.Field(_RatingStatistics)

    def resolve_ratings(self, _: Any) -> object:
        return _RatingStatistics()


class _Query(graphene.ObjectType):
    statistics = graphene.Field(_Statistics)

    def resolve_statistics(self, _: Any) -> _Statistics:
        return _Statistics()


schema = graphene.Schema(query=_Query)
