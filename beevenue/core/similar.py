from queue import PriorityQueue
from typing import List, Set

from flask import g

from beevenue.flask import BeevenueContext

from ..types import MediumDocument


def _find_candidates(
    context: BeevenueContext, medium_id: int, target_tag_names: Set[str]
) -> Set[MediumDocument]:
    """Find all media that have *some* similarity to the specified one."""

    candidates = set()

    # Maybe add a reverse index (tag => media) so this query is faster
    for medium in g.spindex.all():
        if medium.medium_id == medium_id:
            continue

        if context.is_sfw and medium.rating != "s":
            continue

        if context.user_role != "admin" and medium.rating == "e":
            continue

        if len(medium.tag_names.innate & target_tag_names) == 0:
            continue

        candidates.add(medium)

    return candidates


def _get_similarity(
    context: BeevenueContext, medium: MediumDocument
) -> PriorityQueue:
    target_tag_names = medium.tag_names.innate
    candidates = _find_candidates(context, medium.medium_id, target_tag_names)

    # Keep up to 6 similar items in memory. We eject the least similar
    # once we have more than 5.
    jaccard_indices: PriorityQueue = PriorityQueue(maxsize=5 + 1)

    for candidate in candidates:
        candidate_tags = candidate.tag_names.innate
        intersection_size = len(candidate_tags & target_tag_names)
        union_size = len(candidate_tags | target_tag_names)

        similarity = float(intersection_size) / float(union_size)

        jaccard_indices.put_nowait(
            (
                similarity,
                candidate.medium_id,
            )
        )

        if jaccard_indices.full():
            jaccard_indices.get_nowait()

    return jaccard_indices


def similar_media(
    context: BeevenueContext, medium: MediumDocument
) -> List[MediumDocument]:
    jaccard_indices = _get_similarity(context, medium)

    similar_media_ids = []
    for _ in range(0, 5):
        if jaccard_indices.empty():
            break
        indices = jaccard_indices.get_nowait()
        similar_media_ids.append(indices[1])

    # Since we kept Jaccard indices sorted ascendingly, we have to reverse them
    # here so that media_ids are sorted descendingly (most similar first)
    similar_media_ids.reverse()

    media: List[MediumDocument] = g.spindex.get_media(similar_media_ids)
    return media
