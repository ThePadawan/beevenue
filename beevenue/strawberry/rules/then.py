
from .common import (  # noqa: F401
    HasRating, HasAnyTagsLike, HasAnyTagsIn
)


class Fail(object):
    def get_medium_ids(self, session, filtering_medium_ids=[]):
        return []

    def pprint_then(self):
        return "should not exist."
