import json
from typing import List

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
from . import types


def _decode_common(obj: types.RuleJson) -> IffAndThen:
    if obj["type"] == "hasRating":
        return HasRating(obj.get("data", None))  # type: ignore

    if obj["type"] == "hasAnyTagsIn":
        return HasAnyTagsIn(*obj["data"])

    if obj["type"] == "hasAnyTagsLike":
        return HasAnyTagsLike(*obj["data"])

    raise Exception(f'Unknown rule part type "{obj["type"]}"')


def _decode_iff(obj: types.RuleJson) -> Iff:
    if obj["type"] == "all":
        return All()
    return _decode_common(obj)


def _decode_then(obj: types.RuleJson) -> Then:
    if obj["type"] == "fail":
        return Fail()
    return _decode_common(obj)


def _decode_thens(thens_obj: List[types.RuleJson]) -> List[Then]:
    return [_decode_then(t) for t in thens_obj]


def _decode_rule(obj: types.TopLevelRuleJson) -> Rule:
    iff = _decode_iff(obj["if"])
    thens = _decode_thens(obj["then"])

    return Rule(iff, thens)


def decode_rules_json(json_text: str) -> List[Rule]:
    """Decode given JSON text into list of Rules."""
    return decode_rules_list(json.loads(json_text))


def decode_rules_list(json_list: List[types.TopLevelRuleJson]) -> List[Rule]:
    """Decode given list of dictionaries into list of Rules."""
    return [_decode_rule(rule) for rule in json_list]


class RulePartEncoder(json.JSONEncoder):
    """JSON Encoder for `RulePart`."""

    def default(self, o: RulePart) -> types.RuleJson:
        if isinstance(o, All):
            all_json: types.AllJson = {"type": "all"}
            return all_json
        if isinstance(o, Fail):
            fail: types.FailJson = {"type": "fail"}
            return fail
        if isinstance(o, HasRating):
            if o.rating:
                specific_rating_json: types.HasSpecificRatingJson = {
                    "type": "hasRating",
                    "data": o.rating,
                }
                return specific_rating_json

            any_rating_json: types.HasAnyRatingJson = {"type": "hasRating"}
            return any_rating_json
        if isinstance(o, HasAnyTagsIn):
            has_any_tags_in_json: types.HasAnyTagsInJson = {
                "type": "hasAnyTagsIn",
                "data": list(o.tag_names),
            }
            return has_any_tags_in_json
        if isinstance(o, HasAnyTagsLike):
            has_any_tags_like_json: types.HasAnyTagsLikeJson = {
                "type": "hasAnyTagsLike",
                "data": list(o.regexes),
            }
            return has_any_tags_like_json
        raise Exception(f"Cannot encode rule part with type {type(o)}")


class RuleEncoder(json.JSONEncoder):
    """JSON Encoder for `Rule`."""

    def default(self, o: types.TopLevelRuleJson) -> Rule:
        if isinstance(o, Rule):
            i = RulePartEncoder()
            return {
                "if": i.default(o.iff),
                "then": [i.default(t) for t in o.thens],
            }
        raise Exception(f"Cannot encode rule with type {type(o)}")
