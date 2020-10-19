from pathlib import Path
from typing import Any, Optional, Tuple

from flask import g
from flask_login import current_user
from flask_principal import identity_loaded, Permission

from . import notifications
from .decorators import RequirementDecorator, requires
from .types import MediumDocument


class _CanSeeMediumWithRatingNeed:
    """Permission need to see things with a specific rating."""

    def __init__(self, rating: str):
        self.rating = rating

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.rating == other.rating
        return False

    def __hash__(self) -> int:
        return hash((self.rating,))

    def __repr__(self) -> str:
        return f"<_CanSeeMediumWithRatingNeed rating='{self.rating}'>"


_can_see_e = _CanSeeMediumWithRatingNeed("e")
_can_see_u = _CanSeeMediumWithRatingNeed("u")
_can_see_q = _CanSeeMediumWithRatingNeed("q")
_can_see_s = _CanSeeMediumWithRatingNeed("s")

_can_see_all = frozenset([_can_see_e, _can_see_q, _can_see_s, _can_see_u])


class AdminRoleNeed:
    """Sentinel singleton for permission that only admins have."""


_admin_role_need = AdminRoleNeed()


@identity_loaded.connect
def on_identity_loaded(_: Any, identity: Any) -> None:
    if hasattr(current_user, "role"):
        identity.role = current_user.role
        if current_user.role == "admin":
            identity.provides.add(_admin_role_need)
            identity.provides |= _can_see_all
        else:
            identity.provides |= set([_can_see_s, _can_see_q])


_allowed = Permission()


def _can_see_spindex_medium(
    maybe_medium: Optional[MediumDocument],
) -> Permission:
    """Get Permission to see the specified medium."""

    if not maybe_medium:
        return _allowed

    return Permission(_CanSeeMediumWithRatingNeed(maybe_medium.rating))


def _can_see_medium(medium_id: int) -> Permission:
    return _can_see_spindex_medium(g.spindex.get_medium(medium_id))


def _can_see_full_path(full_path: str) -> Permission:
    medium_hash = str(Path(full_path).with_suffix(""))
    all_media = g.spindex.all()

    matching = [m for m in all_media if m.medium_hash == medium_hash]

    maybe_medium: Optional[MediumDocument] = None
    if matching:
        maybe_medium = matching[0]

    return _can_see_spindex_medium(maybe_medium)


def _requires_permission(permission: Permission) -> RequirementDecorator:
    def validator(*args: Any, **kwargs: Any) -> Optional[Tuple[Any, int]]:
        if callable(permission):
            actual_permission = permission(*args, **kwargs)
        else:
            actual_permission = permission

        if not actual_permission.can():
            return notifications.no_permission(), 403
        return None

    return requires(validator)


get_medium = _requires_permission(_can_see_medium)
get_medium_file = _requires_permission(_can_see_full_path)

is_owner = _requires_permission(Permission(_admin_role_need))
