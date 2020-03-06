from flask import jsonify

from .viewmodels import (
    medium_schema,
    tag_show_schema,
    pagination_schema,
    tag_statistics_schema,
)
from .spindex.load import SpindexedMedium
from .core.model.search import Pagination
from .core.model.tags.statistics import TagStatistics
from .models import Tag


SCHEMAS = {
    SpindexedMedium: medium_schema,
    Tag: tag_show_schema,
    Pagination: pagination_schema,
    TagStatistics: tag_statistics_schema,
}


def try_convert_model(model):
    schema = SCHEMAS.get(type(model), None)
    if not schema:
        return model
    return jsonify(schema.dump(model))


def decorate_response(res, model):
    if isinstance(model, SpindexedMedium):
        res.push_file(model)
        res.push_thumbs(model.similar)
    if isinstance(model, Pagination) and model.items:
        res.push_thumbs(model.items[:20])
