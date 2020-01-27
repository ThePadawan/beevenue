from flask import jsonify, Blueprint, current_app, request


from .spindex import SPINDEX
from .init import full_load

from ..decorators import requires_permission
from .. import permissions

bp = Blueprint('spindex', __name__)


@bp.route('/spindex/status')
@requires_permission(permissions.is_owner)
def status():
    output = []
    for m in SPINDEX.all():
        output.append({
            "id": m.id,
            "rating": m.rating,
            "hash": m.hash,
            "tag_names": list(m.tag_names)
        })

    return jsonify(output), 200


@bp.route('/spindex/reindex', methods=["POST"])
@requires_permission(permissions.is_owner)
def reindex():
    full_load(request.beevenue_context.session())
    return jsonify(f"Full load finished. Loaded {len(SPINDEX.all())} entries."), 200
