from queue import PriorityQueue
from ...spindex.spindex import SPINDEX


def _find_candidates(context, medium_id, target_tag_names):
    """
    Find all media that have *some* similarity to the medium
    with Id `medium_id`.
    """
    candidates = set()

    # Maybe add a reverse index (tag => media) so this query is faster
    for m in SPINDEX.all():
        if m.id == medium_id:
            continue

        if context.is_sfw and m.rating != "s":
            continue

        if context.user_role != "admin" and m.rating == "e":
            continue

        if len(m.tag_names.innate & target_tag_names) == 0:
            continue

        candidates.add(m)

    return candidates


def _get_similarity(context, medium):
    target_tag_names = medium.tag_names.innate
    candidates = _find_candidates(context, medium.id, target_tag_names)

    # Keep up to 6 similar items in memory. We eject the least similar
    # once we have more than 5.
    jaccard_indices = PriorityQueue(maxsize=5 + 1)

    for candidate in candidates:
        candidate_tags = candidate.tag_names.innate
        intersection_size = len(candidate_tags & target_tag_names)
        union_size = len(candidate_tags | target_tag_names)

        similarity = float(intersection_size) / float(union_size)

        jaccard_indices.put_nowait((similarity, candidate.id,))

        if jaccard_indices.full():
            jaccard_indices.get_nowait()

    return jaccard_indices


def similar_media(context, medium):
    jaccard_indices = _get_similarity(context, medium)

    similar_media_ids = []
    for _ in range(0, 5):
        if jaccard_indices.empty():
            break
        t = jaccard_indices.get_nowait()
        similar_media_ids.append(t[1])

    # Since we kept Jaccard indices sorted ascendingly, we have to reverse them
    # here so that media_ids are sorted descendingly (most similar first)
    similar_media_ids.reverse()

    return SPINDEX.get_media(similar_media_ids)
