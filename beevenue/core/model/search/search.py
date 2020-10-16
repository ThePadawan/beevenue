from typing import List, Optional, Set, TypeVar

from beevenue.context import BeevenueContext
from beevenue.request import request

from ....spindex.models import SpindexedMedium
from ....spindex.spindex import SPINDEX
from .pagination import Pagination
from .terms import get_search_terms, SearchTerm
from .terms.simple import Negative, RatingSearchTerm


def find_all() -> Pagination[SpindexedMedium]:
    return _run(set())


def run(search_term_list: List[str]) -> Pagination[SpindexedMedium]:
    search_terms = get_search_terms(search_term_list)

    if not search_terms:
        return Pagination.empty()

    return _run(search_terms)


def _run(search_terms: Set[SearchTerm]) -> Pagination[SpindexedMedium]:
    context = request.beevenue_context
    medium_ids = _search(context, search_terms)

    if not medium_ids:
        return Pagination.empty()

    sorted_medium_ids = list(medium_ids)
    sorted_medium_ids.sort(reverse=True)
    pagination = _paginate(sorted_medium_ids)
    media = SPINDEX.get_media(pagination.items)

    pagination.items = media  # type: ignore
    return pagination  # type: ignore


def _censor(
    context: BeevenueContext, search_terms: Set[SearchTerm]
) -> Set[SearchTerm]:
    search_terms = set(search_terms)

    if context.is_sfw:
        search_terms.add(RatingSearchTerm("s"))
    if context.user_role != "admin":
        search_terms.add(Negative(RatingSearchTerm("e")))
        search_terms.add(Negative(RatingSearchTerm("u")))

    return search_terms


def _search(
    context: BeevenueContext, search_terms: Set[SearchTerm]
) -> Set[int]:
    search_terms = _censor(context, search_terms)

    all_media = SPINDEX.all()
    result = set()

    for m in all_media:
        for search_term in search_terms:
            if not search_term.applies_to(m):
                break
        else:
            result.add(m.id)

    return result


T = TypeVar("T")


def _paginate(ids: List[T]) -> Pagination[T]:
    pageNumberArg: Optional[str] = request.args.get("pageNumber", type=str)
    pageSizeArg: Optional[str] = request.args.get("pageSize", type=str)

    if pageNumberArg is None or pageSizeArg is None:
        raise Exception("Cannot paginate request without pagination parameters")

    pageNumber = int(pageNumberArg)
    pageSize = int(pageSizeArg)

    if pageSize < 1:
        return Pagination(
            items=[], pageCount=1, pageNumber=pageNumber, pageSize=pageSize
        )

    if pageNumber < 1:
        skip = 0
    else:
        skip = (pageNumber - 1) * pageSize

    pageCount = len(ids) // pageSize
    if (len(ids) % pageSize) != 0:
        pageCount += 1

    return Pagination(
        items=ids[skip : skip + pageSize],
        pageCount=pageCount,
        pageNumber=pageNumber,
        pageSize=pageSize,
    )
