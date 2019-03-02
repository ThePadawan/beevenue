import json

from .rule import Rule
from . import iff

# TODO: Also write decoders. Consider Flask-JSON and @encoder, which seems to allow
# more customization



class RulePartEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, iff.All):
            return {"type": "all"}
        if isinstance(obj, iff.HasRating):
            return {"type": "hasRating", "data": obj.rating}
        if isinstance(obj, iff.HasAnyTagsIn):
            return {"type": "hasAnyTagsIn", "data": obj.names}
        if isinstance(obj, iff.HasAnyTagsLike):
            return {"type": "hasAnyTagsLike", "data": obj.like_exprs}
        return json.JSONEncoder.default(self, obj)


class RuleEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Rule):
            i = RulePartEncoder()
            return {'if': i.default(obj.iff), 'then': [i.default(t) for t in obj.thens]}
        return json.JSONEncoder.default(self, obj)