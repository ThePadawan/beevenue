from flask import request

from .signals import (
    medium_deleted,
    medium_added,
    medium_updated,
    tag_renamed,
    alias_added,
    alias_removed,
    implication_added,
    implication_removed,
)

from .spindex import SPINDEX


def _reindex_medium(id):
    SPINDEX.reindex_medium(request.beevenue_context.session(), id)


def _rename_tag(names):
    old_name, new_name = names
    SPINDEX.rename_tag(old_name, new_name)


def _unindex_medium(id):
    SPINDEX.remove_medium(id)


def _add_alias(msg):
    tag_name, new_alias = msg
    SPINDEX.add_alias(tag_name, new_alias)


def _remove_alias(msg):
    tag_name, former_alias = msg
    SPINDEX.remove_alias(tag_name, former_alias)


def _add_implication(msg):
    implying, implied = msg
    SPINDEX.add_implication(implying, implied)


def _remove_implication(msg):
    implying, implied = msg
    SPINDEX.remove_implication(implying, implied)


def setup_signals():
    medium_updated.connect(_reindex_medium)
    medium_added.connect(_reindex_medium)
    medium_deleted.connect(_unindex_medium)

    tag_renamed.connect(_rename_tag)

    alias_added.connect(_add_alias)
    alias_removed.connect(_remove_alias)

    implication_added.connect(_add_implication)
    implication_removed.connect(_remove_implication)
