from pathlib import Path

from flask_login import current_user
from flask_principal import identity_loaded, Permission

from .spindex.spindex import SPINDEX
from .decorators import requires
from . import notifications


class CanSeeMediumWithRatingNeed(object):
    def __init__(self, rating):
        self.rating = rating

    def __eq__(self, other):
        return self.rating == other.rating

    def __hash__(self):
        return hash((self.rating,))

    def __repr__(self):
        return f"<CanSeeMediumWithRatingNeed rating='{self.rating}'>"


_can_see_e = CanSeeMediumWithRatingNeed('e')
_can_see_u = CanSeeMediumWithRatingNeed('u')
_can_see_q = CanSeeMediumWithRatingNeed('q')
_can_see_s = CanSeeMediumWithRatingNeed('s')

_can_see_all = frozenset([_can_see_e, _can_see_q, _can_see_s, _can_see_u])


class AdminRoleNeed(object):
    pass


_admin_role_need = AdminRoleNeed()


@identity_loaded.connect
def on_identity_loaded(sender, identity):
    if hasattr(current_user, 'role'):
        identity.role = current_user.role
        if current_user.role == 'admin':
            identity.provides.add(_admin_role_need)
            identity.provides |= _can_see_all
        else:
            identity.provides |= set([_can_see_s, _can_see_q])


_allowed = Permission()


def _can_see_spindex_medium(m):
    if not m:
        return _allowed

    return Permission(CanSeeMediumWithRatingNeed(m.rating))


def _can_see_medium(medium_id):
    return _can_see_spindex_medium(SPINDEX.get_medium(medium_id))


def _can_see_full_path(full_path):
    hash = str(Path(full_path).with_suffix(''))
    all_media = SPINDEX.all()

    matching = [m for m in all_media if m.hash == hash]
    if matching:
        m = matching[0]
    else:
        m = None

    return _can_see_spindex_medium(m)


def _can_see_file(**kwargs):
    if "medium_id" in kwargs:
        return _can_see_spindex_medium(SPINDEX.get_medium(kwargs["medium_id"]))
    if "full_path" in kwargs:
        return _can_see_full_path(kwargs["full_path"])


def _requires_permission(permission):
    def validator(*args, **kwargs):
        p = permission
        if callable(p):
            p = p(*args, **kwargs)

        if not p.can():
            return notifications.no_permission(), 403
    return requires(validator)


get_medium = _requires_permission(_can_see_medium)
get_thumb = _requires_permission(_can_see_file)
get_medium_file = _requires_permission(_can_see_file)

is_owner = _requires_permission(Permission(_admin_role_need))
