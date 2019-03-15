from ....models import MediaTags


class CountingSearch(object):
    def __init__(self, session, all_media):
        self._session = session
        self.all_media = all_media

    def evaluate(self, counting_terms):
        all_media_ids = [m.id for m in self.all_media]

        found = set()
        for term in counting_terms:
            filters = []

            q = self._session\
                .query(MediaTags.c.medium_id)\
                .select_from(MediaTags)\
                .group_by(MediaTags.c.medium_id)

            if filters:
                q = q.filter(*filters)

            # If term contains zero, load values for >= 1 and
            # do ALL MINUS that result.
            found_for_this_term = set()

            if term.contains_zero():
                geq_1_term = term.with_(operator='>=', number=1)

                results_for_geq_1 = q.having(geq_1_term.having_expr()).all()
                results_for_geq_1 = [t[0] for t in results_for_geq_1]

                results_for_eq_0 = set(all_media_ids) - set(results_for_geq_1)
                found_for_this_term |= results_for_eq_0

            results = q.having(term.having_expr()).all()
            results = [t[0] for t in results]
            found_for_this_term |= set(results)

            if found:
                found &= found_for_this_term
            else:
                found = found_for_this_term

        return found
