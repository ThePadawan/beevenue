from .common import HasRating, HasAnyTagsLike, HasAnyTagsIn  # noqa: F401

from ...spindex.spindex import SPINDEX


class All(object):
    def get_medium_ids(self, filtering_medium_ids=[]):
        return [m.id for m in SPINDEX.all()]

    def applies_to(self, medium_id):
        return True

    def pprint_if(self):
        return "Any medium"
