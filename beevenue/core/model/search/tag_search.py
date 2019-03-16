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

        implication_map = {}
        for t in implying_tags:
            implication_map[t.tag] = set([tt.tag for tt in t.implied_by_this])

        results = []

        for medium in self.all_media:
            medium_tag_names = set([t.tag for t in medium.tags])

            is_hit = False

            hits = set()

            for term in term_strings:
                if term in medium_tag_names:
                    is_hit = True
                    hits.add(term)

            for term in implying_tag_strings:
                if term in medium_tag_names:
                    is_hit = True
                    for t in implication_map[term]:
                        hits.add(t)

            if is_and and hits and len(hits.union(term_strings)) == len(hits):
                results.append(medium.id)
            if not is_and and is_hit:
                results.append(medium.id)

        return results
