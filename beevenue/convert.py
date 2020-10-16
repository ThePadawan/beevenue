from typing import Any

from flask import jsonify

from .core.model.detail import MediumDetail
from .core.model.search.pagination import Pagination
from .core.model.tags.tag_summary import TagSummary
from .models import Tag
from .response import BeevenueResponse
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
    schema = SCHEMAS.get(type(model), None)
    if not schema:
        return model
    return jsonify(schema.dump(model))


def decorate_response(res: BeevenueResponse, model: Any) -> None:
    if isinstance(model, MediumDetail):
        res.push_file(model)
        res.push_thumbs(model.similar)
    elif isinstance(model, Pagination) and model.items:
        res.push_thumbs(model.items[:20])
