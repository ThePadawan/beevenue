import re

from ....models import Tag

def _get_indirect_hits(category_string, indirect_hits):
    FOO_RE = re.compile(category_string + r':(.*)')

    indirect_hit_set = set()
    for indirect_hit in indirect_hits:
        for implied_tag in indirect_hit.implied_by_this:
            match = FOO_RE.match(implied_tag.tag)
            if match:
                indirect_hit_set.add(match.group(0))

    return indirect_hit_set


class CategorySearch(object):
    def __init__(self, session, all_media, search_terms):
        self._session = session
        self.all_media = all_media
        self.search_terms = search_terms

    def _tags_per_category(self):
        category_names = set([t.category for t in self.search_terms.category])

        tags_per_category = {}

        for category_name in category_names:
            tags_in_this_category = \
                self._session.query(Tag)\
                .filter(Tag.tag.like(f'{category_name}:%'))\
                .all()

            tags_implying_this_category = set()
            for t in tags_in_this_category:
                tags_implying_this_category |= set(t.implying_this)

            tags_per_category[category_name] = (
                tags_in_this_category,
                tags_implying_this_category
            )

        return tags_per_category

    def evaluate(self):
        tags_per_category = self._tags_per_category()

        results = set()

        for category_term in self.search_terms.category:
            category_string = category_term.category
            tags_in_this_category = tags_per_category.get(
                category_string, None)
            if not tags_in_this_category:
                continue

            for medium in self.all_media:
                direct_tags = tags_in_this_category[0]
                indirect_tags = tags_in_this_category[1]
                these_tags = set(medium.tags)

                direct_hits = these_tags.intersection(direct_tags)
                indirect_hits = these_tags.intersection(indirect_tags)

                indirect_hit_set = _get_indirect_hits(
                    category_string, indirect_hits)
                direct_hit_strings = set([t.tag for t in direct_hits])

                hit_count = len(direct_hit_strings | indirect_hit_set)

                is_hit = category_term.having(hit_count)
                if is_hit:
                    results.add(medium)

        return set([m.id for m in results])