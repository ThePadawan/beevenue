from flask import jsonify, Blueprint, current_app, request
from flask.json import dumps

import random

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


@bp.route('/tags/missing/<int:medium_id>', methods=["GET", "OPTION"])
@requires_permission(permissions.get_medium)
def get_missing_tags_for_post(medium_id):
    session = request.beevenue_context.session()
    broken_rules = set()

    for rule in _rules():
        medium_ids = rule.iff.get_medium_ids(session)

        if medium_id not in medium_ids:
            continue

        medium_ids = [medium_id]

        for then in rule.thens:
            valid_medium_ids = then.get_medium_ids(
                session,
                medium_ids)

            if medium_id not in valid_medium_ids:
                broken_rules.add(rule)

    return _jsonified({medium_id: broken_rules})


@bp.route('/tags/missing/all', methods=["GET", "OPTION"])
@requires_permission(permissions.is_owner)
def get_missing_tags():
    session = request.beevenue_context.session()
    rule_breaks = {}

    for rule in _rules():
        medium_ids = rule.iff.get_medium_ids(session)

        for then in rule.thens:
            valid_medium_ids = then.get_medium_ids(
                session,
                medium_ids)
            invalid_medium_ids = set(medium_ids) - set(valid_medium_ids)

            for invalid_medium_id in invalid_medium_ids:
                if invalid_medium_id not in rule_breaks:
                    rule_breaks[invalid_medium_id] = set()
                rule_breaks[invalid_medium_id].add(rule)

    return _jsonified(rule_breaks)


@bp.route('/tags/missing/any', methods=["GET", "OPTION"])
@requires_permission(permissions.is_owner)
def get_missing_tags_any():
    session = request.beevenue_context.session()
    rule_breaks = {}

    for rule in _rules():
        medium_ids = rule.iff.get_medium_ids(session)

        random.shuffle(medium_ids)

        for then in rule.thens:
            valid_medium_ids = then.get_medium_ids(
                session,
                medium_ids)
            invalid_medium_ids = set(medium_ids) - set(valid_medium_ids)

            for invalid_medium_id in invalid_medium_ids:
                if invalid_medium_id not in rule_breaks:
                    rule_breaks[invalid_medium_id] = set()
                rule_breaks[invalid_medium_id].add(rule)
                return _jsonified(rule_breaks)

    return _jsonified(rule_breaks)
