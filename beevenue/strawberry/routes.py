from flask import jsonify, Blueprint, current_app, request
from flask.json import dumps

import random

from ..spindex.spindex import SPINDEX
from ..decorators import requires_permission
from .. import permissions
from .rules.json import decode_rules, decode_rules_obj

bp = Blueprint('strawberry', __name__)


def _persist(rules_obj):
    res = dumps(rules_obj, indent=4, separators=(',', ': '))
    rules_file_path = current_app.config["BEEVENUE_RULES_FILE"]
    with open(rules_file_path, 'w') as rules_file:
        rules_file.write(res)


def _jsonified(rule_breaks):
    json_helper = {}
    for medium_id, broken_rules in rule_breaks.items():
        json_helper[medium_id] = list([r.pprint() for r in broken_rules])

    return jsonify(json_helper)


def _rules():
    rules_file_path = current_app.config["BEEVENUE_RULES_FILE"]
    with open(rules_file_path, 'r') as rules_file:
        rules_file_json = rules_file.read()

    rules_file_json = rules_file_json or '[]'

    return decode_rules(rules_file_json)


@bp.route('/rules')
@requires_permission(permissions.is_owner)
def get_rules():
    return jsonify(_rules()), 200


@bp.route('/rules/rules.json')
@requires_permission(permissions.is_owner)
def get_rules_as_json():
    return jsonify(_rules()), 200


@bp.route('/rules/<int:rule_index>', methods=["DELETE"])
@requires_permission(permissions.is_owner)
def remove_rule(rule_index):
    current_rules = _rules()
    if rule_index < 0 or rule_index > (len(current_rules) - 1):
        return '', 400

    del current_rules[rule_index]
    _persist(current_rules)
    return '', 200


@bp.route('/rules', methods=["POST"])
@requires_permission(permissions.is_owner)
def upload_rules():
    try:
        maybe_rules = decode_rules_obj(request.json)
    except Exception:
        return '', 400

    _persist(maybe_rules)
    return '', 200


@bp.route('/rules/validation', methods=["POST"])
@requires_permission(permissions.is_owner)
def validate_rules():
    try:
        maybe_rules = decode_rules_obj(request.json)
        return jsonify({'ok': True, 'data': len(maybe_rules)}), 200
    except Exception as e:
        return jsonify({'ok': False, 'data': str(e)}), 200


def _violating_medium_ids(rule):
    medium_ids = rule.iff.get_medium_ids()
    if not medium_ids:
        return []

    invalid_medium_ids = set()

    for then in rule.thens:
        valid_medium_ids = then.get_medium_ids(
            medium_ids)
        invalid_medium_ids |= set(medium_ids) - set(valid_medium_ids)

    return invalid_medium_ids


def _get_rule_violations():
    for rule in _rules():
        for violating_medium_id in _violating_medium_ids(rule):
            yield (violating_medium_id, rule)


@bp.route('/tags/missing/<int:medium_id>', methods=["GET", "OPTION"])
@requires_permission(permissions.get_medium)
def get_missing_tags_for_post(medium_id):
    broken_rules = [r for r in _rules() if r.is_violated_by(medium_id)]
    return _jsonified({medium_id: broken_rules})


@bp.route('/tags/missing/any', methods=["GET", "OPTION"])
@requires_permission(permissions.is_owner)
def get_missing_tags_any():
    violations = list(_get_rule_violations())

    # Ensure that tag violations are ordered somewhat randomly,
    # but also that all SFW media get reviewed before all others.
    random.shuffle(violations)

    all_media = SPINDEX.all()

    violation_medium_ids = frozenset(v[0] for v in violations)
    media = [m for m in all_media if m.id in violation_medium_ids]

    rating_by_id = {m.id: m.rating for m in media}

    def sorter(violation):
        if rating_by_id[violation[0]] == 's':
            return 1
        else:
            return 2

    violations.sort(key=sorter)

    for medium_id, rule in violations:
        return _jsonified({medium_id: [rule]})

    return _jsonified({})
