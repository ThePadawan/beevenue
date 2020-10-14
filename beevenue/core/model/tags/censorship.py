from collections import defaultdict
from flask import request
from ....models import Tag


class Censorship(object):
    def __init__(self, session, tag_ids=None):
        self._set_ratings()
        self._fill_cache(session, tag_ids)

        self.censored_counter = 0
        self.names = dict()

    def _set_ratings(self):
        context = request.beevenue_context

        self.ratings_to_censor = set(["u"])
        if context.user_role != "admin":
            self.ratings_to_censor.add("e")
        if context.is_sfw:
            self.ratings_to_censor |= set(["q", "e"])

    def _fill_cache(self, session, tag_ids):
        query = session.query(Tag)
        if tag_ids:
            query = query.filter(Tag.id.in_(tag_ids))
        tags = query.all()

        self.name_lookup = {}
        self.id_lookup = {}
        self.category_lookup = defaultdict(lambda: True)

        for t in tags:
            self.name_lookup[t.tag] = t
            self.id_lookup[t.id] = t

            maybe_category = t.tag.split(":")[0]
            if maybe_category != t.tag:
                self.category_lookup[maybe_category] &= self.is_tag_censored(
                    t.tag
                )

    def is_tag_censored(self, tag_name):
        return self.name_lookup[tag_name].rating in self.ratings_to_censor

    def is_category_censored(self, category_name):
        return self.category_lookup[category_name]

    def get_name(self, id):
        if id not in self.names:
            thing = self.id_lookup[id]

            if thing.rating in self.ratings_to_censor:
                self.names[id] = f"anon{self.censored_counter}"
                self.censored_counter += 1
            else:
                self.names[id] = thing.tag

        return self.names[id]
