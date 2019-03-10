from flask import jsonify, Blueprint, current_app, request

import json
import random

from .rules.json import RuleEncoder

bp = Blueprint('strawberry', __name__)


def _jsonified(rule_breaks):
    json_helper = {}
    for medium_id, broken_rules in rule_breaks.items():
        json_helper[medium_id] = list([r.pprint() for r in broken_rules])

    return jsonify(json_helper)


def _rules():
    return current_app.config['RULES']


@bp.route('/tags/missing/rules')
def get_rules():
    return json.dumps(_rules(), cls=RuleEncoder), 200


# TODO: Setup logging for testing
# TODO Switch from bare blueprint to application factory to inject json encoder
@bp.route('/tags/missing/<int:post_id>', methods=["GET", "OPTION"])
def get_missing_tags_for_post(post_id):
    session = request.beevenue_context.session()
    broken_rules = set()

    for rule in _rules():
        medium_ids = rule.iff.get_medium_ids(session)

        if post_id not in medium_ids:
            continue

        medium_ids = [post_id]

        for then in rule.thens:
            valid_medium_ids = then.get_medium_ids(
                session,
                medium_ids)

            if post_id not in valid_medium_ids:
                broken_rules.add(rule)

    return _jsonified({post_id: broken_rules})


@bp.route('/tags/missing/all', methods=["GET", "OPTION"])
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
