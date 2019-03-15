import re

from sqlalchemy.sql import func
from sqlalchemy.orm import load_only

from ....models import Medium, Tag, MediaTags, TagAlias

from .terms import get_search_terms


def _tags_per_category(session, search_terms):
    category_names = set([t.category for t in search_terms.category])

    tags_per_category = {}

    for category_name in category_names:
        tags_in_this_category = \
            session.query(Tag)\
            .filter(Tag.tag.like(f'{category_name}:%'))\
            .all()

        tags_implying_this_category = set()
        for t in tags_in_this_category:
            tags_implying_this_category |= set(t.implying_this)

        tags_per_category[category_name] = (tags_in_this_category, tags_implying_this_category)

    return tags_per_category


def _having_expr(category_term):
    if category_term.operator in (':', '='):
        return func.count(MediaTags.c.tag_id) == category_term.number
    if category_term.operator == '<':
        return func.count(MediaTags.c.tag_id) < category_term.number
    if category_term.operator == '>':
        return func.count(MediaTags.c.tag_id) > category_term.number
    if category_term.operator == '<=':
        return func.count(MediaTags.c.tag_id) <= category_term.number
    if category_term.operator == '>=':
        return func.count(MediaTags.c.tag_id) >= category_term.number
    if category_term.operator == '!=':
        return func.count(MediaTags.c.tag_id) != category_term.number
    raise Exception(f"Unknown operator in {category_term}")


def _having(category_term, value):
    if category_term.operator in (':', '='):
        return value == category_term.number
    if category_term.operator == '<':
        return value < category_term.number
    if category_term.operator == '>':
        return value > category_term.number
    if category_term.operator == '<=':
        return value <= category_term.number
    if category_term.operator == '>=':
        return value >= category_term.number
    if category_term.operator == '!=':
        return value != category_term.number
    raise Exception(f"Unknown operator in {category_term}")


# Pass "is_and"=True to AND together conditions.
# Otherwise, they will be ORed together.
def _find_media_ids(session, all_media, terms, is_and):

    # User supplied no search terms: show nothing
    if not terms:
        return []

    term_strings = set([t.term for t in terms])

    term_tags = session.query(Tag).filter(Tag.tag.in_(term_strings)).all()

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

    for medium in all_media:
        medium_tag_names = set([t.tag for t in medium.tags])

        target_strings = term_strings | implying_tag_strings

        intersection = medium_tag_names.intersection(target_strings)

        if is_and and len(intersection) == len(term_strings):
            results.append(medium.id)
        if not is_and and intersection:
            results.append(medium.id)

    return results


def _term_contains_zero(term):
    if term.operator in (':', '=', '>='):
        return term.number == 0
    if term.operator in ('<'):
        return term.number > 0
    if term.operator in ('<='):
        return term.number >= 0
    if term.operator in ('>'):
        return False
    if term.operator in ('!='):
        return term.number != 0


# Pass tag_ids_per_category != None to search for "ctags>2",
# or None for "tags>2" etc.
def _find_helper(session, all_media, terms):
    all_media_ids = [m.id for m in all_media]

    found = set()
    for term in terms:
        filters = []

        q = session\
            .query(MediaTags.c.medium_id)\
            .select_from(MediaTags)\
            .group_by(MediaTags.c.medium_id)

        if filters:
            q = q.filter(*filters)

        # If term contains zero, load values for >= 1 and
        # do ALL MINUS that result.
        found_for_this_term = set()

        if _term_contains_zero(term):
            geq_1_term = term.with_(operator='>=', number=1)

            results_for_geq_1 = q.having(_having_expr(geq_1_term)).all()
            results_for_geq_1 = [t[0] for t in results_for_geq_1]

            results_for_eq_0 = set(all_media_ids) - set(results_for_geq_1)
            found_for_this_term |= results_for_eq_0

        results = q.having(_having_expr(term)).all()
        results = [t[0] for t in results]
        found_for_this_term |= set(results)

        if found:
            found &= found_for_this_term
        else:
            found = found_for_this_term

    return found


def _replace_aliases(session, search_terms):
    possible_alias_terms = set()
    possible_alias_terms |= set([t.term for t in search_terms.positive])
    possible_alias_terms |= set([t.term for t in search_terms.negative])

    if not possible_alias_terms:
        # Nothing to do
        return search_terms

    found_aliases = session.query(TagAlias)\
        .filter(TagAlias.alias.in_(possible_alias_terms))\
        .all()

    replacements = {}

    for found_alias in found_aliases:
        replacements[found_alias.alias] = found_alias.tag.tag

    for old, new in replacements.items():
        for target in [search_terms.positive, search_terms.negative]:
            for term in target:
                if term.term == old:
                    term.term = new

    return search_terms


def _get_indirect_hits(category_string, indirect_hits):
    FOO_RE = re.compile(category_string + r':(.*)')

    indirect_hit_set = set()
    for indirect_hit in indirect_hits:
        for implied_tag in indirect_hit.implied_by_this:
            match = FOO_RE.match(implied_tag.tag)
            if match:
                indirect_hit_set.add(match.group(0))

    return indirect_hit_set


def _find_by_category(session, all_media, search_terms):
    tags_per_category = _tags_per_category(session, search_terms)

    results = set()

    for category_term in search_terms.category:
        category_string = category_term.category
        tags_in_this_category = tags_per_category.get(category_string, None)
        if not tags_in_this_category:
            continue

        for medium in all_media:
            direct_tags = tags_in_this_category[0]
            indirect_tags = tags_in_this_category[1]
            these_tags = set(medium.tags)

            direct_hits = these_tags.intersection(direct_tags)
            indirect_hits = these_tags.intersection(indirect_tags)

            indirect_hit_set = _get_indirect_hits(category_string, indirect_hits)
            direct_hit_strings = set([t.tag for t in direct_hits])

            hit_count = len(direct_hit_strings | indirect_hit_set)

            is_hit = _having(category_term, hit_count)
            if is_hit:
                results.add(medium)

    return set([m.id for m in results])


def _evaluate(context, search_terms):
    session = context.session()
    all_media = session.query(Medium).all()

    search_terms = _replace_aliases(session, search_terms)

    found_by_counting = _find_helper(session, all_media, search_terms.counting)

    found_by_category = _find_by_category(
        session,
        all_media,
        search_terms)

    pos_medium_ids = _find_media_ids(
        session, all_media, search_terms.positive, is_and=True)
    neg_medium_ids = _find_media_ids(
        session, all_media, search_terms.negative, is_and=False)

    to_exclude = set(neg_medium_ids)

    found_by_rating = set()
    if search_terms.rating:
        rating_term = search_terms.rating[0]
        ids = session.query(Medium.id).select_from(Medium)\
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
            found = set(session.query(MediaTags.c.medium_id).all())
            found = set([f[0] for f in found])
        else:
            found = set()
    else:
        found = non_empty_result_sets[0]
        for other_set in non_empty_result_sets[1:]:
            found &= other_set

    found -= to_exclude

    return found


def run_search(context, search_term_list):
    search_terms = get_search_terms(search_term_list)

    medium_ids = _evaluate(context, search_terms)

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
