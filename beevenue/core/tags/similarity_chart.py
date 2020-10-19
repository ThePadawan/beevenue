from typing import Dict, Set, TypedDict
from collections import defaultdict

from flask import g

from ...models import MediaTags, Tag
from . import tag_name_selector
from .censorship import Censorship

GroupedMediaIds = Dict[int, Set[int]]
Similarity = TypedDict("Similarity", {"similarity": float, "relevance": int})
SimilarityRow = Dict[str, Similarity]
Similarities = Dict[str, SimilarityRow]


def _get_similarities(
    censoring: Censorship, grouped_media_ids: GroupedMediaIds
) -> Similarities:
    similarities: Similarities = {}
    for tag1_id, media1_ids in grouped_media_ids.items():
        similarity_row: SimilarityRow = {}

        for tag2_id, media2_ids in grouped_media_ids.items():
            if tag1_id == tag2_id:
                continue

            intersection_size = len(media1_ids & media2_ids)

            if intersection_size == 0:
                continue

            union_size = len(media1_ids | media2_ids)
            similarity = float(intersection_size) / float(union_size)

            similarity_row[censoring.get_name(tag2_id)] = {
                "similarity": similarity,
                "relevance": union_size,
            }

        similarities[censoring.get_name(tag1_id)] = similarity_row

    return similarities


SimilarityNode = TypedDict("SimilarityNode", {"size": int})
SimilarityNodes = Dict[str, SimilarityNode]
SimilarityMatrix = TypedDict(
    "SimilarityMatrix", {"nodes": SimilarityNodes, "links": Similarities}
)


def get_similarity_matrix() -> SimilarityMatrix:
    session = g.db

    all_tags = session.query(Tag).all()
    tag_dict = {t.id: t for t in all_tags}

    media_tags = session.query(MediaTags).all()
    grouped_media_ids = defaultdict(set)

    for mediatag in media_tags:
        grouped_media_ids[mediatag.tag_id].add(mediatag.medium_id)

    censoring = Censorship(tag_dict, tag_name_selector)

    nodes: SimilarityNodes = {
        censoring.get_name(k): {"size": len(v)}
        for k, v in grouped_media_ids.items()
    }

    similarities = _get_similarities(censoring, grouped_media_ids)

    return {"nodes": nodes, "links": similarities}
