from typing import Tuple

from flask import g

from ..signals import (
    alias_added,
    alias_removed,
    implication_added,
    implication_removed,
    medium_added,
    medium_deleted,
    medium_updated,
    tag_renamed,
)


def _reindex_medium(medium_id: int) -> None:
    g.spindex.reindex_medium(medium_id)


def _rename_tag(names: Tuple[str, str]) -> None:
    old_name, new_name = names
    g.spindex.rename_tag(old_name, new_name)


def _unindex_medium(medium_id: int) -> None:
    g.spindex.remove_medium(medium_id)


def _add_alias(msg: Tuple[str, str]) -> None:
    tag_name, new_alias = msg
    g.spindex.add_alias(tag_name, new_alias)


def _remove_alias(msg: str) -> None:
    former_alias = msg
    g.spindex.remove_alias(former_alias)


def _add_implication(msg: Tuple[str, str]) -> None:
    implying, implied = msg
    g.spindex.add_implication(implying, implied)


def _remove_implication(msg: Tuple[str, str]) -> None:
    implying, implied = msg
    g.spindex.remove_implication(implying, implied)


def setup_signals() -> None:
    """Register signal handlers."""

    medium_updated.connect(_reindex_medium)
    medium_added.connect(_reindex_medium)
    medium_deleted.connect(_unindex_medium)

    tag_renamed.connect(_rename_tag)

    alias_added.connect(_add_alias)
    alias_removed.connect(_remove_alias)

    implication_added.connect(_add_implication)
    implication_removed.connect(_remove_implication)
