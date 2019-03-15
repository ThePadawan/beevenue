from ....models import Tag


class TagSearch(object):
    def __init__(self, session, all_media):
        self._session = session
        self.all_media = all_media

    def evaluate(self, terms, is_and):
        # User supplied no search terms: show nothing
        if not terms:
            return []

        term_strings = set([t.term for t in terms])

        term_tags = self._session.query(Tag)\
            .filter(Tag.tag.in_(term_strings)).all()

        term_to_tag = {}
        for tag in term_tags:
            term_to_tag[tag.tag] = tag

        implying_tags = set()
        for t in [term.term for term in terms if not term.is_quoted]:
            tag = term_to_tag.get(t, None)
            if not tag:
                continue
            implying_tags |= set(tag.implying_this)

        implying_tag_strings = set([t.tag for t in implying_tags])

        results = []

        for medium in self.all_media:
            medium_tag_names = set([t.tag for t in medium.tags])

            target_strings = term_strings | implying_tag_strings

            intersection = medium_tag_names.intersection(target_strings)

            if is_and and len(intersection) == len(term_strings):
                results.append(medium.id)
            if not is_and and intersection:
                results.append(medium.id)

        return results
