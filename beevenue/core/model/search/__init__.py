from flask import request

from ....spindex.spindex import SPINDEX
from ....models import Medium

from .terms import get_search_terms
from .terms.simple import RatingSearchTerm, Negative


def run(search_term_list):
    search_terms = get_search_terms(search_term_list)

    context = request.beevenue_context
    medium_ids = _search(context, search_terms)

    if not medium_ids:
        return []

    media = Medium.query.\
        filter(Medium.id.in_(medium_ids)).\
        order_by(Medium.id.desc())

    return context.paginate(media)


def _search(context, search_terms):
    search_terms = set(search_terms)

    if context.is_sfw:
        search_terms.add(RatingSearchTerm("s"))
    if context.user_role != "admin":
        search_terms.add(Negative(RatingSearchTerm('e')))
        search_terms.add(Negative(RatingSearchTerm('u')))

    all_media = SPINDEX.all()
    result = set()

    for x in all_media:
        for search_term in search_terms:
            if not search_term.applies_to(x):
                break
        else:
            result.add(x.id)

    return result
