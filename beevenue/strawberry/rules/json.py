import json

from .rule import Rule
from . import iff, then


def _decode_part(obj):
    if obj["type"] == "all":
        return iff.All()

    if obj["type"] == "fail":
        return then.Fail()

    if obj["type"] == "hasRating":
        return iff.HasRating(obj.get("data", None))

    if obj["type"] == "hasAnyTagsIn":
        return iff.HasAnyTagsIn(*obj["data"])

    if obj["type"] == "hasAnyTagsLike":
        return iff.HasAnyTagsLike(*obj["data"])

    raise Exception("Unknown rule IF")


def _decode_thens(thens_obj):
    return [_decode_part(t) for t in thens_obj]


def _decode_rule(obj):
    iff = _decode_part(obj["if"])
    thens = _decode_thens(obj["then"])

    return Rule(iff, thens)


def decode_rules(json_text):
    rules_obj = json.loads(json_text)
    return decode_rules_obj(rules_obj)


def decode_rules_obj(obj):
    return [_decode_rule(rule) for rule in obj]


class RulePartEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, iff.All):
            return {"type": "all"}
        if isinstance(obj, then.Fail):
            return {"type": "fail"}
        if isinstance(obj, iff.HasRating):
            result = {"type": "hasRating"}
            if obj.rating:
                result["data"] = obj.rating
            return result
        if isinstance(obj, iff.HasAnyTagsIn):
            return {"type": "hasAnyTagsIn", "data": list(obj.tag_names)}
        if isinstance(obj, iff.HasAnyTagsLike):
            return {"type": "hasAnyTagsLike", "data": list(obj.regexes)}
        return json.JSONEncoder.default(self, obj)


class RuleEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Rule):
            i = RulePartEncoder()
            return {'if': i.default(obj.iff), 'then': [i.default(t) for t in obj.thens]}
        return json.JSONEncoder.default(self, obj)
