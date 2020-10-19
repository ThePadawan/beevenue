from typing import List, Set, TypeVar

from flask import g

from beevenue.flask import BeevenueContext, request

from ...types import MediumDocument

from .pagination import Pagination
from .parse import parse_search_terms
from .base import SearchTerm
from .simple import Negative, RatingSearchTerm


def find_all() -> Pagination[MediumDocument]:
    return _run(set())


def run(search_term_list: List[str]) -> Pagination[MediumDocument]:
    search_terms = parse_search_terms(search_term_list)

    if not search_terms:
        return Pagination.empty()

    return _run(search_terms)


def _run(search_terms: Set[SearchTerm]) -> Pagination[MediumDocument]:
    context = request.beevenue_context
    medium_ids = _search(context, search_terms)

    if not medium_ids:
        return Pagination.empty()

    sorted_medium_ids = list(medium_ids)
    sorted_medium_ids.sort(reverse=True)
    pagination = _paginate(sorted_medium_ids)
    media = g.spindex.get_media(pagination.items)

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

    all_media = g.spindex.all()
    result = set()

    for medium in all_media:
        for search_term in search_terms:
            if not search_term.applies_to(medium):
                break
        else:
            result.add(medium.medium_id)

    return result


TItem = TypeVar("TItem")


def _paginate(ids: List[TItem]) -> Pagination[TItem]:
    page_number_arg: str = request.args.get(  # type: ignore
        "pageNumber", type=str
    )
    page_size_arg: str = request.args.get("pageSize", type=str)  # type: ignore

    page_number = int(page_number_arg)
    page_size = int(page_size_arg)

    if page_number < 1:
        page_number = 1

    if page_size < 1:
        return Pagination(
            items=[], page_count=1, page_number=page_number, page_size=page_size
        )

    skip = (page_number - 1) * page_size

    page_count = len(ids) // page_size
    if (len(ids) % page_size) != 0:
        page_count += 1

    return Pagination(
        items=ids[skip : skip + page_size],
        page_count=page_count,
        page_number=page_number,
        page_size=page_size,
    )
