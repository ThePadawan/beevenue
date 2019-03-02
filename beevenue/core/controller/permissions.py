from pathlib import Path

from flask_login import current_user
from flask_principal import identity_loaded, Permission, RoleNeed

from ...beevenue import app
from ...models import Medium


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


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    if hasattr(current_user, 'role'):
        identity.role = current_user.role
        if current_user.role == 'admin':
            identity.provides.add(_admin_role_need)
            identity.provides |= _can_see_all
        else:
            identity.provides |= set([_can_see_s, _can_see_q])


_allowed = Permission()

def _can_see_medium_by_filter(filter):
    maybe_medium = Medium.query.filter(filter).first()
    if not maybe_medium:
        return _allowed

    return Permission(CanSeeMediumWithRatingNeed(maybe_medium.rating))

def _can_see_medium(medium_id):
    return _can_see_medium_by_filter(Medium.id == medium_id)

def _can_see_file(full_path):
    hash = str(Path(full_path).with_suffix(''))
    return _can_see_medium_by_filter(Medium.hash == hash)

get_medium = _can_see_medium
get_thumb = _can_see_file
get_medium_file = _can_see_file

upload_medium = Permission(_admin_role_need)
delete_medium = Permission(_admin_role_need)
update_medium = Permission(_admin_role_need)
upload_medium = Permission(_admin_role_need)

create_thumbnail = Permission(_admin_role_need)

get_tag_stats = Permission(_admin_role_need)
delete_orphan_tags = Permission(_admin_role_need)