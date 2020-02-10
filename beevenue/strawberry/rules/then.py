from .common import HasRating, HasAnyTagsLike, HasAnyTagsIn  # noqa: F401


class Fail(object):
    def get_medium_ids(self, filtering_medium_ids=[]):
        return []

    def applies_to(self, medium_id):
        return False

    def pprint_then(self):
        return "should not exist."
