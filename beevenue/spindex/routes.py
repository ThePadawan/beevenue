from flask import Blueprint, g, jsonify

from .. import permissions
from .init import full_load

bp = Blueprint("spindex", __name__)


@bp.route("/spindex/status")
@permissions.is_owner
def status():  # type: ignore
    output = []
    for medium in g.spindex.all():
        output.append(
            {
                "id": medium.medium_id,
                "rating": medium.rating,
                "hash": medium.medium_hash,
            }
        )

    return jsonify(output), 200


@bp.route("/spindex/reindex", methods=["POST"])
@permissions.is_owner
def reindex():  # type: ignore
    full_load()
    return f"Full load finished. Loaded {len(g.spindex.all())} entries.", 200
