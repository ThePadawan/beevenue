from typing import Any

from flask import jsonify

from .core.model.detail import MediumDetail
from .core.model.search.pagination import Pagination
from .core.model.tags.tag_summary import TagSummary
from .models import Tag
from .viewmodels import (
    medium_detail_schema,
    pagination_schema,
    tag_show_schema,
    tag_summary_schema,
)

SCHEMAS = {
    MediumDetail: medium_detail_schema,
    Tag: tag_show_schema,
    Pagination: pagination_schema,
    TagSummary: tag_summary_schema,
}


def try_convert_model(model: Any) -> Any:
    """Use custom schemas to serialize models (or the default on fallback).

    This allows us to simply return models from our flask endpoints and
    convert them to JSON in this one central location, instead of in every
    endpoint separately."""

    schema = SCHEMAS.get(type(model), None)
    if not schema:
        return model
    return jsonify(schema.dump(model))


def decorate_response(res: Any, model: Any) -> None:
    """Set headers on the response based on the returned model.

    We use this to add preload headers for related files to that
    specified in the model Thanks to HTTP/2, this makes navigation much faster.
    """

    if isinstance(model, MediumDetail):
        res.push_medium(model)
        res.push_thumbs(model.similar)
    elif isinstance(model, Pagination) and model.items:
        res.push_thumbs(model.items[:20])
