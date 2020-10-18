# pylint: disable=missing-class-docstring
from typing import List, Literal, Optional, TypedDict, Union


class AllJson(TypedDict):
    type: Literal["all"]


class FailJson(TypedDict):
    type: Literal["fail"]


class HasAnyRatingJson(TypedDict):
    type: Literal["hasRating"]


class HasSpecificRatingJson(TypedDict):
    type: Literal["hasRating"]
    data: Optional[str]


class HasAnyTagsInJson(TypedDict):
    type: Literal["hasAnyTagsIn"]
    data: List[str]


class HasAnyTagsLikeJson(TypedDict):
    type: Literal["hasAnyTagsLike"]
    data: List[str]


RuleJson = Union[
    AllJson,
    FailJson,
    HasAnyRatingJson,
    HasSpecificRatingJson,
    HasAnyTagsInJson,
    HasAnyTagsLikeJson,
]


TopLevelRuleJson = TypedDict(
    "TopLevelRuleJson", {"if": RuleJson, "then": List[RuleJson]}
)
