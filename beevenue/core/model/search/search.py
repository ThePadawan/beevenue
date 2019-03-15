from sqlalchemy.orm import load_only

from ....models import Medium, MediaTags, TagAlias

from .terms import get_search_terms
from .counting_search import CountingSearch
from .category_search import CategorySearch
from .tag_search import TagSearch


def run_search(context, search_term_list):
    search_terms = get_search_terms(search_term_list)

    medium_ids = Search(context, search_terms).evaluate()

    filters = []
    if context.is_sfw:
        filters.append(Medium.rating == 's')
    if context.user_role != 'admin':
        filters.append(Medium.rating != 'e')
        filters.append(Medium.rating != 'u')

    if not medium_ids:
        return []

    if filters:
        result = Medium.query.filter(Medium.id.in_(medium_ids), *filters)\
            .options(load_only("id"))\
            .all()
        medium_ids = [m.id for m in result]

    return medium_ids


class Search(object):
    def __init__(self, context, search_terms):
        self.context = context
        self._session = context.session()
        self.all_media = self._session.query(Medium).all()
        self.search_terms = search_terms

    def _replace_aliases(self):
        possible_alias_terms = set()
        possible_alias_terms |= set(
            [t.term for t in self.search_terms.positive])
        possible_alias_terms |= set(
            [t.term for t in self.search_terms.negative])

        if not possible_alias_terms:
            # Nothing to do
            return self.search_terms

        found_aliases = self._session.query(TagAlias)\
            .filter(TagAlias.alias.in_(possible_alias_terms))\
            .all()

        replacements = {}

        for found_alias in found_aliases:
            replacements[found_alias.alias] = found_alias.tag.tag

        for old, new in replacements.items():
            for target in [
              self.search_terms.positive,
              self.search_terms.negative]:
                for term in target:
                    if term.term == old:
                        term.term = new

        return self.search_terms

    def evaluate(self):
        """Returns medium IDs."""

        search_terms = self._replace_aliases()

        s = CountingSearch(self._session, self.all_media)
        found_by_counting = s.evaluate(search_terms.counting)

        s = CategorySearch(self._session, self.all_media, self.search_terms)
        found_by_category = s.evaluate()

        s = TagSearch(self._session, self.all_media)

        pos_medium_ids = s.evaluate(search_terms.positive, True)
        neg_medium_ids = s.evaluate(search_terms.negative, False)

        to_exclude = set(neg_medium_ids)

        found_by_rating = set()
        if search_terms.rating:
            rating_term = search_terms.rating[0]
            ids = self._session.query(Medium.id).select_from(Medium)\
                .filter(Medium.rating == rating_term.rating).all()
            ids = [i[0] for i in ids]
            found_by_rating = set(ids)

        found_by_pos = set(pos_medium_ids)

        # INTERSECT all non-empty result sets.
        non_empty_result_sets = []
        for result_set in [
                found_by_pos, found_by_category,
                found_by_counting, found_by_rating]:
            if len(result_set) > 0:
                non_empty_result_sets.append(result_set)

        if len(non_empty_result_sets) == 0:
            if len(search_terms) == 0 or len(to_exclude) > 0:
                found = set(self._session.query(MediaTags.c.medium_id).all())
                found = set([f[0] for f in found])
            else:
                found = set()
        else:
            found = non_empty_result_sets[0]
            for other_set in non_empty_result_sets[1:]:
                found &= other_set

        found -= to_exclude

        return found
