from flask import jsonify, Blueprint, request

from .. import permissions

from .spindex import SPINDEX
from .init import full_load


bp = Blueprint("spindex", __name__)


@bp.route("/spindex/status")
@permissions.is_owner
def status():
    output = []
    for m in SPINDEX.all():
        output.append({"id": m.id, "rating": m.rating, "hash": m.hash})

    return jsonify(output), 200


@bp.route("/spindex/reindex", methods=["POST"])
@permissions.is_owner
def reindex():
    full_load()
    return f"Full load finished. Loaded {len(SPINDEX.all())} entries.", 200
