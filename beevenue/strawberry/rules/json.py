import json
from typing import List, Literal, Optional, TypedDict, Union

from .common import (
    HasAnyTagsIn,
    HasAnyTagsLike,
    HasRating,
    IffAndThen,
    RulePart,
)
from .iff import All, Iff
from .rule import Rule
from .then import Fail, Then


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

TopLevelRule = TypedDict(
    "TopLevelRule", {"if": RuleJson, "then": List[RuleJson]}
)


def _decode_common(obj: RuleJson) -> IffAndThen:
    if obj["type"] == "hasRating":
        return HasRating(obj.get("data", None))  # type: ignore

    if obj["type"] == "hasAnyTagsIn":
        return HasAnyTagsIn(*obj["data"])

    if obj["type"] == "hasAnyTagsLike":
        return HasAnyTagsLike(*obj["data"])

    raise Exception(f'Unknown rule part type "{obj["type"]}"')


def _decode_iff(obj: RuleJson) -> Iff:
    if obj["type"] == "all":
        return All()
    return _decode_common(obj)


def _decode_then(obj: RuleJson) -> Then:
    if obj["type"] == "fail":
        return Fail()
    return _decode_common(obj)


def _decode_thens(thens_obj: List[RuleJson]) -> List[Then]:
    return [_decode_then(t) for t in thens_obj]


def _decode_rule(obj: TopLevelRule) -> Rule:
    iff = _decode_iff(obj["if"])
    thens = _decode_thens(obj["then"])

    return Rule(iff, thens)


def decode_rules(json_text: str) -> List[Rule]:
    rules_obj = json.loads(json_text)
    return decode_rules_obj(rules_obj)


def decode_rules_obj(obj: List[TopLevelRule]) -> List[Rule]:
    return [_decode_rule(rule) for rule in obj]


class RulePartEncoder(json.JSONEncoder):
    def default(self, obj: RulePart) -> RuleJson:
        if isinstance(obj, All):
            all: AllJson = {"type": "all"}
            return all
        if isinstance(obj, Fail):
            fail: FailJson = {"type": "fail"}
            return fail
        if isinstance(obj, HasRating):
            if obj.rating:
                specificRatingJson: HasSpecificRatingJson = {
                    "type": "hasRating",
                    "data": obj.rating,
                }
                return specificRatingJson
            else:
                anyRatingJson: HasAnyRatingJson = {"type": "hasRating"}
                return anyRatingJson
        if isinstance(obj, HasAnyTagsIn):
            hasAnyTagsInJson: HasAnyTagsInJson = {
                "type": "hasAnyTagsIn",
                "data": list(obj.tag_names),
            }
            return hasAnyTagsInJson
        if isinstance(obj, HasAnyTagsLike):
            hasAnyTagsLikeJson: HasAnyTagsLikeJson = {
                "type": "hasAnyTagsLike",
                "data": list(obj.regexes),
            }
            return hasAnyTagsLikeJson
        raise Exception(f"Cannot encode rule part with type {type(obj)}")


class RuleEncoder(json.JSONEncoder):
    def default(self, obj: TopLevelRule) -> Rule:
        if isinstance(obj, Rule):
            i = RulePartEncoder()
            return {
                "if": i.default(obj.iff),
                "then": [i.default(t) for t in obj.thens],
            }
        raise Exception(f"Cannot encode rule with type {type(obj)}")
