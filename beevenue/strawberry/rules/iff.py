from ...models import Medium

from .common import (  # noqa: F401
    HasRating, HasAnyTagsLike, HasAnyTagsIn
)


class All(object):
    def get_medium_ids(self, session, filtering_medium_ids=[]):
        media = session.query(Medium).all()
        return [m.id for m in media]

    def pprint_if(self):
        return "Any medium"
