from itertools import groupby

from ...spindex.spindex import SPINDEX
from ...models import MediaTags, Medium


def similar_media(context, medium_id):
    session = context.session()

    medium = Medium.query.filter(Medium.id == medium_id).first()
    if not medium:
        return []

    target_tag_entities = medium.tags
    target_ids = set([t.id for t in target_tag_entities])

    filters = []
    if context.is_sfw:
        filters.append(Medium.rating == 's')
    if context.user_role != 'admin':
        filters.append(Medium.rating != 'e')

    all_media_tags = session.query(MediaTags, Medium.rating)\
        .join(Medium, Medium.id == MediaTags.c.medium_id)\
        .filter(MediaTags.c.tag_id.in_(target_ids), *filters)\
        .all()

    lookup = groupby(all_media_tags, lambda mt: mt.medium_id)

    jaccard_indices = []

    for medium_id, media_tags in lookup:
        if medium_id == medium.id:
            continue

        tags = [mt for mt in media_tags]
        rating = tags[0].rating
        tag_id_set = frozenset([mt.tag_id for mt in tags])
        intersection_size = len(tag_id_set & target_ids)
        union_size = len(tag_id_set | target_ids)
        jaccard_indices.append(
            {'medium_id': medium_id,
             'rating': rating,
             'value': float(intersection_size) / float(union_size)})

    jaccard_indices.sort(key=lambda j: j['value'], reverse=True)

    similar_media_ids = [j["medium_id"] for j in jaccard_indices[:5]]

    return SPINDEX.get_media(similar_media_ids)
