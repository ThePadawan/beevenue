from pathlib import Path
from typing import Any, Optional, Tuple

from flask_login import current_user
from flask_principal import identity_loaded, Permission

from . import notifications
from .decorators import RequirementDecorator, requires
from .spindex.models import SpindexedMedium
from .spindex.spindex import SPINDEX


class CanSeeMediumWithRatingNeed(object):
    def __init__(self, rating: str):
        self.rating = rating

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.rating == other.rating
        return False

    def __hash__(self) -> int:
        return hash((self.rating,))

    def __repr__(self) -> str:
        return f"<CanSeeMediumWithRatingNeed rating='{self.rating}'>"


_can_see_e = CanSeeMediumWithRatingNeed("e")
_can_see_u = CanSeeMediumWithRatingNeed("u")
_can_see_q = CanSeeMediumWithRatingNeed("q")
_can_see_s = CanSeeMediumWithRatingNeed("s")

_can_see_all = frozenset([_can_see_e, _can_see_q, _can_see_s, _can_see_u])


class AdminRoleNeed(object):
    pass


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


def _can_see_spindex_medium(m: Optional[SpindexedMedium]) -> Permission:
    if not m:
        return _allowed

    return Permission(CanSeeMediumWithRatingNeed(m.rating))


def _can_see_medium(medium_id: int) -> Permission:
    return _can_see_spindex_medium(SPINDEX.get_medium(medium_id))


def _can_see_full_path(full_path: str) -> Permission:
    hash = str(Path(full_path).with_suffix(""))
    all_media = SPINDEX.all()

    m: Optional[SpindexedMedium] = None

    matching = [m for m in all_media if m.hash == hash]
    if matching:
        m = matching[0]

    return _can_see_spindex_medium(m)


def _requires_permission(permission: Permission) -> RequirementDecorator:
    def validator(*args: Any, **kwargs: Any) -> Optional[Tuple[Any, int]]:
        if callable(permission):
            p = permission(*args, **kwargs)
        else:
            p = permission

        if not p.can():
            return notifications.no_permission(), 403
        return None

    return requires(validator)


get_medium = _requires_permission(_can_see_medium)
get_medium_file = _requires_permission(_can_see_full_path)

is_owner = _requires_permission(Permission(_admin_role_need))
