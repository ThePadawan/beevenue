
from ....spindex.spindex import SPINDEX

from .terms import get_search_terms
from .terms.simple import RatingSearchTerm, Negative


def run_search(context, search_term_list):
    search_terms = get_search_terms(search_term_list)

    medium_ids = Search(context, search_terms).evaluate()
    return medium_ids


class Search(object):
    def __init__(self, context, search_terms):
        search_terms = set(search_terms)
        if context.is_sfw:
            search_terms.add(RatingSearchTerm("s"))
        if context.user_role != "admin":
            search_terms.add(Negative(RatingSearchTerm('e')))
            search_terms.add(Negative(RatingSearchTerm('u')))

        self.search_terms = search_terms

    def evaluate(self):
        all_media = SPINDEX.all()

        result = set()

        for x in all_media:
            for search_term in self.search_terms:
                if not search_term.applies_to(x):
                    break
            else:
                result.add(x.id)

        return result
