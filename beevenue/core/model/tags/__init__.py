from collections import defaultdict
from itertools import groupby
import re
from typing import (
    Dict,
    Iterable,
    List,
    NewType,
    Optional,
    Set,
    Tuple,
    TypedDict,
    Union,
)

from sqlalchemy.orm.scoping import scoped_session

from .... import db
from ....models import MediaTags, Medium, Tag, TagAlias, TagImplication
from ....spindex.signals import medium_updated, tag_renamed
from .censorship import Censorship

VALID_TAG_REGEX_INNER = "(?P<category>[a-z]+:)?([a-zA-Z0-9.]+)"
VALID_TAG_REGEX = re.compile(f"^{VALID_TAG_REGEX_INNER}$")


def _tag_name_selector(t: Tag) -> str:
    name: str = t.tag
    return name


def get(name: str) -> Optional[Tag]:
    session = db.session()
    all_tags: List[Tag] = session.query(Tag).filter_by(tag=name).all()
    if len(all_tags) != 1:
        return None

    return all_tags[0]


ImplicationNodes = Dict[str, object]
ImplicationLinks = Dict[str, List[str]]
Implications = TypedDict(
    "Implications", {"nodes": ImplicationNodes, "links": ImplicationLinks}
)


def get_all_implications() -> Implications:
    session = db.session()
    all_rows = session.query(TagImplication).all()

    if not all_rows:
        return {"nodes": {}, "links": {}}

    all_tag_ids = set()
    for row in all_rows:
        all_tag_ids.add(row.implying_tag_id)
        all_tag_ids.add(row.implied_tag_id)

    tag_names = session.query(Tag).filter(Tag.id.in_(all_tag_ids)).all()
    tag_dict = {t.id: t for t in tag_names}

    censoring = Censorship(tag_dict, _tag_name_selector)

    def grouper(implication: TagImplication) -> int:
        id: int = implication.implying_tag_id
        return id

    links: ImplicationLinks = {}
    for left_id, rows in groupby(all_rows, grouper):
        left = censoring.get_name(left_id)
        right = [censoring.get_name(r.implied_tag_id) for r in rows]
        links[left] = right

    nodes: ImplicationNodes = {}
    for id in all_tag_ids:
        nodes[censoring.get_name(id)] = {}

    return {"nodes": nodes, "links": links}


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
    session = db.session()

    all_tags = session.query(Tag).all()
    tag_dict = {t.id: t for t in all_tags}

    media_tags = session.query(MediaTags).all()
    grouped_media_ids = defaultdict(set)

    for mt in media_tags:
        grouped_media_ids[mt.tag_id].add(mt.medium_id)

    censoring = Censorship(tag_dict, _tag_name_selector)

    nodes: SimilarityNodes = {
        censoring.get_name(k): {"size": len(v)}
        for k, v in grouped_media_ids.items()
    }

    similarities = _get_similarities(censoring, grouped_media_ids)

    return {"nodes": nodes, "links": similarities}


ValidTagName = NewType("ValidTagName", str)


def validate(tag_names: Iterable[str]) -> List[ValidTagName]:
    """
    Filters input iterable such that it only contains valid tag names.
    """
    return [
        ValidTagName(n.strip()) for n in tag_names if VALID_TAG_REGEX.match(n)
    ]


def _load(
    trimmed_tag_names: List[ValidTagName], medium_ids: Set[int]
) -> Optional[Tuple[scoped_session, Set[Tag], Set[Medium]]]:
    # User submitted no non-empty tag names
    if not trimmed_tag_names:
        return None

    if not medium_ids:
        return None

    session = db.session()
    all_tags = Tag.query.filter(Tag.tag.in_(trimmed_tag_names)).all()

    # User submitted only tags that don't exist yet.
    # Note: add_batch does not autocreate tags.
    if not all_tags:
        return None

    # load media by ids
    all_media = Medium.query.filter(Medium.id.in_(medium_ids)).all()

    # User submitted only ids for nonexistant media
    if not all_media:
        return None

    return session, all_tags, all_media


def _add_all(
    trimmed_tag_names: Iterable[ValidTagName],
    session: scoped_session,
    tags: Set[Tag],
    media: Set[Medium],
) -> int:
    tags_by_name = {t.tag: t for t in tags}

    added_count = 0
    for tag_name in trimmed_tag_names:
        if tag_name not in tags_by_name:
            # User might have entered a valid, but non-existant tag
            continue

        tag = tags_by_name[tag_name]
        for medium in media:
            if tag not in medium.tags:
                medium.tags.append(tag)
                added_count += 1

    session.commit()

    for medium in media:
        medium_updated.send(medium.id)

    return added_count


def add_batch(
    tag_names: Iterable[str], medium_ids: Set[int]
) -> Optional[Tuple[int, int]]:
    trimmed_tag_names = validate(tag_names)
    loaded = _load(trimmed_tag_names, medium_ids)

    if not loaded:
        return None

    added_count = _add_all(trimmed_tag_names, *loaded)
    return len(trimmed_tag_names), added_count


def create(name: ValidTagName) -> Tuple[bool, Optional[Tag]]:
    """
    Returns tuple of (needs_to_be_inserted, matching_tag)
    """
    session = db.session()

    # Don't create tag if there is another tag that has the same 'name'
    maybe_conflict = session.query(Tag).filter_by(tag=name).first()
    if maybe_conflict:
        return False, None

    # Don't create tag if there is another tag that has 'name' as an alias
    maybe_conflict = session.query(TagAlias).filter_by(alias=name).first()
    if maybe_conflict:
        return False, maybe_conflict.tag

    return True, Tag.create(name)


def delete_orphans() -> None:
    session = db.session()

    tags_to_delete = (
        session.query(Tag)
        .outerjoin(MediaTags)
        .filter(MediaTags.c.tag_id.is_(None))
        .all()
    )

    def is_deletable(tag: Tag) -> bool:
        return len(tag.implying_this) == 0 and len(tag.aliases) == 0

    tags_to_delete = [t for t in tags_to_delete if is_deletable(t)]

    for t in tags_to_delete:
        session.delete(t)

    if tags_to_delete:
        session.commit()


def _rename(
    session: scoped_session, old_tag: Tag, new_name: str
) -> Tuple[str, bool]:
    if not new_name:
        return "You must specify a new name", False

    old_name = old_tag.tag

    new_tags = session.query(Tag).filter(Tag.tag == new_name).all()

    if len(new_tags) < 1:
        # New tag doesn't exist yet. We can simply rename "old_tag".
        old_tag.tag = new_name
        tag_renamed.send(
            (
                old_name,
                new_name,
            )
        )
        return "Successfully renamed tag", True

    new_tag = new_tags[0]

    # if new_tag does exist, UPDATE all medium tags
    # to reference new_tag instead of old_tag, then remove old_tag
    MediaTags.update().where(MediaTags.c.tag_id == old_tag.id).values(
        tag_id=new_tag.id
    )

    session.delete(old_tag)

    tag_renamed.send(
        (
            old_name,
            new_name,
        )
    )
    return "Successfully renamed tag", True


def update(tag_name: str, new_model: dict) -> Tuple[bool, Union[str, Tag]]:
    session = db.session()
    tag = session.query(Tag).filter(Tag.tag == tag_name).first()

    if not tag:
        return False, "Could not find tag with that name"

    if "tag" in new_model:
        msg, success = _rename(session, tag, new_model["tag"])
        if not success:
            return False, msg

    if "rating" in new_model:
        rating = new_model["rating"]
        if rating not in ("s", "q", "e"):
            return False, "Please specify a valid rating"

        tag.rating = rating

    session.commit()
    return True, tag
